import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray


class EncoderMerger(Node):
    def __init__(self):
        super().__init__('encoder_merger')

        self.espA = [0.0, 0.0, 0.0]       # ESP-A → 3 encoders
        self.espB = [0.0, 0.0, 0.0, 0.0]  # ESP-B → 4 encoders

        self.create_subscription(
            Float32MultiArray,
            'esp1_angles',
            self.espA_cb,
            10
        )

        self.create_subscription(
            Float32MultiArray,
            'esp2_angles',
            self.espB_cb,
            10
        )

        self.pub = self.create_publisher(
            Float32MultiArray,
            'encoder_angles',
            10
        )

        self.get_logger().info("Encoder merger running (3 + 4)")

    def espA_cb(self, msg):
        self.espA = list(msg.data)
        self.publish()

    def espB_cb(self, msg):
        self.espB = list(msg.data)
        self.publish()

    def publish(self):
        msg = Float32MultiArray()
        msg.data = self.espA + self.espB
        self.pub.publish(msg)
        self.get_logger().debug(f"Merged angles: {msg.data}")


def main():
    rclpy.init()
    rclpy.spin(EncoderMerger())
    rclpy.shutdown()


if __name__ == '__main__':
    main()
