#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAST-LIO2 運行狀態監控腳本
根據用戶提供的調試步驟進行檢查：
1. 檢查 /odom 是否有里程計輸出
2. 檢查 IMU 數據（加速度、方向、時間戳）
3. 檢查時間同步（Sim Time）
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from rosgraph_msgs.msg import Clock
import time
from collections import deque
from datetime import datetime
import threading
import signal
import sys
import math


class FASTLIO2Monitor(Node):
    def __init__(self):
        super().__init__('fastlio2_monitor')
        
        # 可配置的 topic 名稱（用戶可以通過參數修改）
        self.declare_parameter('odom_topic', '/odom')  # 用戶指定的 odom topic
        self.declare_parameter('imu_topic', '/imu')    # IMU topic
        self.declare_parameter('clock_topic', '/clock') # 時鐘 topic
        
        self.odom_topic = self.get_parameter('odom_topic').get_parameter_value().string_value
        self.imu_topic = self.get_parameter('imu_topic').get_parameter_value().string_value
        self.clock_topic = self.get_parameter('clock_topic').get_parameter_value().string_value
        
        # 統計信息
        self.odom_stats = {
            'message_count': 0,
            'timestamps': deque(maxlen=100),
            'positions': deque(maxlen=100),  # 存儲位置歷史
            'last_message_time': None,
            'first_message_time': None,
            'last_position': None,
            'position_changed': False,
            'last_odom_msg': None,
        }
        
        self.imu_stats = {
            'message_count': 0,
            'timestamps': deque(maxlen=100),
            'last_message_time': None,
            'first_message_time': None,
            'last_imu_msg': None,
            'has_gravity': False,  # 是否檢測到重力（z 軸加速度接近 9.8）
            'all_zero_accel': False,  # 加速度是否全為 0
        }
        
        self.clock_stats = {
            'message_count': 0,
            'last_sim_time': None,
            'last_message_time': None,
            'has_clock': False,
        }
        
        self.lock = threading.Lock()
        
        # 創建訂閱者
        self.create_subscribers()
        
        # 設置定時器用於定期輸出統計信息
        self.timer = self.create_timer(2.0, self.print_statistics)  # 每 2 秒輸出一次
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.get_logger().info("=" * 80)
        self.get_logger().info("FAST-LIO2 運行狀態監控腳本已啟動")
        self.get_logger().info("=" * 80)
        self.get_logger().info(f"監控話題：")
        self.get_logger().info(f"  - 里程計: {self.odom_topic}")
        self.get_logger().info(f"  - IMU: {self.imu_topic}")
        self.get_logger().info(f"  - 時鐘: {self.clock_topic}")
        self.get_logger().info("=" * 80)
        self.get_logger().info("按 Ctrl+C 退出")
        self.get_logger().info("")
    
    def create_subscribers(self):
        """為每個話題創建訂閱者"""
        # 訂閱里程計
        try:
            self.odom_sub = self.create_subscription(
                Odometry,
                self.odom_topic,
                self.odom_callback,
                10
            )
            self.get_logger().info(f"已訂閱里程計話題: {self.odom_topic}")
        except Exception as e:
            self.get_logger().error(f"訂閱里程計話題 {self.odom_topic} 失敗: {e}")
        
        # 訂閱 IMU
        try:
            self.imu_sub = self.create_subscription(
                Imu,
                self.imu_topic,
                self.imu_callback,
                10
            )
            self.get_logger().info(f"已訂閱 IMU 話題: {self.imu_topic}")
        except Exception as e:
            self.get_logger().error(f"訂閱 IMU 話題 {self.imu_topic} 失敗: {e}")
        
        # 訂閱時鐘（可選，用於檢查 Sim Time）
        try:
            self.clock_sub = self.create_subscription(
                Clock,
                self.clock_topic,
                self.clock_callback,
                10
            )
            self.get_logger().info(f"已訂閱時鐘話題: {self.clock_topic}")
        except Exception as e:
            self.get_logger().warn(f"訂閱時鐘話題 {self.clock_topic} 失敗（可能不是 Sim Time 模式）: {e}")
    
    def odom_callback(self, msg):
        """里程計消息回調函數"""
        with self.lock:
            stats = self.odom_stats
            current_time = time.time()
            
            # 更新統計信息
            stats['message_count'] += 1
            stats['timestamps'].append(current_time)
            
            if stats['first_message_time'] is None:
                stats['first_message_time'] = current_time
            stats['last_message_time'] = current_time
            
            # 提取位置
            pos = msg.pose.pose.position
            current_position = (pos.x, pos.y, pos.z)
            stats['positions'].append(current_position)
            stats['last_odom_msg'] = msg
            
            # 檢查位置是否變化
            if stats['last_position'] is not None:
                dx = abs(current_position[0] - stats['last_position'][0])
                dy = abs(current_position[1] - stats['last_position'][1])
                dz = abs(current_position[2] - stats['last_position'][2])
                
                # 如果位置變化超過 0.01 米，認為有變化
                if dx > 0.01 or dy > 0.01 or dz > 0.01:
                    stats['position_changed'] = True
            
            stats['last_position'] = current_position
    
    def imu_callback(self, msg):
        """IMU 消息回調函數"""
        with self.lock:
            stats = self.imu_stats
            current_time = time.time()
            
            # 更新統計信息
            stats['message_count'] += 1
            stats['timestamps'].append(current_time)
            
            if stats['first_message_time'] is None:
                stats['first_message_time'] = current_time
            stats['last_message_time'] = current_time
            stats['last_imu_msg'] = msg
            
            # 檢查加速度
            accel = msg.linear_acceleration
            accel_x = accel.x
            accel_y = accel.y
            accel_z = accel.z
            
            # 檢查是否全為 0
            if abs(accel_x) < 0.001 and abs(accel_y) < 0.001 and abs(accel_z) < 0.001:
                stats['all_zero_accel'] = True
            else:
                stats['all_zero_accel'] = False
            
            # 檢查是否有重力（z 軸應該接近 9.8 或 -9.8 m/s²）
            # 考慮到可能的方向，檢查絕對值
            if abs(abs(accel_z) - 9.8) < 2.0:  # 允許 2 m/s² 的誤差
                stats['has_gravity'] = True
            elif abs(abs(accel_x) - 9.8) < 2.0 or abs(abs(accel_y) - 9.8) < 2.0:
                # 重力可能在 x 或 y 軸（取決於 IMU 安裝方向）
                stats['has_gravity'] = True
            else:
                stats['has_gravity'] = False
    
    def clock_callback(self, msg):
        """時鐘消息回調函數"""
        with self.lock:
            stats = self.clock_stats
            stats['message_count'] += 1
            stats['last_sim_time'] = msg.clock.sec + msg.clock.nanosec * 1e-9
            stats['last_message_time'] = time.time()
            stats['has_clock'] = True
    
    def calculate_frequency(self, timestamps):
        """計算發布頻率（Hz）"""
        if len(timestamps) < 2:
            return 0.0
        
        # 計算時間間隔
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i-1]
            if diff > 0:
                time_diffs.append(diff)
        
        if not time_diffs:
            return 0.0
        
        # 計算平均頻率
        avg_interval = sum(time_diffs) / len(time_diffs)
        frequency = 1.0 / avg_interval if avg_interval > 0 else 0.0
        
        return frequency
    
    def print_statistics(self):
        """打印統計信息和診斷結果"""
        with self.lock:
            print("\033[2J\033[H", end="")  # 清屏並移動光標到頂部
            print("=" * 100)
            print(f"FAST-LIO2 運行狀態監控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 100)
            print()
            
            # ========== 步驟 1：檢查里程計 ==========
            print("【步驟 1】檢查 FAST-LIO2 是否有輸出里程計")
            print("-" * 100)
            print(f"話題: {self.odom_topic}")
            
            odom_stats = self.odom_stats
            if odom_stats['message_count'] == 0:
                print("❌ 狀態: 完全沒有數據輸出")
                print()
                print("可能原因：")
                print("  - 程式卡死在初始化階段")
                print("  - 時間戳錯亂導致拒絕處理新數據")
                print("  - FAST-LIO2 節點未啟動或 topic 名稱不正確")
                print()
                print("建議檢查：")
                print("  1. 確認 FAST-LIO2 是否已啟動")
                print("  2. 檢查 Isaac Sim 是否有發布 /clock")
                print("  3. 確認啟動 FAST-LIO2 時有加 use_sim_time:=true")
                print("  4. 使用以下命令檢查 topic 是否存在：")
                print(f"     ros2 topic list | grep -E 'odom|Odometry'")
                print()
            else:
                # 計算頻率
                frequency = self.calculate_frequency(list(odom_stats['timestamps']))
                
                # 計算運行時間
                runtime = 0.0
                if odom_stats['first_message_time']:
                    runtime = time.time() - odom_stats['first_message_time']
                
                print(f"✅ 狀態: 有數據輸出")
                print(f"  消息數量: {odom_stats['message_count']}")
                print(f"  發布頻率: {frequency:.3f} Hz")
                print(f"  運行時間: {runtime:.1f} 秒")
                
                # 檢查位置是否變化
                if odom_stats['last_position'] is not None:
                    pos = odom_stats['last_position']
                    print(f"  當前位置: x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.3f}")
                    
                    # 檢查位置變化
                    if len(odom_stats['positions']) >= 2:
                        first_pos = odom_stats['positions'][0]
                        last_pos = odom_stats['positions'][-1]
                        dx = abs(last_pos[0] - first_pos[0])
                        dy = abs(last_pos[1] - first_pos[1])
                        dz = abs(last_pos[2] - first_pos[2])
                        total_movement = math.sqrt(dx*dx + dy*dy + dz*dz)
                        
                        print(f"  位置變化: Δx={dx:.3f}, Δy={dy:.3f}, Δz={dz:.3f}, 總距離={total_movement:.3f} 米")
                        
                        if total_movement < 0.01:
                            print("  ⚠️  警告: 位置幾乎沒有變化（可能車子靜止或 SLAM 未正常工作）")
                            print("  可能原因：")
                            print("    - IMU 數據有問題（例如讀不到加速度，或者時間戳比雷達慢）")
                            print("    - FAST-LIO2 認為車子靜止")
                        else:
                            print("  ✅ 位置有變化，SLAM 正常運行")
                
                # 顯示時間戳信息
                if odom_stats['last_odom_msg']:
                    msg = odom_stats['last_odom_msg']
                    stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
                    print(f"  最後消息時間戳: {stamp_sec:.3f} 秒")
                
                # 顯示最後更新時間
                if odom_stats['last_message_time']:
                    time_since_last = time.time() - odom_stats['last_message_time']
                    if time_since_last < 1.0:
                        print(f"  最後更新: {time_since_last*1000:.0f} ms 前")
                    else:
                        print(f"  最後更新: {time_since_last:.1f} 秒前")
                
                print()
            
            # ========== 步驟 2：檢查 IMU 數據 ==========
            print("【步驟 2】檢查 IMU 數據（最可能的問題來源）")
            print("-" * 100)
            print(f"話題: {self.imu_topic}")
            
            imu_stats = self.imu_stats
            if imu_stats['message_count'] == 0:
                print("❌ 狀態: 完全沒有 IMU 數據")
                print()
                print("可能原因：")
                print("  - Isaac Sim 的 IMU 未正確配置")
                print("  - IMU topic 名稱不正確")
                print()
                print("建議檢查：")
                print("  1. 確認 Isaac Sim 的 Action Graph 中 ROS2 IMU Bridge 已啟用")
                print("  2. 檢查 IMU Bridge 使用 Simulation Time")
                print("  3. 確認頻率設為 100Hz 以上")
                print("  4. 使用以下命令檢查 topic：")
                print(f"     ros2 topic echo {self.imu_topic} --no-arr")
                print()
            else:
                frequency = self.calculate_frequency(list(imu_stats['timestamps']))
                runtime = 0.0
                if imu_stats['first_message_time']:
                    runtime = time.time() - imu_stats['first_message_time']
                
                print(f"✅ 狀態: 有 IMU 數據")
                print(f"  消息數量: {imu_stats['message_count']}")
                print(f"  發布頻率: {frequency:.3f} Hz")
                print(f"  運行時間: {runtime:.1f} 秒")
                
                if imu_stats['last_imu_msg']:
                    msg = imu_stats['last_imu_msg']
                    accel = msg.linear_acceleration
                    orient = msg.orientation
                    
                    print(f"  線性加速度: x={accel.x:.3f}, y={accel.y:.3f}, z={accel.z:.3f} m/s²")
                    print(f"  角速度: x={msg.angular_velocity.x:.3f}, y={msg.angular_velocity.y:.3f}, z={msg.angular_velocity.z:.3f} rad/s")
                    print(f"  方向: w={orient.w:.3f}, x={orient.x:.3f}, y={orient.y:.3f}, z={orient.z:.3f}")
                    
                    # 檢查加速度
                    if imu_stats['all_zero_accel']:
                        print("  ❌ 嚴重問題: 加速度全為 0！")
                        print("  FAST-LIO2 如果發現 IMU 的加速度是 0，會認為車子靜止")
                        print("  建議：檢查 Isaac Sim 的 IMU 設定")
                    else:
                        print("  ✅ 加速度非零")
                    
                    # 檢查重力
                    if imu_stats['has_gravity']:
                        print("  ✅ 檢測到重力（加速度正常）")
                    else:
                        print("  ⚠️  警告: 未檢測到重力（z 軸應該接近 9.8 或 -9.8 m/s²）")
                        print("  如果 X, Y, Z 都不是 9.8 左右，可能 IMU 設定有問題")
                    
                    # 檢查方向
                    if abs(orient.w) < 0.001 and abs(orient.x) < 0.001 and \
                       abs(orient.y) < 0.001 and abs(orient.z) < 0.001:
                        print("  ⚠️  警告: 方向全為 0 且沒有變化，可能也有問題")
                    
                    # 顯示時間戳
                    stamp_sec = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
                    print(f"  時間戳: {stamp_sec:.3f} 秒")
                    
                    # 與里程計時間戳比較（如果有的話）
                    if odom_stats['last_odom_msg']:
                        odom_msg = odom_stats['last_odom_msg']
                        odom_stamp = odom_msg.header.stamp.sec + odom_msg.header.stamp.nanosec * 1e-9
                        time_diff = abs(stamp_sec - odom_stamp)
                        print(f"  與里程計時間差: {time_diff:.3f} 秒")
                        if time_diff > 1.0:
                            print("  ⚠️  警告: IMU 和里程計時間戳差異過大（>1秒）")
                            print("  如果時間差很多，演算法會直接丟棄數據")
                
                if imu_stats['last_message_time']:
                    time_since_last = time.time() - imu_stats['last_message_time']
                    if time_since_last < 1.0:
                        print(f"  最後更新: {time_since_last*1000:.0f} ms 前")
                    else:
                        print(f"  最後更新: {time_since_last:.1f} 秒前")
                
                print()
            
            # ========== 步驟 3：檢查時間同步 ==========
            print("【步驟 3】檢查時間同步（Sim Time）")
            print("-" * 100)
            print(f"話題: {self.clock_topic}")
            
            clock_stats = self.clock_stats
            if clock_stats['message_count'] == 0:
                print("⚠️  狀態: 未檢測到 /clock 話題")
                print()
                print("可能原因：")
                print("  - 未使用 Sim Time 模式")
                print("  - Isaac Sim 未發布 /clock")
                print()
                print("重要提醒：")
                print("  Isaac Sim 發出的數據時間戳是「模擬時間（從 0 開始）」")
                print("  如果 FAST-LIO2 沒開 use_sim_time，它會用「電腦系統時間」去比對")
                print("  發現模擬器傳來的數據是「幾小時前」甚至「幾十年前」的舊數據，會全部丟掉")
                print()
                print("建議：")
                print("  重啟 FAST-LIO2，並確保加上 use_sim_time 參數：")
                print("  ros2 launch fast_lio mapping.launch.py config_file:=velodyne16.yaml use_sim_time:=true")
                print()
            else:
                print(f"✅ 狀態: 有 /clock 數據")
                print(f"  消息數量: {clock_stats['message_count']}")
                if clock_stats['last_sim_time'] is not None:
                    print(f"  當前模擬時間: {clock_stats['last_sim_time']:.3f} 秒")
                if clock_stats['last_message_time']:
                    time_since_last = time.time() - clock_stats['last_message_time']
                    if time_since_last < 1.0:
                        print(f"  最後更新: {time_since_last*1000:.0f} ms 前")
                    else:
                        print(f"  最後更新: {time_since_last:.1f} 秒前")
                print()
            
            # ========== 總結診斷 ==========
            print("=" * 100)
            print("診斷總結")
            print("=" * 100)
            
            issues = []
            if odom_stats['message_count'] == 0:
                issues.append("❌ 里程計沒有輸出")
            elif odom_stats['last_position'] and len(odom_stats['positions']) >= 2:
                first_pos = odom_stats['positions'][0]
                last_pos = odom_stats['positions'][-1]
                total_movement = math.sqrt(
                    (last_pos[0] - first_pos[0])**2 +
                    (last_pos[1] - first_pos[1])**2 +
                    (last_pos[2] - first_pos[2])**2
                )
                if total_movement < 0.01:
                    issues.append("⚠️  里程計位置沒有變化")
            
            if imu_stats['message_count'] == 0:
                issues.append("❌ IMU 沒有數據")
            elif imu_stats['all_zero_accel']:
                issues.append("❌ IMU 加速度全為 0")
            elif not imu_stats['has_gravity']:
                issues.append("⚠️  IMU 未檢測到重力")
            
            if clock_stats['message_count'] == 0:
                issues.append("⚠️  未檢測到 Sim Time（/clock）")
            
            if not issues:
                print("✅ 所有檢查項目正常")
            else:
                print("發現以下問題：")
                for issue in issues:
                    print(f"  {issue}")
            
            print()
            print("=" * 100)
            print("提示: 按 Ctrl+C 退出")
            print()
    
    def signal_handler(self, signum, frame):
        """信號處理函數"""
        print("\n\n正在退出...")
        rclpy.shutdown()
        sys.exit(0)


def main(args=None):
    rclpy.init(args=args)
    
    monitor = FASTLIO2Monitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

