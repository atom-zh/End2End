# R550 传统 Autoware 自动驾驶运行手册

本手册覆盖 R550 PLUS 阿克曼车基于 Autoware Universe 的室内/园区低速自动驾驶流程：传感器启动、建图、定位、规划、控制和实车验收。所有步骤均可在车机或开发机手动执行。

## 1. 目标与适用范围

- 面向已建图的室内和园区道路。
- 速度不超过 0.5 m/s，需要物理急停和遥控接管能力。
- 不包含红绿灯识别，障碍物按 `Unknown` 类型处理。

## 2. 前置条件

### 2.1 车机

```bash
ssh wheeltec@192.168.101.15
echo $ROS_DISTRO           # 预期 humble
echo $ROS_DOMAIN_ID        # 预期 31
ros2 pkg list | grep -E 'autoware_launch|autoware_wheeltec_interface|wheeltec_sensor_kit_launch'
```

确认工作空间已 source：

```bash
source /opt/ros/humble/setup.bash
source /home/wheeltec/wheeltec_ros2/install/setup.bash
source /home/wheeltec/autoware/install/setup.bash
```

### 2.2 开发机

```bash
source /opt/ros/humble/setup.bash
ros2 pkg list | grep -E 'gazebo_ros|rviz2|nav2'
```

开发机与车机需在 `192.168.101.0/24` 网段，且 `ROS_DOMAIN_ID=31` 保持一致。

## 3. 硬件与接口检查

| 设备 | 检查命令 | 预期 |
|---|---|---|
| 底盘 | `ls -l /dev/wheeltec_controller` | 指向 `ttyCH343USB0` |
| GNSS | `ls -l /dev/wheeltec_gnss` | 指向 `ttyACM0` |
| IMU | `ls -l /dev/wheeltec_IMU` | 指向 `ttyCH343USB1` |
| 雷达网络 | `ip -brief addr show enP8p1s0` | `192.168.1.102/24` |
| 深度相机 | `lsusb \| grep -i orbbec` | 出现 Orbbec Depth Sensor |

## 4. 传感器启动

建议先分开启动，便于定位问题。

```bash
# 底盘 + 外接 IMU + TF
ros2 launch common_wheeltec_sensor_launch imu_launch.py use_wheeltec_imu:=true

# 16 线雷达
ros2 launch common_wheeltec_sensor_launch lslidar_cx_launch.py

# GNSS/RTK
ros2 launch common_wheeltec_sensor_launch wheeltec_gnss_launch.py

# Astra Pro Plus
ros2 launch astra_camera astra_pro_plus.launch.py
```

验证话题和频率：

```bash
ros2 topic list
ros2 topic hz /point_cloud_raw
ros2 topic hz /sensing/imu/imu_data
ros2 topic hz /gps/fix
ros2 topic hz /camera/color/image_raw
```

预期：

- `/point_cloud_raw`：建议 20 Hz，低于 10 Hz 会导致定位漂移。
- `/sensing/imu/imu_data`：有 IMU 数据。
- `/gps/fix`：RTK 固定时 `status.status == 2`。
- `/camera/color/image_raw`：有彩色图像。

查看 TF：

```bash
ros2 run tf2_tools view_frames
```

应存在 `base_link -> laser`、`base_link -> camera_link`、`base_link -> gyro_link`、`base_link -> navsat_link`。

## 5. Autoware Universe

### 5.1 编译

车机源码已在 `/home/wheeltec/autoware`。修改参数后只编译需要的包：

```bash
cd /home/wheeltec/autoware
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

### 5.2 规划仿真

不需要真实传感器，可在开发机或车机运行：

```bash
ros2 launch autoware_launch planning_simulator.launch.xml \
  map_path:=/home/wheeltec/autoware/src/universe/autoware.universe/planning/planning_test_utils/test_map \
  vehicle_model:=wheeltec_vehicle \
  sensor_model:=wheeltec_sensor_kit
```

在 RViz2 中验证车辆模型、规划路线和速度曲线。

### 5.3 真实导航

```bash
ros2 launch autoware_launch autoware.launch.xml \
  map_path:=/home/wheeltec/autoware_map/my3 \
  vehicle_model:=wheeltec_vehicle \
  sensor_model:=wheeltec_sensor_kit
```

操作顺序：

1. 点击 `2D Pose Estimate` 给定初始位姿。
2. 等待约 30 秒，点云刷新并出现障碍物框。
3. 选择目标点。
4. `OperationMode` 选 `Auto`，`AutowareControl` 选 `Enable`。
5. 随时可切 `Stop`，或直接使用遥控/急停接管。

## 6. 建图

### 6.1 LIO-SAM 点云地图

录制传感器 bag：

```bash
ros2 bag record \
  /point_cloud_raw \
  /sensing/imu/imu_data \
  /gps/fix \
  /odom \
  -o r550_mapping
```

离线建图：

```bash
ros2 launch lio_sam run_usegnss.launch.py
ros2 bag play r550_mapping
```

输出点云地图文件需命名为 `pointcloud_map.pcd`。

### 6.2 Lanelet2 高精地图

使用 Vector Map Builder：

```text
https://tools.tier4.jp/vector_map_builder_ll2/
```

地图目录至少包含：

```text
my3/
├── lanelet2_map.osm
├── pointcloud_map.pcd
└── map_projector_info.yaml
```

GNSS 版使用 MGRS，填写 `mgrs_grid`；无 GNSS 版使用局部坐标系，`map_projector_info.yaml` 不填经纬度。

## 7. 导航与调参

- NDT 定位：室内 `Leaf size` 偏小，室外偏大；最大距离 200 m，最小距离 0.15 m。
- 横向控制：`tier4_control_component.launch.xml` 中 `lateral_controller_mode` 已调试 `pure_pursuit`。
- 纵向控制：调 `pid.param.yaml`，优先保证停车平稳、速度不过冲。
- 雷达点云：`angle_disable_min/max` 用于屏蔽车体方向点云。

## 8. 实车验收

顺序必须是：

1. 台架空转，确认 `/cmd_vel` 能安全驱动。
2. 室内低速，全程有人跟车，随时急停。
3. 园区低速，路径避开行人和机动车。

每次测试：

```bash
ros2 bag record -a -o run_$(date +%Y%m%d_%H%M%S)
```

保存日志：

```bash
mkdir -p log/$(date +%Y%m%d)
ros2 launch ... 2>&1 | tee log/$(date +%Y%m%d)/autoware.log
```

## 9. 故障排查

| 现象 | 检查 |
|---|---|
| 无点云 | 雷达 IP 是否可达：`ping 192.168.1.200`；端口 2368/2369 |
| TF 断链 | `ros2 run tf2_tools view_frames`，检查 `base_link -> laser` |
| 定位漂移 | 雷达频率、地图质量、初始位姿、NDT 参数 |
| 底盘不响应 | `/dev/wheeltec_controller` 是否存在、OLED 是否显示 `ROS`、急停是否释放 |
| RTK 不固定 | G70 RTK 绿灯是否常亮；4G DTU CORS 账号、Ntrip 参数；`/gps/fix` 状态码 |
| Autoware 不输出 | `OperationMode` 是否为 `Auto`，`AutowareControl` 是否为 `Enable`，`/control/command/control_cmd` 是否发布 |
