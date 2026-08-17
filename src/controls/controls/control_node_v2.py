import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from custom_msg.msg import MotorControl, Joints


class JointControlNode(Node):
    def __init__(self):
        super().__init__('joint_control_node_v2')
        self.get_logger().info('Joint Control Node v2 started')

        # ================= PUBLISHER TO MOTORS =================
        self.motor_pub = self.create_publisher(
            Joints, 'motor_commands', 10
        )

        # ================= INPUT SUB  =================

        self.input_sub = self.create_subscription(
            String, 'user_input', self.input_callback, 10
        )

        # ================= KEY MAPS =================
        self.GRIPPER_MAP = {
            'r': [('gripper', +1)],  # open
            'f': [('gripper', -1)],  # close
        }

        self.WRIST_MAP = {
            't': [('wrist1', -1), ('wrist2', +1)],  # pitch up
            'g': [('wrist1', +1), ('wrist2', -1)],  # pitch down
            'y': [('wrist1', +1), ('wrist2', +1)],  # roll ACW
            'h': [('wrist1', -1), ('wrist2', -1)],  # roll CW
        }

        self.SHOULDER_MAP = {
            'u': [('shoulder1', -1), ('shoulder2', +1)],  # pitch up
            'j': [('shoulder1', +1), ('shoulder2', -1)],  # pitch down
            'i': [('shoulder1', +1), ('shoulder2', +1)],  # roll ACW
            'k': [('shoulder1', -1), ('shoulder2', -1)],  # roll CW
        }

        self.ELBOW_MAP = {
            'o': [('elbow', +1)],  # flex
            'l': [('elbow', -1)],  # extend
        }

        self.STOP_KEY = 'x'
        self.HOME_KEY = 'p'
        self.PWM = 255


    # ================= INPUT CALLBACK =================
    def input_callback(self, msg: String):
        key = msg.data.strip().lower()

        joints = Joints()
        joints.gripper = self._rest()
        joints.wrist1 = self._rest()
        joints.wrist2 = self._rest()
        joints.elbow = self._rest()
        joints.shoulder1 = self._rest()
        joints.shoulder2 = self._rest()

        if key == self.HOME_KEY:
            joints.wrist1.direction = True
            self.motor_pub.publish(joints)
            self.get_logger().warn("HOME REQUEST")
            return

        if key == self.STOP_KEY:
            self.motor_pub.publish(joints)
            self.get_logger().warn("STOP ALL MOTORS")
            return

        if key in self.GRIPPER_MAP:
            self._apply_motion(joints, self.GRIPPER_MAP[key])
            self.motor_pub.publish(joints)
            self.get_logger().info(f"Gripper motion: {key}")
            return

        if key in self.WRIST_MAP:
            self._apply_motion(joints, self.WRIST_MAP[key])
            self.motor_pub.publish(joints)
            self.get_logger().info(f"Wrist motion: {key}")
            return

        if key in self.SHOULDER_MAP:
            self._apply_motion(joints, self.SHOULDER_MAP[key])
            self.motor_pub.publish(joints)
            self.get_logger().info(f"Shoulder motion: {key}")
            return

        if key in self.ELBOW_MAP:
            self._apply_motion(joints, self.ELBOW_MAP[key])
            self.motor_pub.publish(joints)
            self.get_logger().info(f"Elbow motion: {key}")
            return

        self.get_logger().warn(f"Unknown key: {key}")

    # ================= HELPERS =================
    def _apply_motion(self, joints, motion_list):
        for joint_name, direction in motion_list:
            setattr(joints, joint_name, self._active(direction))

    def _rest(self):
        m = MotorControl()
        m.direction = False
        m.pwm = 0
        return m

    def _active(self, direction):
        m = MotorControl()
        m.direction = True if direction > 0 else False
        m.pwm = self.PWM
        return m


def main():
    rclpy.init()
    node = JointControlNode()
    try:
        rclpy.spin(node)
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
