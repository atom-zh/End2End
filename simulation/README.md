# 仿真目录

Gazebo 仿真已具备最小可运行闭环：

- `launch/r550_sim.launch.py`：启动 Gazebo、R550 阿克曼模型、`robot_state_publisher`、joystick 和 teleop。
- `worlds/r550_office_indoor.world`：默认世界，20 m × 16 m 的办公室/实验室布局，包含 6 个带门洞的房间、中央走廊、柱子、桌椅、货架和走廊障碍物。
- `worlds/r550_complex_indoor.world`：中等复杂度的旧版测试世界，含隔间、柱子和障碍物。
- `worlds/r550_indoor.world`：只有两面墙的轻量回归世界，适合快速排查启动问题。
- 车辆模型：`../r550_description/urdf/r550_ackermann_official.urdf`，使用 `gazebo_ros_ackermann_drive` 驱动，前轮转向由控制器保持回正。

## 构建与运行

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select r550_description simulation
source install/setup.bash
ros2 launch simulation r550_sim.launch.py
```

使用其他世界：

```bash
ros2 launch simulation r550_sim.launch.py world:=/home/liuxiaolong/work/code/e2e/install/simulation/share/simulation/worlds/r550_complex_indoor.world
ros2 launch simulation r550_sim.launch.py world:=/home/liuxiaolong/work/code/e2e/install/simulation/share/simulation/worlds/r550_indoor.world
```

无界面验证：

```bash
ros2 launch simulation r550_sim.launch.py gui:=false
```

## 当前接口

- 底盘：`/cmd_vel` 输入，`/odom` 输出。
- 2D 雷达中间层：`/scan`。
- 16 线点云：`/point_cloud_raw`，由 `scan_to_16line.py` 从 `/scan` 生成。
- RGB 相机：`/camera/color/image_raw`、`/camera/color/camera_info`。
- 深度相机：`/camera/depth/image_rect_raw`、`/camera/depth/camera_info`、`/camera/depth/points`。
- IMU：`/sensing/imu/imu_data`，frame `gyro_link`。

## 待补

- 确认实车默认 URDF 候选后固定轴距/轮距参数。
- 可选的 GNSS/RTK 仿真插件，用于带 GNSS 的 Autoware 测试。
