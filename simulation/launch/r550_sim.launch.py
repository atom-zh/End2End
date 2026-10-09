import os
import tempfile
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command


def generate_launch_description():
    description_pkg = get_package_share_directory("r550_description")
    simulation_pkg = get_package_share_directory("simulation")
    gazebo_ros_pkg = get_package_share_directory("gazebo_ros")

    urdf_path = os.path.join(description_pkg, "urdf", "r550_ackermann_official.urdf")
    default_world = os.path.join(simulation_pkg, "worlds", "r550_indoor.world")

    # Gazebo does not reliably resolve package:// URIs for user workspaces.
    # Resolve them to the installed package path before spawning the entity.
    urdf_text = Path(urdf_path).read_text()
    resolved_urdf_text = urdf_text.replace(
        "package://r550_description", f"file://{description_pkg}"
    )
    resolved_urdf_dir = tempfile.mkdtemp(prefix="r550_ackermann_")
    resolved_urdf_path = os.path.join(resolved_urdf_dir, "r550_ackermann.urdf")
    Path(resolved_urdf_path).write_text(resolved_urdf_text)

    world_arg = DeclareLaunchArgument(
        "world",
        default_value=default_world,
        description="Gazebo world path",
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([gazebo_ros_pkg, "launch", "gazebo.launch.py"])
        ),
        launch_arguments={"world": LaunchConfiguration("world")}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description": ParameterValue(
                    resolved_urdf_text, value_type=str
                )
            }
        ],
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="spawn_r550",
        output="screen",
        arguments=[
            "-file",
            resolved_urdf_path,
            "-entity",
            "r550_ackermann",
            "-x",
            "0.0",
            "-y",
            "0.0",
            "-z",
            "0.16",
        ],
    )

    joy = Node(package="joy", executable="joy_node", name="joy_node", output="screen")

    teleop = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_twist_joy",
        output="screen",
        parameters=[{"enable_button": 0, "axis_linear.x": 1, "axis_angular.yaw": 0}],
    )

    scan_to_16line = Node(
        package="simulation",
        executable="scan_to_16line.py",
        name="scan_to_16line",
        output="screen",
    )

    return LaunchDescription(
        [
            world_arg,
            gazebo,
            robot_state_publisher,
            spawn_entity,
            joy,
            teleop,
            scan_to_16line,
        ]
    )
