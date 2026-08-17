# ROB ARM GUIDE

This workspace is a USB-only manual control stack for the robotic arm.

## One-Line Summary

The current live path is:

`browser UI -> /user_input -> control_node_v2 -> /motor_commands -> USB serial writers -> ESP32 firmware -> motors`

## Flow Chart

```text
┌───────────────┐
│  Browser UI   │
│ index.html    │
└──────┬────────┘
       │ WebSocket JSON {"key":"r"}
       v
┌────────────────────┐
│ web_server.py      │
│ publishes /user_input
└──────┬─────────────┘
       │ std_msgs/String
       v
┌────────────────────┐
│ control_node_v2.py │
│ key -> Joints      │
└──────┬─────────────┘
       │ custom_msg/Joints on /motor_commands
       v
┌──────────────────────────────┐
│ USB motor writers            │
│ ESP-A + ESP-B                │
└──────┬───────────────┬───────┘
       │               │
       │ serial bytes  │ serial bytes
       v               v
┌───────────────┐   ┌───────────────┐
│ ESP-A board   │   │ ESP-B board   │
│ gripper/wrist │   │ elbow/shoulder│
└──────┬────────┘   └──────┬────────┘
       │                   │
       └──────────┬────────┘
                  v
              ┌────────┐
              │ Motors │
              └────────┘
```

## Startup Flow

```text
┌────────────────────────────┐
│ ./robarm27.sh              │
└─────────────┬──────────────┘
              │
              v
┌────────────────────────────┐
│ source /opt/ros/humble     │
└─────────────┬──────────────┘
              │
              v
┌────────────────────────────┐
│ colcon build --symlink-install
└─────────────┬──────────────┘
              │
              v
┌────────────────────────────┐
│ source install/setup.bash   │
└─────────────┬──────────────┘
              │
              v
┌────────────────────────────┐
│ ros2 launch arm_bringup robarm27.launch.py │
└──────┬──────────┬──────────┘
       │          │
       │          ├──────────────▶ web_server starts on :8080
       │          │
       │          ├──────────────▶ control_node_v2 subscribes /user_input
       │          │
       │          ├──────────────▶ USB writers open ttyUSB/ttyACM ports
       │          │
       v          v
┌────────────────────────────┐
│ Browser auto-opens         │
│ http://localhost:8080      │
└────────────────────────────┘
```

## What Runs When You Start It

The one-command entry point is:

```bash
./robarm27.sh
```

That script does three things in order:

1. Builds the workspace with `colcon build --symlink-install`
2. Sources the workspace overlay from `install/setup.bash`
3. Launches `arm_bringup/robarm27.launch.py`

That launch file starts these ROS nodes:

- `web_ui.web_server`
- `controls.control_node_v2`
- `ros_bt.ros_write_motors_espA_usb`
- `ros_bt.ros_write_motors_espB_usb`

Default serial ports:

- ESP-A: `/dev/ttyUSB0`
- ESP-B: `/dev/ttyUSB1`

You can override them at launch:

```bash
./robarm27.sh port_a:=/dev/ttyACM0 port_b:=/dev/ttyACM1
```

## Full Data Flow

### 1. User input starts in the browser

The browser UI is served from:

- [`src/web_ui/static/index.html`](./src/web_ui/static/index.html)

The page contains buttons and keyboard shortcuts for the arm controls.

When you click a button or press a key:

- the browser sends a JSON message over WebSocket to `web_server`
- the JSON format is `{"key": "<character>"}`

### 2. `web_server` publishes `/user_input`

The web server node lives in:

- [`src/web_ui/web_ui/web_server.py`](./src/web_ui/web_ui/web_server.py)

Its job is:

- serve the HTML UI
- accept WebSocket messages on `/ws`
- extract the `key`
- publish that key as `std_msgs/String` on `/user_input`

So if the browser sends `{"key":"r"}`, the ROS message becomes:

```text
/user_input: "r"
```

## 3. `control_node_v2` translates key presses into joint commands

The control node is:

- [`src/controls/controls/control_node_v2.py`](./src/controls/controls/control_node_v2.py)

It subscribes to:

- `/user_input`

It publishes:

- `/motor_commands`

It maps keys like this:

- `r` / `f` -> gripper open / close
- `t` / `g` -> wrist pitch up / down
- `y` / `h` -> wrist roll ACW / CW
- `u` / `j` -> shoulder pitch up / down
- `i` / `k` -> shoulder roll ACW / CW
- `o` / `l` -> elbow flex / extend
- `x` -> stop all motors
- `p` -> home request, but in this USB-only pipeline it is ignored by the USB writers

