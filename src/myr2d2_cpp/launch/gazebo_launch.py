import launch
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import launch_ros
import os


def generate_launch_description():
    pkg_share = launch_ros.substitutions.FindPackageShare(package='myr2d2_cpp').find('myr2d2_cpp')
    default_model_path = os.path.join(pkg_share, 'urdf/myr2d2_gz.urdf')
    world_file_name = 'empty_world.world'
    world_path = os.path.join(pkg_share, 'worlds', world_file_name)

    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': ['-r -v4 ', world_path], 
        'on_exit_shutdown': 'true'}.items()
    )

    spawn_entity = launch_ros.actions.Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                    '-name', 'myr2d2',
                    '-z', '0.12'], #check if this is needed
        output='screen'
    )

    cmd_vel_bridge = launch_ros.actions.Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='cmd_vel_bridge',
        arguments=['/model/myr2d2/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
        parameters=[{'qos_overrides./model/myr2d2.subscriber.reliability': 'reliable'}],
        output='screen'
    )

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(name='model', default_value=default_model_path,
                                                description='Absolute path to robot urdf file'),
        gazebo,
        robot_state_publisher_node,
        spawn_entity,
        cmd_vel_bridge,
    ])