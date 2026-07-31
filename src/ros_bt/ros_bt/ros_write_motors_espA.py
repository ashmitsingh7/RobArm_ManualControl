import rclpy
from rclpy.node import Node
from custom_msg.msg import Joints


class MotorBTTxEspA(Node):
    def __init__(self):
        super().__init__('motor_bt_tx_espA')
        

        self.sub = self.create_subscription(
            Joints,
            'motor_commands',
            self.cb,
            10
        )

        # ESP-A → gripper + wrists
        self.bt = open('/dev/rfcomm0', 'wb', buffering=0)
        self.get_logger().info('Motor BT TX ESP-A started')

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
            self.bt.write(bytes([0xFF, 0x00, 0x00]))
            self.get_logger().warn("ESP-A HOME (0xFF) sent")
            return
    
        motors = [
            msg.gripper,   # local id 0
            msg.wrist1,    # local id 1
            msg.wrist2     # local id 2
        ]

        packet = bytearray()

        for local_id, motor in enumerate(motors):
            '''if motor.pwm <= 0:
                continue
            '''
            direction = 1 if motor.direction else 0
            pwm = int(motor.pwm)
            packet.append(local_id)
            packet.append(direction)
            packet.append(pwm)

        if packet:
            self.bt.write(packet)
            self.get_logger().debug(f"ESP-A sent: {list(packet)}")
        



def main(args=None):
    rclpy.init(args=args)
    node = MotorBTTxEspA()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
