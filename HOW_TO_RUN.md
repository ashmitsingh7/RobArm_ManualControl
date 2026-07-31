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

Pick **one** firmware pair, matching whichever control path you're using —
don't mix an encoder board with the USB launch file or vice versa.

| Board | Bluetooth build | USB build |
|---|---|---|
| ESP-A (gripper/wrist) | `esp32/espA_motors_encoders.cpp` | `esp32/espA_motors_usb.cpp` |
| ESP-B (elbow/shoulder) | `esp32/espB_motors_encoders.cpp` | `esp32/espB_motors_usb.cpp` |

Flash with Arduino IDE (ESP32 board package) or PlatformIO. The USB build
needs no extra libraries; the Bluetooth build needs `BluetoothSerial` and
`ArduinoJson`.

## 3. Build the workspace

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

This pulls in `pyserial` automatically (declared in `ros_bt`'s
`setup.py`/`package.xml`) — no separate install step needed for the USB
path.

## 4. Run — Bluetooth path

1. Turn on Bluetooth on the machine you're launching from.
2. Pair/trust both ESP32s if you haven't already (MACs are set in
   `src/arm_bringup/scripts/bind_bt.sh`).
3. Terminal 1:
   ```bash
   source install/setup.bash
   ros2 launch arm_bringup arm.launch.py
   ```
   This runs `bind_bt.sh` to bring up both `rfcomm` links, then starts the
   encoder nodes, the two Bluetooth motor writers, and `control_node_v2`.
4. Terminal 2:
   ```bash
   source install/setup.bash
   ros2 run test_pubsub keyboard_teleop
   ```
5. Type keys + Enter into the teleop terminal to drive the arm (see keymap
   in `README.md`). `p` triggers real homing on this path.

**Verify:** check the launch terminal's log for both `rfcomm` links reporting
connected, and each node starting without errors.

## 5. Run — USB path

1. Plug both ESP32s into the launching machine over USB.
2. Check which port each one landed on:
   ```bash
   ls /dev/ttyUSB*
   # or: dmesg | tail -20   (right after plugging each one in, one at a
   # time, to see which device node just appeared)
   ```
   If they show up as `/dev/ttyACM0`/`/dev/ttyACM1` instead, or in a
   different order than expected, edit the `port` parameters in
   `src/arm_bringup/launch/arm_usb.launch.py` (defaults: ESP-A →
   `/dev/ttyUSB0`, ESP-B → `/dev/ttyUSB1`, both at 115200 baud).
3. Terminal 1:
   ```bash
   source install/setup.bash
   ros2 launch arm_bringup arm_usb.launch.py
   ```
4. Terminal 2:
   ```bash
   source install/setup.bash
   ros2 run test_pubsub keyboard_teleop
   ```
5. Drive it the same way. `p` (home) is a safe no-op on this path — the USB
   firmware has no homing state machine.

**Watch for:** USB serial ports on Linux can silently swap — `ttyUSB0`
becomes `ttyUSB1` on reconnect if the boards are plugged in a different
order next time. If a key moves the wrong joint or nothing happens, that's
the first thing to check; `dmesg | tail` shows which device node just
appeared.

## 6. If using a GCS controller instead of the keyboard

Skip `keyboard_teleop` — just make sure the controller code on the GCS
publishes keystrokes as `std_msgs/String` on `/user_input`, matching what
`control_node_v2` expects. Everything downstream (either launch file) works
the same regardless of what's publishing to `/user_input`.

## Troubleshooting

- **`colcon build` fails on missing message types** — make sure `custom_msg`
  built first (it defines `Joints`/`MotorControl`, which `controls` and
  `ros_bt` both import); a plain `colcon build` from the workspace root
  handles ordering automatically.
- **`Ctrl+C` throws `AttributeError` on `control_node_v2`** — you're running
  an unpatched copy; this repo's version has that fix already (see
  `README.md`).
- **Bluetooth launch never gets past `bind_bt`** — check
  `/tmp/rfcomm_0.log` and `/tmp/rfcomm_1.log` (written by `bind_bt.sh`) for
  the raw `rfcomm connect` output, and confirm both boards are paired/
  trusted and powered on.
