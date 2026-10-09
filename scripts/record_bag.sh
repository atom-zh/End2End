#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-data/rosbags}"
PREFIX="${PREFIX:-r550_run}"
mkdir -p "$OUT_DIR"

ros2 bag record \
  /camera/color/image_raw \
  /camera/depth/points \
  /point_cloud_raw \
  /sensing/imu/imu_data \
  /odom \
  /joy \
  -o "$OUT_DIR/${PREFIX}_$(date +%Y%m%d_%H%M%S)"
