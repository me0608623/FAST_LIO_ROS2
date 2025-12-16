> ROS2 Fork repo maintainer: [Ericsiii](https://github.com/Ericsii)

## Related Works and Extended Application

**SLAM:**

1. [ikd-Tree](https://github.com/hku-mars/ikd-Tree): A state-of-art dynamic KD-Tree for 3D kNN search.
2. [R2LIVE](https://github.com/hku-mars/r2live): A high-precision LiDAR-inertial-Vision fusion work using FAST-LIO as LiDAR-inertial front-end.
3. [LI_Init](https://github.com/hku-mars/LiDAR_IMU_Init): A robust, real-time LiDAR-IMU extrinsic initialization and synchronization package..
4. [FAST-LIO-LOCALIZATION](https://github.com/HViktorTsoi/FAST_LIO_LOCALIZATION): The integration of FAST-LIO with **Re-localization** function module.

**Control and Plan:**

1. [IKFOM](https://github.com/hku-mars/IKFoM): A Toolbox for fast and high-precision on-manifold Kalman filter.
2. [UAV Avoiding Dynamic Obstacles](https://github.com/hku-mars/dyn_small_obs_avoidance): One of the implementation of FAST-LIO in robot's planning.
3. [UGV Demo](https://www.youtube.com/watch?v=wikgrQbE6Cs): Model Predictive Control for Trajectory Tracking on Differentiable Manifolds.
4. [Bubble Planner](https://arxiv.org/abs/2202.12177): Planning High-speed Smooth Quadrotor Trajectories using Receding Corridors.

<!-- 10. [**FAST-LIVO**](https://github.com/hku-mars/FAST-LIVO): Fast and Tightly-coupled Sparse-Direct LiDAR-Inertial-Visual Odometry. -->

## FAST-LIO
**FAST-LIO** (Fast LiDAR-Inertial Odometry) is a computationally efficient and robust LiDAR-inertial odometry package. It fuses LiDAR feature points with IMU data using a tightly-coupled iterated extended Kalman filter to allow robust navigation in fast-motion, noisy or cluttered environments where degeneration occurs. Our package address many key issues:
1. Fast iterated Kalman filter for odometry optimization;
2. Automaticaly initialized at most steady environments;
3. Parallel KD-Tree Search to decrease the computation;

## FAST-LIO 2.0 (2021-07-05 Update)
<!-- ![image](doc/real_experiment2.gif) -->
<!-- [![Watch the video](doc/real_exp_2.png)](https://youtu.be/2OvjGnxszf8) -->
<div align="left">
<img src="doc/real_experiment2.gif" width=49.6% />
<img src="doc/ulhkwh_fastlio.gif" width = 49.6% >
</div>

**Related video:**  [FAST-LIO2](https://youtu.be/2OvjGnxszf8),  [FAST-LIO1](https://youtu.be/iYCY6T79oNU)

**Pipeline:**
<div align="center">
<img src="doc/overview_fastlio2.svg" width=99% />
</div>

**New Features:**
1. Incremental mapping using [ikd-Tree](https://github.com/hku-mars/ikd-Tree), achieve faster speed and over 100Hz LiDAR rate.
2. Direct odometry (scan to map) on Raw LiDAR points (feature extraction can be disabled), achieving better accuracy.
3. Since no requirements for feature extraction, FAST-LIO2 can support many types of LiDAR including spinning (Velodyne, Ouster) and solid-state (Livox Avia, Horizon, MID-70) LiDARs, and can be easily extended to support more LiDARs.
4. Support external IMU.
5. Support ARM-based platforms including Khadas VIM3, Nivida TX2, Raspberry Pi 4B(8G RAM).

**Related papers**: 

[FAST-LIO2: Fast Direct LiDAR-inertial Odometry](doc/Fast_LIO_2.pdf)

[FAST-LIO: A Fast, Robust LiDAR-inertial Odometry Package by Tightly-Coupled Iterated Kalman Filter](https://arxiv.org/abs/2010.08196)

**Contributors**

[Wei Xu 徐威](https://github.com/XW-HKU)，[Yixi Cai 蔡逸熙](https://github.com/Ecstasy-EC)，[Dongjiao He 贺东娇](https://github.com/Joanna-HE)，[Fangcheng Zhu 朱方程](https://github.com/zfc-zfc)，[Jiarong Lin 林家荣](https://github.com/ziv-lin)，[Zheng Liu 刘政](https://github.com/Zale-Liu), [Borong Yuan](https://github.com/borongyuan)

<!-- <div align="center">
    <img src="doc/results/HKU_HW.png" width = 49% >
    <img src="doc/results/HKU_MB_001.png" width = 49% >
</div> -->

## 1. Prerequisites
### 1.1 **Ubuntu** and **ROS**
**Ubuntu >= 20.04**

The **default from apt** PCL and Eigen is enough for FAST-LIO to work normally.

ROS >= Foxy (Recommend to use ROS-Humble). [ROS Installation](https://docs.ros.org/en/humble/Installation.html)

### 1.2. **PCL && Eigen**
PCL    >= 1.8,   Follow [PCL Installation](https://pointclouds.org/downloads/#linux).

Eigen  >= 3.3.4, Follow [Eigen Installation](http://eigen.tuxfamily.org/index.php?title=Main_Page).

### <span id="1.3">1.3. **livox_ros_driver2**</span>
Follow [livox_ros_driver2 Installation](https://github.com/Livox-SDK/livox_ros_driver2).

You can also use the one I modified [livox_ros_driver2](https://github.com/Ericsii/livox_ros_driver2/tree/feature/use-standard-unit)

*Remarks:*
- Since the FAST-LIO must support Livox serials LiDAR firstly, so the **livox_ros_driver** must be installed and **sourced** before run any FAST-LIO launch file.
- How to source? The easiest way is add the line ``` source $Livox_ros_driver_dir$/devel/setup.bash ``` to the end of file ``` ~/.bashrc ```, where ``` $Livox_ros_driver_dir$ ``` is the directory of the livox ros driver workspace (should be the ``` ws_livox ``` directory if you completely followed the livox official document).


## 2. Build
Clone the repository and colcon build:

```bash
    cd <ros2_ws>/src # cd into a ros2 workspace folder
    git clone https://github.com/Ericsii/FAST_LIO_ROS2.git --recursive
    cd ..
    rosdep install --from-paths src --ignore-src -y
    colcon build --symlink-install
    . ./install/setup.bash # use setup.zsh if use zsh
```
- **Remember to source the livox_ros_driver before build (follow [1.3 livox_ros_driver](#1.3))**
- If you want to use a custom build of PCL, add the following line to ~/.bashrc
```export PCL_ROOT={CUSTOM_PCL_PATH}```
## 3. Directly run
Noted:

A. Please make sure the IMU and LiDAR are **Synchronized**, that's important.

B. The warning message "Failed to find match for field 'time'." means the timestamps of each LiDAR points are missed in the rosbag file. That is important for the forward propagation and backwark propagation.

C. We recommend to set the **extrinsic_est_en** to false if the extrinsic is give. As for the extrinsic initiallization, please refer to our recent work: [**Robust Real-time LiDAR-inertial Initialization**](https://github.com/hku-mars/LiDAR_IMU_Init).

### 3.1 Run use ros launch
Connect to your PC to Livox LiDAR by following  [Livox-ros-driver2 installation](https://github.com/Livox-SDK/livox_ros_driver2), then
```bash
cd <ros2_ws>
. install/setup.bash # use setup.zsh if use zsh
ros2 launch fast_lio mapping.launch.py config_file:=avia.yaml
```

Change `config_file` parameter to other yaml file under config directory as you need.

Launch livox ros driver. Use MID360 as an example.

```bash
ros2 launch livox_ros_driver2 msg_MID360_launch.py
```

- For livox serials, FAST-LIO only support the data collected by the ``` livox_lidar_msg.launch ``` since only its ``` livox_ros_driver2/CustomMsg ``` data structure produces the timestamp of each LiDAR point which is very important for the motion undistortion. ``` livox_lidar.launch ``` can not produce it right now.
- If you want to change the frame rate, please modify the **publish_freq** parameter in the [livox_lidar_msg.launch](https://github.com/Livox-SDK/livox_ros_driver/blob/master/livox_ros_driver2/launch/livox_lidar_msg.launch) of [Livox-ros-driver](https://github.com/Livox-SDK/livox_ros_driver2) before make the livox_ros_driver pakage.

### 3.2 For Livox serials with external IMU

mapping_avia.launch theratically supports mid-70, mid-40 or other livox serial LiDAR, but need to setup some parameters befor run:

Edit ``` config/avia.yaml ``` to set the below parameters:

1. LiDAR point cloud topic name: ``` lid_topic ```
2. IMU topic name: ``` imu_topic ```
3. Translational extrinsic: ``` extrinsic_T ```
4. Rotational extrinsic: ``` extrinsic_R ``` (only support rotation matrix)
- The extrinsic parameters in FAST-LIO is defined as the LiDAR's pose (position and rotation matrix) in IMU body frame (i.e. the IMU is the base frame). They can be found in the official manual.
- FAST-LIO produces a very simple software time sync for livox LiDAR, set parameter ```time_sync_en``` to ture to turn on. But turn on **ONLY IF external time synchronization is really not possible**, since the software time sync cannot make sure accuracy.

### 3.4 PCD file save

1. Enable `pcd_save.pcd_save_en` in the config file and set the `map_file_path` to the path where the map will be saved.
2. Launch the fastlio2 according to README.
3. Open RQt and switch to `Plugins->Services->Service Caller`. Trigger the service `/map_save`, then the pcd map file will be generated

```pcl_viewer scans.pcd``` can visualize the point clouds.

*Tips for pcl_viewer:*
- change what to visualize/color by pressing keyboard 1,2,3,4,5 when pcl_viewer is running. 
```
    1 is all random
    2 is X values
    3 is Y values
    4 is Z values
    5 is intensity
```

## 4. Rosbag Example
### 4.1 Livox Avia Rosbag
<div align="left">
<img src="doc/results/HKU_LG_Indoor.png" width=47% />
<img src="doc/results/HKU_MB_002.png" width = 51% >

Files: Can be downloaded from [google drive](https://drive.google.com/drive/folders/1CGYEJ9-wWjr8INyan6q1BZz_5VtGB-fP?usp=sharing)**!!!This ros1 bag should be convert to ros2!!!**

Run:
```bash
ros2 launch fast_lio mapping.launch.py config_path:=<path_to_your_config_file>
ros2 bag play <your_bag_dir>

```

### 4.2 Velodyne HDL-32E Rosbag

**NCLT Dataset**: Original bin file can be found [here](http://robots.engin.umich.edu/nclt/).

We produce [Rosbag Files](https://drive.google.com/drive/folders/1VBK5idI1oyW0GC_I_Hxh63aqam3nocNK?usp=sharing) and [a python script](https://drive.google.com/file/d/1leh7DxbHx29DyS1NJkvEfeNJoccxH7XM/view) to generate Rosbag files: ```python3 sensordata_to_rosbag_fastlio.py bin_file_dir bag_name.bag```**!!!This ros1 bag should be convert to ros2!!!** To convert ros1 bag to ros2 bag, please follow the documentation [Convert rosbag versions](https://ternaris.gitlab.io/rosbags/topics/convert.html)
    
Run:
```
roslaunch fast_lio mapping_velodyne.launch
rosbag play YOUR_DOWNLOADED.bag
```

## 5.Implementation on UAV
In order to validate the robustness and computational efficiency of FAST-LIO in actual mobile robots, we build a small-scale quadrotor which can carry a Livox Avia LiDAR with 70 degree FoV and a DJI Manifold 2-C onboard computer with a 1.8 GHz Intel i7-8550U CPU and 8 G RAM, as shown in below.

The main structure of this UAV is 3d printed (Aluminum or PLA), the .stl file will be open-sourced in the future.

<div align="center">
    <img src="doc/uav01.jpg" width=40.5% >
    <img src="doc/uav_system.png" width=57% >
</div>

## 6. Isaac Sim 整合使用指南

### 6.1 Topic 設定說明

FAST-LIO2 需要訂閱以下 ROS2 topics：

#### 輸入 Topics（必須）

| Topic 名稱 | 訊息類型 | 說明 | 預設值 |
|-----------|---------|------|--------|
| `/velodyne_points` | `sensor_msgs/PointCloud2` | 雷達點雲數據 | 在 `config/velodyne.yaml` 中設定 |
| `/imu` | `sensor_msgs/Imu` | IMU 慣性測量數據 | 在 `config/velodyne.yaml` 中設定 |

#### 輸出 Topics

| Topic 名稱 | 訊息類型 | 說明 |
|-----------|---------|------|
| `/Laser_map` | `sensor_msgs/PointCloud2` | 全局地圖點雲（frame_id: `camera_init`） |
| `/cloud_registered` | `sensor_msgs/PointCloud2` | 註冊後的點雲（frame_id: `camera_init`） |
| `/cloud_registered_body` | `sensor_msgs/PointCloud2` | 機體坐標系點雲（frame_id: `body`） |
| `/Odometry` | `nav_msgs/Odometry` | 優化後的里程計（frame: `camera_init -> body`） |

#### Topic 設定方式

在配置檔案中設定（例如 `config/velodyne.yaml`）：

```yaml
common:
    lid_topic:  "/velodyne_points"  # 雷達點雲 topic
    imu_topic:  "/imu"              # IMU topic
```

**重要提醒：**
- 確保 Isaac Sim 發布的 topic 名稱與配置檔案中的設定一致
- 如果 Isaac Sim 使用不同的 topic 名稱，請修改配置檔案或使用 ROS2 的 `topic_tools` 進行重映射

### 6.2 使用方式

#### 方式 A：使用 Isaac Sim 專用 Launch 文件（推薦）

```bash
cd ~/IsaacSim-ros_workspaces/jazzy_ws
source install/setup.bash

# 啟動 FAST-LIO2（自動配置 Isaac Sim 整合）
ros2 launch fast_lio mapping_isaac_sim.launch.py config_file:=velodyne.yaml
```

**此方式會自動：**
- ✅ 設置 `use_sim_time:=true`（使用模擬時間）
- ✅ 發布 `camera_init -> odom` 的 static transform（TF bridge）
- ✅ 使用指定的配置檔案（`velodyne.yaml`）

#### 方式 B：使用標準 Launch 文件

```bash
cd ~/IsaacSim-ros_workspaces/jazzy_ws
source install/setup.bash

# 啟動 FAST-LIO2（需手動指定參數）
ros2 launch fast_lio mapping.launch.py \
    config_file:=velodyne.yaml \
    use_sim_time:=true \
    enable_tf_bridge:=true
```

#### 方式 C：手動啟動 TF Bridge

如果需要手動控制 TF bridge：

```bash
# 終端 1: 啟動 FAST-LIO2
ros2 launch fast_lio mapping.launch.py config_file:=velodyne.yaml use_sim_time:=true

# 終端 2: 啟動 TF Bridge
bash ~/IsaacSim-ros_workspaces/jazzy_ws/src/FAST_LIO_ROS2/scripts/tf_bridge_isaac_sim.sh

# 或直接使用命令
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 camera_init odom
```

### 6.3 TF Tree 結構

FAST-LIO2 與 Isaac Sim 整合後的 TF Tree：

```
camera_init (Map) ──修正──> odom ──輪速計──> base_link
```

**說明：**
- `camera_init`: FAST-LIO2 的地圖原點（SLAM 計算的全局坐標系）
- `odom`: Isaac Sim 的里程計原點（模擬器的里程計坐標系）
- `base_link`: 機器人本體坐標系（Isaac Sim 發布）

**FAST-LIO2 發布的 TF：**
- `camera_init -> body`（SLAM 計算的位姿）

**驗證 TF Tree：**

```bash
# 查看完整的 TF Tree
ros2 run tf2_tools view_frames

# 檢查特定 transform
ros2 run tf2_ros tf2_echo camera_init odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo camera_init base_link  # 應該能成功（通過 odom）

# 查看所有 TF frames
ros2 run tf2_ros tf2_monitor
```

### 6.4 監控數據方式

#### 方式 A：使用監控腳本（推薦）

我們提供了一個專門的監控腳本，可以實時檢查 FAST-LIO2 的運行狀態：

```bash
cd ~/IsaacSim-ros_workspaces/jazzy_ws
source install/setup.bash

# 啟動監控腳本
ros2 run fast_lio monitor_fastlio2.py
```

**監控腳本會檢查：**

1. **里程計輸出狀態**
   - 是否有 `/odom` 數據輸出
   - 發布頻率
   - 位置變化情況
   - 時間戳信息

2. **IMU 數據狀態**
   - IMU 數據是否正常接收
   - 加速度是否為零（異常情況）
   - 是否檢測到重力（驗證 IMU 數據有效性）
   - 發布頻率

3. **時間同步狀態**
   - 是否使用 Sim Time（檢查 `/clock` topic）
   - 模擬時間與系統時間的同步情況

**自定義監控參數：**

```bash
ros2 run fast_lio monitor_fastlio2.py \
    --ros-args \
    -p odom_topic:=/odom \
    -p imu_topic:=/imu \
    -p clock_topic:=/clock
```

#### 方式 B：使用 ROS2 命令行工具

**檢查 Topic 列表：**

```bash
# 列出所有 topics
ros2 topic list

# 檢查特定 topic 是否存在
ros2 topic list | grep -E 'odom|imu|velodyne'
```

**監聽 Topic 數據：**

```bash
# 監聽里程計數據
ros2 topic echo /odom --no-arr

# 監聽 IMU 數據
ros2 topic echo /imu --no-arr

# 監聽點雲數據（僅顯示訊息頭部）
ros2 topic echo /velodyne_points --no-arr | head -20
```

**檢查 Topic 發布頻率：**

```bash
# 檢查里程計頻率
ros2 topic hz /odom

# 檢查 IMU 頻率
ros2 topic hz /imu

# 檢查點雲頻率
ros2 topic hz /velodyne_points
```

**查看 Topic 訊息類型：**

```bash
ros2 topic info /odom
ros2 topic info /imu
ros2 topic info /velodyne_points
```

#### 方式 C：使用 RViz2 可視化

```bash
# 啟動 FAST-LIO2（帶 RViz）
ros2 launch fast_lio mapping_isaac_sim.launch.py \
    config_file:=velodyne.yaml \
    rviz:=true

# 或單獨啟動 RViz2
rviz2
```

**在 RViz2 中設定：**
- Fixed Frame: `camera_init` 或 `odom`
- 添加 PointCloud2 顯示，選擇 `/Laser_map` 或 `/cloud_registered`
- 添加 TF 顯示，查看 TF Tree 結構

### 6.5 常見問題排查

#### 問題 1：里程計沒有輸出

**症狀：** `/odom` topic 沒有數據

**檢查步驟：**
1. 確認 FAST-LIO2 節點是否正常啟動
   ```bash
   ros2 node list | grep fastlio
   ```

2. 確認是否使用 Sim Time
   ```bash
   ros2 param get /fastlio_mapping use_sim_time
   ```
   應該返回 `true`

3. 檢查 Isaac Sim 是否發布 `/clock`
   ```bash
   ros2 topic echo /clock --no-arr
   ```

4. 使用監控腳本進行詳細診斷
   ```bash
   ros2 run fast_lio monitor_fastlio2.py
   ```

#### 問題 2：IMU 數據異常

**症狀：** IMU 加速度全為 0 或未檢測到重力

**解決方案：**
1. 檢查 Isaac Sim 的 IMU Bridge 設定
   - 確認 ROS2 IMU Bridge 已啟用
   - 確認使用 Simulation Time
   - 確認頻率設為 100Hz 以上

2. 檢查 IMU topic 名稱是否正確
   ```bash
   ros2 topic echo /imu --no-arr
   ```

#### 問題 3：時間同步問題

**症狀：** 數據被丟棄，時間戳不匹配

**解決方案：**
```bash
# 確保所有節點使用模擬時間
ros2 param set /fastlio_mapping use_sim_time true

# 重啟 FAST-LIO2，確保加上 use_sim_time 參數
ros2 launch fast_lio mapping_isaac_sim.launch.py config_file:=velodyne.yaml
```

#### 問題 4：TF Tree 不完整

**症狀：** `ros2 run tf2_ros tf2_echo camera_init base_link` 失敗

**解決方案：**
1. 確認 TF bridge 正在運行
   ```bash
   ros2 node list | grep camera_init_to_odom_bridge
   ```

2. 確認 Isaac Sim 正在發布 `odom -> base_link`
   ```bash
   ros2 run tf2_ros tf2_echo odom base_link
   ```

3. 檢查所有節點是否使用相同的 `use_sim_time` 設置

### 6.6 配置檔案說明

主要配置檔案：`config/velodyne.yaml`

**關鍵參數說明：**

```yaml
common:
    lid_topic:  "/velodyne_points"      # 雷達點雲 topic（必須與 Isaac Sim 一致）
    imu_topic:  "/imu"                  # IMU topic（必須與 Isaac Sim 一致）
    time_sync_en: false                 # 時間同步（通常保持 false）

preprocess:
    lidar_type: 2                       # 2 = Velodyne LiDAR
    scan_line: 32                       # 掃描線數
    scan_rate: 10                        # 掃描頻率（Hz）
    blind: 2.0                           # 盲區距離（米）

mapping:
    fov_degree: 360.0                   # 視野角度
    det_range: 100.0                     # 檢測範圍（米）

publish:
    map_en: true                         # 發布地圖點雲
    scan_publish_en: true                # 發布掃描點雲
```

**詳細配置說明請參考：** `ISAAC_SIM_INTEGRATION.md`

## 7. Acknowledgments

Thanks for LOAM(J. Zhang and S. Singh. LOAM: Lidar Odometry and Mapping in Real-time), [Livox_Mapping](https://github.com/Livox-SDK/livox_mapping), [LINS](https://github.com/ChaoqinRobotics/LINS---LiDAR-inertial-SLAM) and [Loam_Livox](https://github.com/hku-mars/loam_livox).
