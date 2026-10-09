# R550 资源与环境清单

本文档是所有外部资料、硬件参数和系统配置的唯一索引。变更后请同步更新日期和版本。

## 1. 原始资料盘

根路径：`/media/home/share/R550`

| 目录 | 用途 | 优先阅读 |
|---|---|---|
| `1.WHEELTEC ROS机器人通用资料` | ROS1/ROS2 教程、底盘控制、主控镜像、ROS 源码 | `7.ROS源码/ROS2源码/Humble源码` |
| `2.WHEELTEC R550 PLUS ROS大型科研机器人系列资料` | R550 PLUS 底盘硬件、STM32 源码、原理图 | `2.运动底盘开发手册` |
| `镭神多线雷达V3.0与三维重建及AutoWare自动驾驶客户资料` | 16 线雷达、三维重建、Autoware 客户资料 | `ROS2_Autoware.universe...` |

关键源码包：

- Humble 常规源码：`/media/home/share/R550/1.WHEELTEC ROS机器人通用资料/7.ROS源码/ROS2源码/Humble源码/JP5.1.1_常规ROS主控_humble_src_202409.zip`
- Autoware 源码：`/media/home/share/R550/1.WHEELTEC ROS机器人通用资料/7.ROS源码/ROS2源码/Humble源码/ROS2多线雷达功能/autoware_src_2025_04_14.zip`
- Autoware 测试地图：`/media/home/share/R550/1.WHEELTEC ROS机器人通用资料/7.ROS源码/ROS2源码/Humble源码/ROS2多线雷达功能/autoware_test_map.zip`

已复制到仓库的建模文件：

- `r550_description/urdf/wheeltec/`：Wheeltec 全系 URDF。
- `r550_description/gazebo/mini_akm/`：Gazebo 阿克曼 xacro + STL。
- `r550_description/radar/雷达_雷神16线雷达.stp`：16 线雷达 3D 模型。
- `r550_description/autoware/wheeltec_vehicle_description/`：Autoware 车辆模型与参数。
- `r550_description/autoware/wheeltec_sensor_kit_description/`：Autoware 传感器套件模型与标定。

## 2. 开发机

| 项目 | 值 |
|---|---|
| 主机 | Ubuntu 22.04.5 LTS，x86_64 |
| CPU/内存 | 32 核 / 62 GiB |
| ROS | ROS 2 Humble |
| 仿真 | Gazebo 11.10.2 |
| ROS 包 | Nav2、slam_toolbox、rtabmap、gazebo_ros_pkgs、velodyne_pointcloud |
| 网络 | `enp3s0 192.168.101.240/24`，可访问车机 `192.168.101.15` |
| GPU | 存在两张 NVIDIA GPU，但当前内核模块未加载；Gazebo 先用 CPU |

## 3. 车机 R550

| 项目 | 值 |
|---|---|
| 登录 | `wheeltec@192.168.101.15` |
| 型号 | Jetson Orin NX Engineering Reference Developer Kit Super |
| 系统 | Ubuntu 22.04.5，内核 5.15.148-tegra，aarch64 |
| JetPack/L4T | R36.4.3，CUDA 12.6，TensorRT 10.3，cuDNN 9.3 |
| 内存 | 15.6 GiB 统一内存，8 核 CPU |
| 磁盘 | 根分区 233G，已用 64G，可用 157G |
| ROS | Humble，819 个已安装包 |
| ROS_DOMAIN_ID | 31 |
| 工作空间 | `/home/wheeltec/wheeltec_ros2`、`/home/wheeltec/autoware` |

## 4. 传感器与端口

| 传感器 | 设备/地址 | 话题 | 关键参数 |
|---|---|---|---|
| 底盘 | `/dev/wheeltec_controller`，115200 | `/cmd_vel`、`/odom` | 阿克曼；STM32 内部完成转向控制 |
| 16 线雷达 | `192.168.1.200:2368/2369` | `/point_cloud_raw` | frame `laser`，TF `x=0.26 y=0 z=0.228 roll=-1.57` |
| Astra Pro Plus | USB 2bc5:0614 | `/camera/...` | `astra_pro_plus.launch.py` |
| GNSS/RTK G70 | `/dev/wheeltec_gnss`，115200 | `/gps/fix` | u-blox USB ID 1546:01a9 |
| Yesense IMU | `/dev/wheeltec_IMU`，460800 | `/sensing/imu/imu_data` | frame `gyro_link` |

## 5. 关键 launch 与模型参数

- 实车传感器整体启动：`wheeltec_sensors` 系列；Autoware 使用 `wheeltec_sensor_kit` 与 `wheeltec_vehicle`。
- Autoware 车辆参数：轴距 `0.322 m`、轮距 `0.312 m`、最大转角 `1.2 rad`、仿真限速 `0.5 m/s`。
- `autoware_wheeltec_interface` 订阅 `/control/command/control_cmd`，用自行车模型发布 `/cmd_vel`。
