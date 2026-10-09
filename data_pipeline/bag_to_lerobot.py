#!/usr/bin/env python3
"""Convert a ROS 2 bag into a LeRobot-style dataset manifest.

This script is intentionally kept as a thin, inspectable wrapper. It records the
bag metadata and expected topics, then delegates the heavy conversion to the
LeRobot/rosbags toolchain. Add a real LeRobot writer once the exact action space
and camera intrinsics for R550 are fixed.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

EXPECTED_TOPICS = {
    "/camera/color/image_raw",
    "/camera/depth/points",
    "/point_cloud_raw",
    "/sensing/imu/imu_data",
    "/odom",
    "/joy",
}


def bag_info(bag: Path) -> dict:
    proc = subprocess.run(
        ["ros2", "bag", "info", str(bag)],
        check=True,
        text=True,
        capture_output=True,
    )
    return {"stdout": proc.stdout, "stderr": proc.stderr}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--instruction", default="沿当前车道低速直行，遇到障碍物停车")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    info = bag_info(args.bag)

    missing = [
        topic
        for topic in EXPECTED_TOPICS
        if topic not in info["stdout"]
    ]
    manifest = {
        "bag": str(args.bag),
        "instruction": args.instruction,
        "expected_topics": sorted(EXPECTED_TOPICS),
        "missing_topics": missing,
        "ros2_bag_info": info["stdout"],
    }

    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)
    )
    print(f"manifest written to {args.out / 'manifest.json'}")
    if missing:
        raise SystemExit(f"missing topics: {missing}")


if __name__ == "__main__":
    main()
