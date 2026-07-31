import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.pub = self.create_publisher(String, '/user_input', 10)
        self.get_logger().info("Keyboard teleop ready. Type keys + ENTER")

    def run(self):
        while rclpy.ok():
            try:
                key = input(">> ").strip()
            except EOFError:
                break
            msg = String()
            msg.data = key
            self.pub.publish(msg)


def main():
    rclpy.init()
    node = KeyboardTeleop()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
