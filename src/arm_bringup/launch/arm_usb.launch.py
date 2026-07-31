from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    nodes = [
        # Adjust 'port' if these don't match your laptop — check with
        # `ls /dev/ttyUSB*` (or /dev/ttyACM*) after plugging both boards in.
        Node(
            package='ros_bt',
            executable='ros_write_motors_espA_usb',
            name='motors_espA',
            parameters=[{'port': '/dev/ttyUSB0', 'baud': 115200}],
        ),
        Node(
            package='ros_bt',
            executable='ros_write_motors_espB_usb',
            name='motors_espB',
            parameters=[{'port': '/dev/ttyUSB1', 'baud': 115200}],
        ),
        Node(package='controls', executable='control_node_v2', name='control_node_v2'),
    ]

    return LaunchDescription(nodes)
