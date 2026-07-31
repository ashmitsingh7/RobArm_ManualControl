import rclpy
from rclpy.node import Node
from custom_msg.msg import Joints


class MotorBTTxEspB(Node):
    def __init__(self):
        super().__init__('motor_bt_tx_espB')

        self.sub = self.create_subscription(
            Joints,
            'motor_commands',
            self.cb,
            10
        )

        # ESP-B → elbow + shoulders
        self.bt = open('/dev/rfcomm1', 'wb', buffering=0)
        self.get_logger().info('Motor BT TX ESP-B started')

    def cb(self, msg: Joints):
        motors = [
            msg.elbow,     # local id 0
            msg.shoulder1,  # local id 1
            msg.shoulder2  # local id 2
        ]

        packet = bytearray()

        for local_id, motor in enumerate(motors):
            '''if motor.pwm <= 0:
                continue'''

            direction = 1 if motor.direction else 0
            pwm = int(motor.pwm)

            packet.append(local_id)
            packet.append(direction)
            packet.append(pwm)

        if packet:
            self.bt.write(packet)
            self.get_logger().debug(f"ESP-B sent: {list(packet)}")


def main(args=None):
    rclpy.init(args=args)
    node = MotorBTTxEspB()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
