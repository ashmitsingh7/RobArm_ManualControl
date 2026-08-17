# ARMstrong — Manual Control Stack

A ROS2 workspace for manually driving Vyadh's robotic arm from a browser UI,
keyboard, or GCS controller. This repo ships one live control path:
USB serial from the browser or keyboard, through ROS2, to the two ESP32 boards.

The active path is:

`browser UI / keyboard_teleop -> /user_input -> control_node_v2 -> /motor_commands -> USB motor writers -> ESP32s`

## Architecture

```
browser UI / keyboard_teleop  ──String──▶  control_node_v2  ──Joints──▶  USB motor writers  ──▶  ESP32s ──▶ motors
 (web_ui / test_pubsub)                       (controls)                 (ros_bt)
```

- **`custom_msg`** — defines the two message types everything else imports:
  `Joints` (one `MotorControl` per joint: gripper, wrist1, wrist2, elbow,
  shoulder1, shoulder2) and `MotorControl` (`direction: bool`, `pwm: uint8`).
- **`controls`** — `control_node_v2` subscribes to `/user_input` (raw
  keystrokes as `String`), maps keys to joint motions, and publishes a
  `Joints` message on `/motor_commands`.
- **`ros_bt`** — the package that talks to the ESP32s:
  - `ros_write_motors_espA_usb` / `ros_write_motors_espB_usb` — USB serial
    writers, same packet format, over `pyserial`.
- **`arm_bringup`** — launch files:
  - `robarm27.launch.py` — the ready-to-run pipeline. Starts the web UI
    server, `control_node_v2`, and both USB motor writer nodes.
- **`test_pubsub`** — `keyboard_teleop`, a standalone node you run in its own
  terminal to type keys onto `/user_input` in place of a real GCS
  controller.
- **`esp32/`** — firmware for both boards, one variant per control path:
  - `espA_motors_usb.cpp` / `espB_motors_usb.cpp` — USB build. Same pins,
    same `setMotor()`, same 3-byte packet format, and no encoder or homing
    logic.

ESP-A drives the gripper/wrist board; ESP-B drives the elbow/shoulder board.

## Keymap

| Key | Action | Key | Action |
|---|---|---|---|
| `r` / `f` | gripper open / close | `u` / `j` | shoulder pitch up / down |
| `t` / `g` | wrist pitch up / down | `i` / `k` | shoulder roll ACW / CW |
| `y` / `h` | wrist roll ACW / CW | `o` / `l` | elbow flex / extend |
| `x` | stop all motors | `p` | home key reserved, no-op in USB-only pipeline |

`p` is kept for keymap compatibility. In this USB-only pipeline the motor
writer nodes ignore it.

## Fixes applied in this repo (vs. the original clone)

1. **`control_node_v2.py` crashed on shutdown** — `main()`'s `finally` block
   called `node.kb_thread.join()`, an attribute that's never created on this
   class (leftover from an older threaded-input version), so `Ctrl+C` threw
   `AttributeError` instead of exiting cleanly. Those two lines are removed.

See `HOW_TO_RUN.md` for setup and day-to-day usage.