The message it publishes is `custom_msg/Joints`, which contains six `MotorControl`
fields:

- `gripper`
- `wrist1`
- `wrist2`
- `elbow`
- `shoulder1`
- `shoulder2`

Each `MotorControl` has:

- `direction: bool`
- `pwm: uint8`

### 4. USB motor writer nodes split the command by board

The two motor writer nodes are:

- [`src/ros_bt/ros_bt/ros_write_motors_espA_usb.py`](./src/ros_bt/ros_bt/ros_write_motors_espA_usb.py)
- [`src/ros_bt/ros_bt/ros_write_motors_espB_usb.py`](./src/ros_bt/ros_bt/ros_write_motors_espB_usb.py)

Both subscribe to:

- `/motor_commands`

#### ESP-A writer

ESP-A handles:

- gripper
- wrist1
- wrist2

It sends three local motor IDs:

- `0` -> gripper
- `1` -> wrist1
- `2` -> wrist2

#### ESP-B writer

ESP-B handles:

- elbow
- shoulder1
- shoulder2

It sends three local motor IDs:

- `0` -> elbow
- `1` -> shoulder1
- `2` -> shoulder2

### 5. Each writer converts ROS messages to 3-byte serial packets

Each motor becomes a 3-byte packet:

```text
[local_id, direction, pwm]
```

Example:

- motor 1
- direction forward
- PWM 255

becomes:

```text
[1, 1, 255]
```

The writers send those bytes over USB serial:

- ESP-A -> `/dev/ttyUSB0` by default
- ESP-B -> `/dev/ttyUSB1` by default

### Packet-level view

The ROS message is higher level, but the wire format is fixed and simple.

For ESP-A:

- motor 0 = gripper
- motor 1 = wrist1
- motor 2 = wrist2

For ESP-B:

- motor 0 = elbow
- motor 1 = shoulder1
- motor 2 = shoulder2

Each motor contributes exactly 3 bytes:

```text
local_id, direction, pwm
```

So one full packet per board is always 9 bytes:

```text
3 motors x 3 bytes each = 9 bytes
```

Example for `r` on ESP-A:

- gripper open -> `[0, 1, 255]`
- wrist1 rest -> `[1, 0, 0]`
- wrist2 rest -> `[2, 0, 0]`

Final bytes sent to ESP-A:

```text
[0, 1, 255, 1, 0, 0, 2, 0, 0]
```

ESP-B receives the same command as all rest values:

```text
[0, 0, 0, 1, 0, 0, 2, 0, 0]
```

Example for `x` stop all:

- both writers send all-zero motor values
- both boards receive:

```text
[0, 0, 0, 1, 0, 0, 2, 0, 0]
```

Example for `p` home:

- `control_node_v2` publishes a home-style `Joints` message
- ESP-A USB writer sees the home pattern and ignores it with a warning
- ESP-B still receives all rest values

So on the USB pipeline, `p` does not move the arm.

### Trace: pressing `r`

1. You click the `Open` button in the browser or press `r`.
2. `index.html` sends `{"key":"r"}` over WebSocket.
3. `web_server.py` receives that JSON and publishes `/user_input = "r"`.
4. `control_node_v2.py` matches `r` to gripper open.
5. It builds a `Joints` message with:

```text
gripper  = active forward, pwm 255
wrist1   = rest
wrist2   = rest
elbow    = rest
shoulder1 = rest
shoulder2 = rest
```

6. It publishes that on `/motor_commands`.
7. ESP-A USB writer turns the gripper/wrist part into:

```text
[0, 1, 255, 1, 0, 0, 2, 0, 0]
```

8. ESP-B USB writer turns the elbow/shoulder part into:

```text
[0, 0, 0, 1, 0, 0, 2, 0, 0]
```

9. The ESP32 firmware receives the packets and drives the motors.

### Trace: pressing `x`

1. You press `x` in the browser or keyboard input node.
2. `index.html` sends `{"key":"x"}` to `web_server.py`.
3. `web_server.py` publishes `/user_input = "x"`.
4. `control_node_v2.py` recognizes the stop key and publishes a `Joints`
   message with every joint at rest.
5. ESP-A USB writer sends:

```text
[0, 0, 0, 1, 0, 0, 2, 0, 0]
```

6. ESP-B USB writer sends:

```text
[0, 0, 0, 1, 0, 0, 2, 0, 0]
```

7. The ESP32 firmware receives all-zero commands and stops the motors.

