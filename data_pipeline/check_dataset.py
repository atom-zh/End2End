#!/usr/bin/env python3
"""Run basic quality checks on a converted R550 HDF5 dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path)
    args = parser.parse_args()

    manifest = args.dataset / "manifest.json"
    if not manifest.exists():
        raise SystemExit(f"manifest not found: {manifest}")
    data = json.loads(manifest.read_text())

    h5_path = Path(data["hdf5"])
    if not h5_path.exists():
        raise SystemExit(f"dataset not found: {h5_path}")

    with h5py.File(h5_path, "r") as h5:
        grp = h5["data"]
        timestamps = grp["timestamp"][:]
        actions = grp["action"][:]
        images = grp["observation/image"][:]

        assert np.all(np.diff(timestamps) > 0), "timestamps must be strictly increasing"
        assert np.all(np.isfinite(actions)), "actions contain non-finite values"
        assert np.all(np.isfinite(images)), "images contain non-finite values"

        speed = actions[:, 0]
        steer = actions[:, 1]
        print(f"frames: {len(timestamps)}")
        print(f"speed  min/max: {speed.min():.3f} / {speed.max():.3f}")
        print(f"steer  min/max: {steer.min():.3f} / {steer.max():.3f}")
        print(f"image  shape: {images.shape}")
        print("dataset checks passed")


if __name__ == "__main__":
    main()
