import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition

from launch_ros.actions import Node


def generate_launch_description():
    """
    FAST-LIO2 Launch 文件 - 專為 Isaac Sim 整合設計
    
    TF Tree 結構：
    camera_init (Map) ──修正──> odom ──輪速計──> base_link
    
    說明：
    - FAST-LIO2 發布：camera_init -> body
    - Isaac Sim 發布：odom -> base_link
    - Static Transform Bridge：camera_init -> odom（自動添加）
    """
    package_path = get_package_share_directory('fast_lio')
    default_config_path = os.path.join(package_path, 'config')
    default_rviz_config_path = os.path.join(
        package_path, 'rviz', 'fastlio.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_path = LaunchConfiguration('config_path')
    config_file = LaunchConfiguration('config_file')
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='true',  # 默認使用模擬時間
        description='Use simulation (Isaac Sim) clock if true'
    )
    declare_config_path_cmd = DeclareLaunchArgument(
        'config_path', default_value=default_config_path,
        description='Yaml config file path'
    )
    declare_config_file_cmd = DeclareLaunchArgument(
        'config_file', default_value='velodyne.yaml',  # 默認使用 Velodyne 配置
        description='Config file'
    )
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='false',  # 默認不啟動 RViz（可選）
        description='Use RViz to monitor results'
    )
    declare_rviz_config_path_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path,
        description='RViz config file path'
    )

    # FAST-LIO2 節點
    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        parameters=[PathJoinSubstitution([config_path, config_file]),
                    {'use_sim_time': use_sim_time}],
        output='screen'
    )
    
    # Static Transform Publisher: camera_init -> odom
    # 這將 FAST-LIO2 的地圖原點 (camera_init) 連接到 Isaac Sim 的里程計原點 (odom)
    # 格式: x y z yaw pitch roll parent_frame child_frame
    # 初始時兩個原點重合，後續可以根據 SLAM 結果調整這個 transform
    tf_bridge_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_init_to_odom_bridge',
        arguments=['0', '0', '0', '0', '0', '0', 'camera_init', 'odom'],
        output='screen'
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        condition=IfCondition(rviz_use)
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_config_path_cmd)
    ld.add_action(declare_config_file_cmd)
    ld.add_action(declare_rviz_cmd)
    ld.add_action(declare_rviz_config_path_cmd)

    ld.add_action(fast_lio_node)
    ld.add_action(tf_bridge_node)  # 自動添加 TF bridge
    ld.add_action(rviz_node)

    return ld

