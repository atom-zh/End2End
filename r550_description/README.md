# 车辆描述与建模文件

放置 R550 PLUS 阿克曼 URDF/Xacro 和参考网格，仿真与 RViz 共用。关键尺寸见 `robot_config/r550_robot.yaml`。

## 已收录内容

| 目录 | 内容 | 来源 |
|---|---|---|
| `urdf/wheeltec/` | Wheeltec 全系 URDF，含 `senior_akm_robot.urdf`、`top_akm_bs_robot.urdf`、`top_akm_dl_robot.urdf` | `JP5.1.1_常规ROS主控_humble_src_202409.zip` 的 `wheeltec_robot_urdf` |
| `urdf/ROS2环境配置更换urdf教程.pdf` | URDF 切换教程 | `6.ROS2系列教程/.../8.ROS2精细URDF模型配置使用` |
| `gazebo/mini_akm/` | Gazebo 阿克曼小车 xacro + STL，作为仿真插件与传动参考 | ROS1 `10.gazebo建图导航仿真/wheeltec_robot_gazebo` |
| `radar/雷达_雷神16线雷达.stp` | 16 线雷达机械 3D 模型 | `镭神多线雷达.../三维模型/雷达_雷神16线雷达` |
| `autoware/wheeltec_vehicle_description/` | Autoware `wheeltec_vehicle` 的 xacro、vehicle_info、simulator_model 和 mesh | `autoware_src_2025_04_14.zip` |
| `autoware/wheeltec_sensor_kit_description/` | Autoware `wheeltec_sensor_kit` 的传感器 URDF 与标定文件 | `autoware_src_2025_04_14.zip` |
| `meshes/r550_ackermann/` | 从实车 `wheeltec_robot_urdf` 复制的 R550 大车阿克曼真实 STL | 车机 `/home/wheeltec/wheeltec_ros2/install/...` |
| `reference/wheeltec_robot_urdf/` | `top_akm_dl/bs`、`senior_akm` 三套完整 URDF+网格 | 车机 `wheeltec_robot_urdf` |

## R550 阿克曼候选 URDF

- `urdf/wheeltec/top_akm_dl_robot.urdf`：轮距/轴距更接近大型科研底盘。
- `urdf/wheeltec/senior_akm_robot.urdf`：Wheeltec launch 默认的旗舰阿克曼候选。
- `urdf/wheeltec/top_akm_bs_robot.urdf`：另一大型阿克曼候选。

实车对应哪个型号需结合 OLED 的 TYPE 值和实际尺寸确认，确认后固定为项目默认模型。

当前 Gazebo 仿真 `urdf/r550_ackermann.urdf` 使用 `meshes/r550_ackermann` 的 R550 大车网格作为视觉外观，碰撞体仍为简化几何。