### Key To Bytes

`rest` means `direction = 0` and `pwm = 0`.

| Key | Action | `/user_input` | ESP-A packet | ESP-B packet |
|---|---|---|---|---|
| `r` | gripper open | `"r"` | `[0,1,255,1,0,0,2,0,0]` | `[0,0,0,1,0,0,2,0,0]` |
| `f` | gripper close | `"f"` | `[0,0,255,1,0,0,2,0,0]` | `[0,0,0,1,0,0,2,0,0]` |
| `t` | wrist pitch up | `"t"` | `[0,0,0,1,0,255,2,1,255]` | `[0,0,0,1,0,0,2,0,0]` |
| `g` | wrist pitch down | `"g"` | `[0,0,0,1,1,255,2,0,255]` | `[0,0,0,1,0,0,2,0,0]` |
| `y` | wrist roll ACW | `"y"` | `[0,0,0,1,1,255,2,1,255]` | `[0,0,0,1,0,0,2,0,0]` |
| `h` | wrist roll CW | `"h"` | `[0,0,0,1,0,255,2,0,255]` | `[0,0,0,1,0,0,2,0,0]` |
| `u` | shoulder pitch up | `"u"` | `[0,0,0,1,0,0,2,0,0]` | `[0,0,0,1,0,255,2,1,255]` |
| `j` | shoulder pitch down | `"j"` | `[0,0,0,1,0,0,2,0,0]` | `[0,0,0,1,1,255,2,0,255]` |
| `i` | shoulder roll ACW | `"i"` | `[0,0,0,1,0,0,2,0,0]` | `[0,0,0,1,1,255,2,1,255]` |
| `k` | shoulder roll CW | `"k"` | `[0,0,0,1,0,0,2,0,0]` | `[0,0,0,1,0,255,2,0,255]` |
| `o` | elbow flex | `"o"` | `[0,0,0,1,0,0,2,0,0]` | `[0,1,255,1,0,0,2,0,0]` |
| `l` | elbow extend | `"l"` | `[0,0,0,1,0,0,2,0,0]` | `[0,0,255,1,0,0,2,0,0]` |
| `x` | stop all | `"x"` | `[0,0,0,1,0,0,2,0,0]` | `[0,0,0,1,0,0,2,0,0]` |
| `p` | home reserved | `"p"` | ignored by USB writer | `[0,0,0,1,0,0,2,0,0]` |

### 6. The ESP32 firmware receives the packets and drives the motors

The launch file expects the USB firmware on the boards:

- ESP-A USB firmware
- ESP-B USB firmware

The firmware reads the 3-byte packets and applies the motor output on the board.

So the final chain is:

```text
browser button or key
  -> WebSocket message
  -> /user_input
  -> control_node_v2
  -> /motor_commands
  -> USB motor writer for ESP-A or ESP-B
  -> serial packet on ttyUSB/ttyACM
  -> ESP32 firmware
  -> motor output
```

## What Is Not In The Repo

This repository only contains the USB browser pipeline.

## Startup Checklist

1. Plug both ESP32 boards into the laptop over USB.
2. Confirm the serial port names with:

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

3. Run:

```bash
./robarm27.sh
```

4. Open the browser if it does not auto-open:

```text
http://localhost:8080
```

## Quick Troubleshooting Map

- If the UI opens but motors do not move, check that the correct serial ports
  were passed to `robarm27.sh`.
- If key presses do nothing, confirm `control_node_v2` is running and subscribed
  to `/user_input`.
- If the browser shows the page but ROS logs are quiet, check `web_server` for
  WebSocket connection errors.
- If a board moves the wrong joint, the port assignments for ESP-A and ESP-B are
  probably swapped.

## File Map

- [`robarm27.sh`](./robarm27.sh)
- [`src/arm_bringup/launch/robarm27.launch.py`](./src/arm_bringup/launch/robarm27.launch.py)
- [`src/web_ui/web_ui/web_server.py`](./src/web_ui/web_ui/web_server.py)
- [`src/web_ui/static/index.html`](./src/web_ui/static/index.html)
- [`src/controls/controls/control_node_v2.py`](./src/controls/controls/control_node_v2.py)
- [`src/ros_bt/ros_bt/ros_write_motors_espA_usb.py`](./src/ros_bt/ros_bt/ros_write_motors_espA_usb.py)
- [`src/ros_bt/ros_bt/ros_write_motors_espB_usb.py`](./src/ros_bt/ros_bt/ros_write_motors_espB_usb.py)
