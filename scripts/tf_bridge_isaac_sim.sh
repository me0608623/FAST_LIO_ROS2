#!/bin/bash
# FAST-LIO2 與 Isaac Sim 的 TF Bridge 腳本
# 發布 static transform: camera_init -> odom

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}FAST-LIO2 TF Bridge for Isaac Sim${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "發布 static transform: camera_init -> odom"
echo ""
echo "TF Tree 結構："
echo "  camera_init (Map) ──修正──> odom ──輪速計──> base_link"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止${NC}"
echo ""

# 發布 static transform
# 格式: x y z yaw pitch roll parent_frame child_frame
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 camera_init odom

