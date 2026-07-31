import rclpy
from rclpy.node import Node
from custom_msg.msg import Joints
import serial


class MotorUSBTxEspB(Node):
    def __init__(self):
        super().__init__('motor_usb_tx_espB')

        # Change this if ESP-B enumerates as something else on your laptop.
        self.declare_parameter('port', '/dev/ttyUSB1')
        self.declare_parameter('baud', 115200)
        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value

        self.sub = self.create_subscription(
            Joints,
            'motor_commands',
            self.cb,
            10
        )

        # ESP-B → elbow + shoulders, now over plain USB serial instead of rfcomm
        self.ser = serial.Serial(port, baud, timeout=0)
        self.get_logger().info(f'Motor USB TX ESP-B started on {port} @ {baud}')

    def cb(self, msg: Joints):
        motors = [
            msg.elbow,      # local id 0
            msg.shoulder1,  # local id 1
            msg.shoulder2   # local id 2
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
            self.get_logger().debug(f"ESP-B sent: {list(packet)}")

    def destroy_node(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MotorUSBTxEspB()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
