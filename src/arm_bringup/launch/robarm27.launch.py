from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    port_a_arg = DeclareLaunchArgument(
        'port_a', default_value='/dev/ttyUSB0',
        description='Serial port for ESP-A (gripper/wrist)'
    )
    port_b_arg = DeclareLaunchArgument(
        'port_b', default_value='/dev/ttyUSB1',
        description='Serial port for ESP-B (elbow/shoulder)'
    )
    baud_arg = DeclareLaunchArgument(
        'baud', default_value='115200',
        description='Baud rate for both serial ports'
    )

    nodes = [
        Node(
            package='web_ui',
            executable='web_server',
            name='web_server',
            output='screen',
        ),
        Node(
            package='controls',
            executable='control_node_v2',
            name='control_node_v2',
            output='screen',
        ),
        Node(
            package='ros_bt',
            executable='ros_write_motors_espA_usb',
            name='motors_espA',
            parameters=[{
                'port': LaunchConfiguration('port_a'),
                'baud': LaunchConfiguration('baud'),
            }],
            output='screen',
        ),
        Node(
            package='ros_bt',
            executable='ros_write_motors_espB_usb',
            name='motors_espB',
            parameters=[{
                'port': LaunchConfiguration('port_b'),
                'baud': LaunchConfiguration('baud'),
            }],
            output='screen',
        ),
    ]

    return LaunchDescription([
        port_a_arg,
        port_b_arg,
        baud_arg,
        *nodes,
    ])
