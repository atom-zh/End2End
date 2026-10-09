#!/usr/bin/env bash
set -euo pipefail

ROBOT_USER="${ROBOT_USER:-wheeltec}"
ROBOT_HOST="${ROBOT_HOST:-192.168.101.15}"

ssh "${ROBOT_USER}@${ROBOT_HOST}" bash -s <<'EOF'
set -euo pipefail
echo '== uname =='
uname -a
echo '== l4t =='
cat /etc/nv_tegra_release 2>/dev/null || true
echo '== network =='
ip -brief addr
echo '== usb =='
lsusb
echo '== wheeltec devices =='
ls -l /dev/wheeltec* 2>/dev/null || true
echo '== ros packages =='
source /opt/ros/humble/setup.bash 2>/dev/null || true
ros2 pkg list 2>/dev/null | grep -Ei 'autoware|wheeltec|lslidar|astra|lio_sam|turn_on|nav2' || true
EOF
