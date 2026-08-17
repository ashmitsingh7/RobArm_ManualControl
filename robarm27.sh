#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source /opt/ros/humble/setup.bash

cd "$SCRIPT_DIR"
colcon build --symlink-install
source install/setup.bash

if command -v xdg-open >/dev/null 2>&1; then
  (sleep 3; xdg-open "http://localhost:8080" >/dev/null 2>&1) &
fi

exec ros2 launch arm_bringup robarm27.launch.py "$@"
