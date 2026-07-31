from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # bind_bt.sh is installed as a package resource (see setup.py data_files),
    # so this resolves correctly regardless of where the workspace lives or
    # who built it — no hardcoded absolute path.
    bind_bt_path = os.path.join(
        get_package_share_directory('arm_bringup'),
        'scripts',
        'bind_bt.sh'
    )

    bind_bt = ExecuteProcess(
        # invoked via bash explicitly so this doesn't depend on the
        # installed file's executable bit surviving the copy
        cmd=['bash', bind_bt_path],
        output='screen'
    )

    nodes = [
        Node(package='ros_bt', executable='espA_read_enc', name='espA_read_enc'),
        Node(package='ros_bt', executable='espB_read_enc', name='espB_read_enc'),
        Node(package='ros_bt', executable='ros_write_motors_espA', name='motors_espA'),
        Node(package='ros_bt', executable='ros_write_motors_espB', name='motors_espB'),
        Node(package='ros_bt', executable='esp_read_enc_merger', name='enc_merger'),
        Node(package='controls', executable='control_node_v2', name='control_node_v2'),
    ]

    start_nodes_after_bt = RegisterEventHandler(
        OnProcessExit(
            target_action=bind_bt,
            on_exit=nodes
        )
    )

    return LaunchDescription([
        bind_bt,
        start_nodes_after_bt
    ])
