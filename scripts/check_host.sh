#!/usr/bin/env bash
set -euo pipefail

echo "== host check =="
uname -a
cat /etc/os-release | grep PRETTY_NAME || true
echo "ROS_DISTRO=${ROS_DISTRO:-not_sourced}"

if [ -x /opt/ros/humble/setup.bash ]; then
  source /opt/ros/humble/setup.bash
fi

for tool in ros2 colcon gazebo python3 git; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf 'ok   %-10s %s\n' "$tool" "$(command -v "$tool")"
  else
    printf 'MISS %-10s\n' "$tool"
  fi
done

echo "== resources =="
[ -d /media/home/share/R550 ] && echo "ok   R550 resource dir" || echo "MISS /media/home/share/R550"

echo "== network =="
ip -brief addr 2>/dev/null || true
