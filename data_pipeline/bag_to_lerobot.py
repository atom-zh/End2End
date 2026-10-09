#!/usr/bin/env python3
"""Convert a ROS 2 bag into a stable intermediate HDF5 driving dataset.

The output is deliberately small and inspectable. Each row is one synchronized
frame:

    observation.image  -> front RGB image (uint8, HxWx3)
    observation.state  -> [linear_x, angular_z] from /odom
    action             -> [linear_x, angular_z] from /cmd_vel
    episode_index      -> episode id
    frame_index        -> frame id inside episode
    timestamp          -> action timestamp in nanoseconds

This HDF5 file is the project-native format. A LeRobot adapter can load it later
without re-reading the bag.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import cv2
import h5py
import numpy as np
from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore


def decode_image(msg) -> np.ndarray:
    encoding = str(getattr(msg, "encoding", "")).lower()
    data = bytes(getattr(msg, "data", b""))
    arr = np.frombuffer(data, dtype=np.uint8)
    height = int(getattr(msg, "height", 0))
    width = int(getattr(msg, "width", 0))
    channels = 1 if "mono" in encoding or "8uc1" in encoding else 3

    if height <= 0 or width <= 0:
        raise ValueError(f"invalid image dimensions {width}x{height}")

    if channels == 3:
        arr = arr.reshape(height, width, 3)
        if "bgr" in encoding or encoding == "8uc3":
            arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
    else:
        arr = arr.reshape(height, width)
        arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
    return arr


def collect_messages(bag_path: Path, topics: set[str]) -> dict[str, list]:
    buffers: dict[str, list] = defaultdict(list)
    typestore = get_typestore(Stores.ROS2_HUMBLE)

    with Reader(bag_path) as reader:
        for connection, timestamp, rawdata in reader.messages():
            if connection.topic not in topics:
                continue
            try:
                msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            except Exception:
                continue
            buffers[connection.topic].append((timestamp, msg))

    for topic in topics:
        buffers[topic].sort(key=lambda item: item[0])
    return buffers


def nearest_index(timestamps: list[int], target: int) -> int:
    return min(range(len(timestamps)), key=lambda i: abs(timestamps[i] - target))


def extract_twist(msg) -> tuple[float, float]:
    if hasattr(msg, "twist"):
        twist = msg.twist.twist
    else:
        twist = msg
    return float(twist.linear.x), float(twist.angular.z)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bag", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--instruction", default="沿当前车道低速直行，遇到障碍物停车")
    parser.add_argument("--max-dt-ms", type=float, default=50.0)
    args = parser.parse_args()

    topics = {
        "/camera/color/image_raw",
        "/cmd_vel",
        "/odom",
    }
    buffers = collect_messages(args.bag, topics)

    if not buffers["/cmd_vel"]:
        raise SystemExit("no /cmd_vel messages found in bag")
    if not buffers["/camera/color/image_raw"]:
        raise SystemExit("no /camera/color/image_raw messages found in bag")
    if not buffers["/odom"]:
        raise SystemExit("no /odom messages found in bag")

    action_ts = np.asarray([t for t, _ in buffers["/cmd_vel"]], dtype=np.int64)
    image_ts = np.asarray(
        [t for t, _ in buffers["/camera/color/image_raw"]], dtype=np.int64
    )
    odom_ts = np.asarray([t for t, _ in buffers["/odom"]], dtype=np.int64)
    max_dt = int(args.max_dt_ms * 1_000_000)

    rows = []
    for action_time, _ in buffers["/cmd_vel"]:
        i_img = nearest_index(image_ts.tolist(), action_time)
        i_odom = nearest_index(odom_ts.tolist(), action_time)
        if abs(int(image_ts[i_img]) - action_time) > max_dt:
            continue
        if abs(int(odom_ts[i_odom]) - action_time) > max_dt:
            continue
        rows.append((action_time, i_img, i_odom))

    if not rows:
        raise SystemExit("no synchronized frames after time alignment")

    first_image = decode_image(buffers["/camera/color/image_raw"][rows[0][1]][1])
    height, width = first_image.shape[:2]
    n_frames = len(rows)

    args.out.mkdir(parents=True, exist_ok=True)
    h5_path = args.out / "dataset.h5"

    with h5py.File(h5_path, "w") as h5:
        grp = h5.create_group("data")
        obs = grp.create_group("observation")
        obs.create_dataset("image", shape=(n_frames, height, width, 3), dtype=np.uint8)
        obs.create_dataset("state", shape=(n_frames, 2), dtype=np.float32)
        grp.create_dataset("action", shape=(n_frames, 2), dtype=np.float32)
        grp.create_dataset("episode_index", shape=(n_frames,), dtype=np.int64)
        grp.create_dataset("frame_index", shape=(n_frames,), dtype=np.int64)
        grp.create_dataset("timestamp", shape=(n_frames,), dtype=np.int64)

        for idx, (action_time, i_img, i_odom) in enumerate(rows):
            obs["image"][idx] = decode_image(
                buffers["/camera/color/image_raw"][i_img][1]
            )
            obs["state"][idx] = extract_twist(buffers["/odom"][i_odom][1])
            grp["action"][idx] = extract_twist(
                buffers["/cmd_vel"][nearest_index(action_ts.tolist(), action_time)][1]
            )
            grp["episode_index"][idx] = 0
            grp["frame_index"][idx] = idx
            grp["timestamp"][idx] = action_time

        meta = grp.create_group("meta")
        meta.attrs["instruction"] = args.instruction
        meta.attrs["fps_note"] = "action rate derived from /cmd_vel"

    manifest = {
        "bag": str(args.bag),
        "instruction": args.instruction,
        "frames": n_frames,
        "image_shape": [height, width, 3],
        "state_features": ["linear_x", "angular_z"],
        "action_features": ["linear_x", "angular_z"],
        "episodes": 1,
        "hdf5": str(h5_path),
    }
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)
    )
    print(f"wrote {h5_path} with {n_frames} frames")


if __name__ == "__main__":
    main()
