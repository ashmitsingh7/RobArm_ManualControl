import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import json


class BTReaderESP_A(Node):
    def __init__(self):
        super().__init__('bt_reader_espA')

        self.pub = self.create_publisher(
            Float32MultiArray, 'esp1_angles', 10
        )

        try:
            self.bt = open('/dev/rfcomm0', 'rb', buffering=0)
            self.get_logger().info("ESP-A connected via /dev/rfcomm0")
        except Exception as e:
            self.get_logger().error(f"Failed to open rfcomm0: {e}")
            raise

        self.buffer = ""
        self.create_timer(0.001, self.read_bt)

    def read_bt(self):
        try:
            data = self.bt.read(1024)
            if not data:
                return

            self.buffer += data.decode("utf-8", errors="ignore")

            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    angles = json.loads(line)

                    if isinstance(angles, list) and len(angles) == 3:
                        msg = Float32MultiArray()
                        msg.data = [float(x) for x in angles]
                        self.pub.publish(msg)
                        self.get_logger().debug(f"ESP-A angles: {angles}")
                    else:
                        self.get_logger().warn(f"ESP-A invalid data: {line}")

                except json.JSONDecodeError:
                    self.get_logger().warn(f"ESP-A bad JSON: {line}")

        except Exception as e:
            data = self.bt.read(1024)
            if not data:
                return
            self.get_logger().info(f"Reveived: {data}")
            self.get_logger().error(f"ESP-A RFCOMM error: {e}")


def main():
    rclpy.init()
    rclpy.spin(BTReaderESP_A())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
