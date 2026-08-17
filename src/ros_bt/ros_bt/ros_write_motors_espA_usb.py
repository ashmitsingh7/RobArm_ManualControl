import rclpy
from rclpy.node import Node
from custom_msg.msg import Joints
import serial


class MotorUSBTxEspA(Node):
    def __init__(self):
        super().__init__('motor_usb_tx_espA')

        # Change this if ESP-A enumerates as something else on your laptop.
        # Check with: ls /dev/ttyUSB* /dev/ttyACM*  (or `dmesg | tail` after plugging in)
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baud', 115200)
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value

        self.sub = self.create_subscription(
            Joints,
            'motor_commands',
            self.cb,
            10
        )

        # ESP-A → gripper + wrists over USB serial
        self.ser = serial.Serial(port, baud, timeout=0)
        self.get_logger().info(f'Motor USB TX ESP-A started on {port} @ {baud}')

    def cb(self, msg: Joints):

        if (
            msg.gripper.pwm == 0 and
            msg.wrist1.pwm == 0 and
            msg.wrist2.pwm == 0 and
            msg.elbow.pwm == 0 and
            msg.shoulder1.pwm == 0 and
            msg.shoulder2.pwm == 0 and
            msg.wrist1.direction is True
        ):
            # The USB firmware has no homing state machine (no limit
            # switches wired to this build). Rather than send the old 0xFF
            # sentinel to a firmware that doesn't know what to do with it,
            # just no-op and say so.
            self.get_logger().warn(
                "HOME key pressed — homing isn't wired up in the USB-only "
                "build, ignoring."
            )
            return

        motors = [
            msg.gripper,   # local id 0
            msg.wrist1,    # local id 1
            msg.wrist2     # local id 2
        ]

        packet = bytearray()

        for local_id, motor in enumerate(motors):
            direction = 1 if motor.direction else 0
            pwm = int(motor.pwm)
            packet.append(local_id)
            packet.append(direction)
            packet.append(pwm)

        if packet:
            self.ser.write(packet)
            self.get_logger().debug(f"ESP-A sent: {list(packet)}")

    def destroy_node(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MotorUSBTxEspA()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
