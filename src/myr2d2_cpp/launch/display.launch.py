from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import os

def generate_launch_description():
    ld = LaunchDescription()
    
    # Find package share directory
    pkg_share = FindPackageShare(package='myr2d2_cpp').find('myr2d2_cpp')
    
    # Set paths to URDF and RVIZ config
    urdf_model_path = os.path.join(pkg_share, 'urdf', 'myr2d2_gz.urdf')
    # urdf_model_path = os.path.join(pkg_share, 'urdf', 'myr2d2.urdf')
    # urdf_model_path = os.path.join(pkg_share, 'urdf', '08-macroed.urdf.xacro')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'urdf.rviz')

    # Create robot description parameter
    robot_description = ParameterValue(
        Command(['xacro ', urdf_model_path]),
        value_type=str
    )

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }]
    )

    # Joint State Publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[{
            'source_list': ['joint_states1'],
            'rate': 30,
        }]
    )

    # RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    # Robot Control Node
    control_node = Node(
        package='myr2d2_cpp',
        executable='myr2d2_control',
        name='myr2d2_control',
        output='screen',
        parameters=[{
            'use_sim_time': False
        }]
    )

    # Add actions to launch description
    ld.add_action(robot_state_publisher_node)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(rviz_node)
    ld.add_action(control_node)

    return ld
