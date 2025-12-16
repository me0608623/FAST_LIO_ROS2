# FAST-LIO2 與 Isaac Sim 整合指南

## TF Tree 目標結構

```
camera_init (Map) ──修正──> odom ──輪速計──> base_link
```

### 說明

- **camera_init**: FAST-LIO2 的地圖原點（SLAM 計算的全局坐標系）
- **odom**: Isaac Sim 的里程計原點（模擬器的里程計坐標系）
- **base_link**: 機器人本體坐標系（Isaac Sim 發布）

## 實現方案

### 方案 A：使用 Launch 文件（推薦）

使用專門為 Isaac Sim 設計的 launch 文件，會自動添加 TF bridge：

```bash
cd ~/IsaacSim-ros_workspaces/jazzy_ws
source install/setup.bash

# 使用專為 Isaac Sim 設計的 launch 文件
ros2 launch fast_lio mapping_isaac_sim.launch.py config_file:=velodyne.yaml
```

這個 launch 文件會：
1. ✅ 啟動 FAST-LIO2（使用 velodyne.yaml 配置）
2. ✅ 自動發布 `camera_init -> odom` 的 static transform
3. ✅ 設置 `use_sim_time:=true`（使用模擬時間）

### 方案 B：使用標準 Launch 文件 + 手動啟動 TF Bridge

```bash
# 終端 1: 啟動 FAST-LIO2
ros2 launch fast_lio mapping.launch.py config_file:=velodyne.yaml use_sim_time:=true enable_tf_bridge:=true

# 或者終端 2: 手動啟動 TF Bridge
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 camera_init odom
```

### 方案 C：使用腳本

```bash
# 終端 1: 啟動 FAST-LIO2
ros2 launch fast_lio mapping.launch.py config_file:=velodyne.yaml use_sim_time:=true

# 終端 2: 運行 TF Bridge 腳本
bash ~/IsaacSim-ros_workspaces/jazzy_ws/src/FAST_LIO_ROS2/scripts/tf_bridge_isaac_sim.sh
```

## 配置說明

### FAST-LIO2 配置（velodyne.yaml）

**重要設定：**

1. **Body Frame 名稱**：
   - FAST-LIO2 使用硬編碼的 `"body"` 作為 body frame
   - 不會與 Isaac Sim 的 `base_link` 衝突 ✅

2. **時間同步**：
   ```yaml
   common:
       time_sync_en: false  # 如果 Isaac Sim 時間同步良好，保持 false
   ```

3. **模擬時間**：
   - Launch 文件會自動設置 `use_sim_time:=true`

### Isaac Sim 設定

**確認事項：**

1. ✅ Isaac Sim 正在發布 `odom -> base_link` 的 TF
2. ✅ 點雲話題：`/velodyne_points`
3. ✅ IMU 話題：`/imu`

## TF Tree 驗證

啟動後，使用以下命令驗證 TF Tree：

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

## 預期的 TF 結構

```
camera_init (fixed frame)
  └── odom (static transform, 0,0,0,0,0,0)
      └── base_link (Isaac Sim 發布)
```

**FAST-LIO2 發布的 TF：**
- `camera_init -> body`（SLAM 計算的位姿）

**注意：** `body` 和 `base_link` 是兩個不同的 frame，它們之間沒有直接的 transform。如果需要連接，可以添加：
```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 body base_link
```

## 調整 TF Bridge

如果 SLAM 結果需要修正，可以調整 static transform 的參數：

```bash
# 格式: x y z yaw pitch roll parent_frame child_frame
# 例如：如果需要在 X 方向偏移 1 米
ros2 run tf2_ros static_transform_publisher 1 0 0 0 0 0 camera_init odom
```

## 故障排除

### 問題 1: TF Tree 不完整

**症狀：** `ros2 run tf2_ros tf2_echo camera_init base_link` 失敗

**解決方案：**
1. 確認 Isaac Sim 正在發布 `odom -> base_link`
2. 確認 TF bridge 正在運行
3. 檢查所有節點是否使用相同的 `use_sim_time` 設置

### 問題 2: 時間不同步

**症狀：** TF 時間戳不匹配

**解決方案：**
```bash
# 確保所有節點使用模擬時間
ros2 param set /fastlio_mapping use_sim_time true
```

### 問題 3: body 和 base_link 不一致

**說明：** 這是正常的，因為：
- `body` 是 FAST-LIO2 計算的 SLAM 位姿
- `base_link` 是 Isaac Sim 的模擬位姿

如果需要讓它們一致，可以添加 `body -> base_link` 的 transform。

## 相關話題

FAST-LIO2 發布的話題：
- `/Laser_map`: 全局地圖點雲（frame_id: `camera_init`）
- `/cloud_registered`: 註冊後的點雲（frame_id: `camera_init`）
- `/cloud_registered_body`: 機體坐標系點雲（frame_id: `body`）
- `/Odometry`: 優化後的里程計（frame: `camera_init -> body`）

## 參考資料

- [FAST-LIO2 官方文檔](https://github.com/hku-mars/FAST_LIO)
- [ROS2 TF2 文檔](https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html)

