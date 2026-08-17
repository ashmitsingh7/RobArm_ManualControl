# How to run

## Requirements

- Ubuntu 22.04
- ROS2 Humble
- `pyserial` (only needed for the USB path — see step 2)

## 1. Get the workspace onto your ROS2 machine

Copy the whole `src/` and `esp32/` folders from this repo anywhere, e.g.:

```bash
mkdir -p ~/ros2_ws
cp -r src ~/ros2_ws/
cd ~/ros2_ws
```

## 2. Flash the ESP32s

Flash the USB firmware pair:

| Board | USB build |
|---|---|---|
| ESP-A (gripper/wrist) | `esp32/espA_motors_usb.cpp` |
| ESP-B (elbow/shoulder) | `esp32/espB_motors_usb.cpp` |

Flash with Arduino IDE (ESP32 board package) or PlatformIO. The USB build
needs no extra libraries.

## 3. Build the workspace

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

This pulls in `pyserial` automatically (declared in `ros_bt`'s
`setup.py`/`package.xml`) — no separate install step needed.

## 4. Run the pipeline

1. Plug both ESP32s into the machine over USB.
2. Check which ports they landed on:
   ```bash
   ls /dev/ttyUSB*
   # or: dmesg | tail -20
   ```
   If they show up as `/dev/ttyACM0` and `/dev/ttyACM1`, or in the wrong
   order, pass explicit launch overrides to the wrapper script.
3. Start the stack:
   ```bash
   ./robarm27.sh
   ```
   If you are in a desktop session, this also opens the browser UI at
   `http://localhost:8080` after a short delay.
   Optional port override:
   ```bash
   ./robarm27.sh port_a:=/dev/ttyACM0 port_b:=/dev/ttyACM1
   ```
4. Open the browser UI:
   ```text
   http://localhost:8080
   ```
5. Click buttons or use the keyboard shortcuts shown in the page.

The browser sends keys to `web_ui/web_server.py`, which publishes `/user_input`.
`control_node_v2` turns those keys into `/motor_commands`, and the USB motor
writers send the packets to the ESP32s.

If you want terminal keyboard input instead, run:

```bash
source install/setup.bash
ros2 run test_pubsub keyboard_teleop
```

That node publishes to the same `/user_input` topic as the browser UI.

## Troubleshooting

- **`colcon build` fails on missing message types** — make sure `custom_msg`
  is present; a plain `colcon build` from the workspace root handles ordering
  automatically.
- **`Ctrl+C` throws `AttributeError` on `control_node_v2`** — you're running
  an unpatched copy; this repo's version has that fix already (see
  `README.md`).
