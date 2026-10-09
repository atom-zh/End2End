#!/usr/bin/env python3
"""Convert the project HDF5 dataset to a LeRobot dataset.

LeRobot APIs change between versions, so this adapter is intentionally isolated
from the ROS2 bag reader. Install LeRobot in the same virtualenv and run:

    source .venv/bin/activate
    pip install "lerobot[smolvla]"
    python data_pipeline/hdf5_to_lerobot.py --hdf5 data/demo_hdf5/dataset.h5 ...
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hdf5", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--repo-id", default="r550/demo")
    parser.add_argument("--robot-type", default="r550_ackermann")
    parser.add_argument("--fps", type=int, default=20)
    args = parser.parse_args()

    try:
        from lerobot.datasets import LeRobotDataset
    except Exception as exc:
        raise SystemExit(
            "LeRobot is not installed. Run: pip install 'lerobot[smolvla]'"
        ) from exc

    manifest = args.manifest or args.hdf5.parent / "manifest.json"
    meta = json.loads(manifest.read_text()) if manifest.exists() else {}
    instruction = meta.get("instruction", "沿当前车道低速直行，遇到障碍物停车")

    with h5py.File(args.hdf5, "r") as h5:
        grp = h5["data"]
        images = grp["observation/image"][:]
        states = grp["observation.state"][:]
        actions = grp["action"][:]

    height, width = images.shape[1], images.shape[2]
    features = {
        "observation.image": {
            "dtype": "video",
            "shape": [3, height, width],
            "names": ["channel", "height", "width"],
        },
        "observation.state": {
            "dtype": "float32",
            "shape": [states.shape[1]],
            "names": ["linear_x", "angular_z"],
        },
        "action": {
            "dtype": "float32",
            "shape": [actions.shape[1]],
            "names": ["linear_x", "angular_z"],
        },
    }

    dataset = LeRobotDataset.create(
        repo_id=args.repo_id,
        fps=args.fps,
        robot_type=args.robot_type,
        features=features,
    )

    for idx in range(len(images)):
        frame = {
            "observation.image": np.transpose(images[idx], (2, 0, 1)),
            "observation.state": states[idx],
            "action": actions[idx],
            "task": instruction,
        }
        dataset.add_frame(frame)

    dataset.save_episode()
    print(f"created LeRobot dataset: {args.repo_id}")


if __name__ == "__main__":
    main()
