#!/usr/bin/env bash
# Headless motion check for the R550 Gazebo model.
#
# It starts an isolated Gazebo/ROS instance, exercises forward, reverse and
# steering commands, and prints the resulting /odom positions.  The isolated
# domain/master lets it run next to an already-open Gazebo GUI.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(realpath "${SCRIPT_DIR}/..")"

export GAZEBO_MASTER_URI="${R550_TEST_GAZEBO_MASTER_URI:-http://127.0.0.1:21399}"
export ROS_DOMAIN_ID="${R550_TEST_ROS_DOMAIN_ID:-199}"

set +u
source /opt/ros/humble/setup.bash
source "${PROJECT_DIR}/install/setup.bash"
set -u

LOG_FILE="$(mktemp -t r550_motion_test.XXXXXX.log)"
LAUNCH_PID=""

cleanup() {
  if [[ -n "${LAUNCH_PID}" ]] && kill -0 "${LAUNCH_PID}" 2>/dev/null; then
    kill -- "-${LAUNCH_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_odom() {
  for _ in $(seq 1 60); do
    if ros2 topic list 2>/dev/null | grep -qx "/odom"; then
      return 0
    fi
    sleep 0.5
  done
  echo "ERROR: /odom did not appear; see ${LOG_FILE}" >&2
  return 1
}

show_position() {
  local label="$1"
  printf '%s: ' "${label}"
  timeout 3s ros2 topic echo /odom --once --field pose.pose.position |
    tr '\n' ' '
  printf '\n'
}

publish_for() {
  local seconds="$1"
  local twist="$2"
  timeout "${seconds}s" ros2 topic pub -r 20 /cmd_vel \
    geometry_msgs/msg/Twist "${twist}" >/dev/null 2>&1 || true
  sleep 1
}

echo "Starting isolated R550 simulation (ROS_DOMAIN_ID=${ROS_DOMAIN_ID}, ${GAZEBO_MASTER_URI})"
setsid ros2 launch simulation r550_sim.launch.py gui:=false >"${LOG_FILE}" 2>&1 &
LAUNCH_PID=$!

wait_for_odom
show_position "initial"

publish_for 5 "{linear: {x: 0.3}, angular: {z: 0.0}}"
show_position "after forward 5 s"

publish_for 5 "{linear: {x: -0.3}, angular: {z: 0.0}}"
show_position "after reverse 5 s"

publish_for 5 "{linear: {x: -0.4}, angular: {z: 0.0}}"
show_position "after fast reverse 5 s"

publish_for 5 "{linear: {x: 0.2}, angular: {z: 0.5}}"
show_position "after left turn 5 s"

echo "PASS: simulation is still alive after forward/reverse/turn."
