# ARMstrong — Manual Control Stack

A ROS2 workspace for manually driving Vyadh's robotic arm from a keyboard or
GCS controller. It supports two interchangeable ways of talking to the two
ESP32 motor-driver boards:

- **Bluetooth (`rfcomm`)** — the original path, with encoder feedback.
- **USB serial** — a simpler alternate path with no Bluetooth pairing step
  and no encoder feedback, useful when you just want the arm to move without
  the BT link or homing/limit-switch hardware in the loop.

Nothing about the high-level architecture changes between the two — same
`Joints`/`MotorControl` messages, same `control_node_v2`, same
`keyboard_teleop`. Only the last hop (motor writer nodes + firmware) differs.

## Architecture

```
keyboard_teleop  ──String──▶  control_node_v2  ──Joints──▶  motor writer node(s)  ──▶  ESP32s ──▶ motors
 (test_pubsub)                   (controls)                      (ros_bt)
```

- **`custom_msg`** — defines the two message types everything else imports:
  `Joints` (one `MotorControl` per joint: gripper, wrist1, wrist2, elbow,
  shoulder1, shoulder2) and `MotorControl` (`direction: bool`, `pwm: uint8`).
- **`controls`** — `control_node_v2` subscribes to `/user_input` (raw
  keystrokes as `String`), maps keys to joint motions, and publishes a
  `Joints` message on `/motor_commands`.
- **`ros_bt`** — the packages that talk to the ESP32s:
  - `ros_write_motors_espA` / `ros_write_motors_espB` — Bluetooth writers,
    write raw 3-byte packets (`[local_id, direction, pwm]`) to
    `/dev/rfcomm0` / `/dev/rfcomm1`.
  - `ros_write_motors_espA_usb` / `ros_write_motors_espB_usb` — USB serial
    writers, same packet format, over `pyserial` instead of `rfcomm`.
  - `espA_read_enc` / `espB_read_enc` / `esp_read_enc_merger` — encoder
    feedback nodes. **Bluetooth path only** — the USB firmware doesn't
    expose encoders, so these aren't launched in the USB stack.
- **`arm_bringup`** — launch files:
  - `arm.launch.py` — Bluetooth stack. Runs `bind_bt.sh` to connect both
    `rfcomm` links first, then starts the encoder + BT motor-writer +
    control nodes once that succeeds.
  - `arm_usb.launch.py` — USB stack. No Bluetooth gate; just starts the two
    USB motor writers and `control_node_v2` directly.
- **`test_pubsub`** — `keyboard_teleop`, a standalone node you run in its own
  terminal to type keys onto `/user_input` in place of a real GCS
  controller.
- **`esp32/`** — firmware for both boards, one variant per control path:
  - `espA_motors_encoders.cpp` / `espB_motors_encoders.cpp` — Bluetooth
    build, includes encoder reporting and the wrist homing/limit-switch
    state machine.
  - `espA_motors_usb.cpp` / `espB_motors_usb.cpp` — USB build. Same pins,
    same `setMotor()`, same 3-byte packet format, but plain `Serial` at
    115200 baud instead of `BluetoothSerial`/`ArduinoJson`, and no encoder
    or homing logic (the homing state machine depends on limit switches
    that weren't verified on this build, so it's left out rather than
    shipping something half-tested).

ESP-A drives the gripper/wrist board; ESP-B drives the elbow/shoulder board.

## Keymap

| Key | Action | Key | Action |
|---|---|---|---|
| `r` / `f` | gripper open / close | `u` / `j` | shoulder pitch up / down |
| `t` / `g` | wrist pitch up / down | `i` / `k` | shoulder roll ACW / CW |
| `y` / `h` | wrist roll ACW / CW | `o` / `l` | elbow flex / extend |
| `x` | stop all motors | `p` | home (Bluetooth build only — see below) |

`p` (home) only does something on the Bluetooth path, where it sends a
sentinel byte the encoder-aware firmware interprets as a homing request. On
the USB path there's no homing state machine to receive it, so
`control_node_v2` still emits the request but the USB motor-writer nodes
catch it, log a warning, and no-op instead of writing garbage to the board.

## Fixes applied in this repo (vs. the original clone)

1. **`bind_bt.sh` path was hardcoded** to `~/Vyadh/temp_ws/...`, so
   `arm.launch.py` only worked from that exact machine/clone location.
   `bind_bt.sh` is now registered as an installed package resource (see
   `arm_bringup/setup.py`), and `arm.launch.py` looks it up at runtime via
   `ament_index_python`'s `get_package_share_directory()` — works from any
   workspace, on any machine.
2. **`control_node_v2.py` crashed on shutdown** — `main()`'s `finally` block
   called `node.kb_thread.join()`, an attribute that's never created on this
   class (leftover from an older threaded-input version), so `Ctrl+C` threw
   `AttributeError` instead of exiting cleanly. Those two lines are removed.

See `HOW_TO_RUN.md` for setup and day-to-day usage.
