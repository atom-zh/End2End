# R550 端到端 + VLA 自动驾驶工程

本仓库用于 R550 PLUS 阿克曼实验车的仿真、数据采集、SmolVLA 端到端训练与实车部署，同时保留传统 Autoware 规则链作为独立路线。目标是所有步骤都可以脱离 AI、按文档和脚本手动复现。

## 最终目标与成功标准

1. 在 R550 PLUS 阿克曼实验车上完成“先仿真、后实车”的端到端 + VLA 自动驾驶，覆盖室内与园区低速场景。
2. 传统 Autoware 规则链作为可独立运行的基线路线；SmolVLA 端到端作为本项目主路线。
3. 实车自动驾驶必须满足安全底线：物理急停、遥控接管、最大速度限制、推理/通信超时停车。
4. 数据、训练、仿真、导出、部署和实车验收全流程脚本化，且每个步骤都有可脱离 AI 手动复现的运行手册。
5. 仿真验收先通过室内路线，再通过园区路线；实车验收按“台架 → 室内 → 园区”逐级推进。

## 已确认硬件与软件基线

| 项目 | 内容 |
|---|---|
| 底盘 | R550 PLUS，阿克曼转向 |
| 车端主控 | Jetson Orin NX 16G，JetPack 6.2 / L4T R36.4.3 |
| 车端系统 | Ubuntu 22.04，ROS 2 Humble，CUDA 12.6，cuDNN 9.3，TensorRT 10.3 |
| 开发机 | Ubuntu 22.04 x86_64，ROS 2 Humble，Gazebo 11 |
| 雷达 | Leishen 16 线，`192.168.1.200:2368/2369` |
| 深度相机 | Orbbec Astra Pro Plus |
| GNSS/RTK | WHEELTEC G70（u-blox） |
| 外接 IMU | Yesense |
| VLA 路线 | `lerobot/smolvla_base`，LoRA 微调，TensorRT 部署 |

## 目录结构

```text
docs/                运行手册、资源清单、环境说明
robot_config/        车机与开发机配置、传感器参数
scripts/             可复用脚本
simulation/          Gazebo 世界、URDF、仿真启动文件
r550_bringup/        实车传感器与控制启动
r550_description/    车辆 URDF/Xacro
r550_interfaces/     自定义 ROS 2 接口（按需）
data_pipeline/       bag 录制、数据转换与质检
model/               SmolVLA 训练与评估脚本
deploy/              ONNX/TensorRT 导出与车端推理节点
notebooks/           分析脚本
```

## 快速入口

- 传统 Autoware 路线：[docs/runbook_autoware_traditional.md](docs/runbook_autoware_traditional.md)
- SmolVLA 端到端路线：[docs/runbook_e2e_smolvla.md](docs/runbook_e2e_smolvla.md)
- 环境与资源清单：[docs/inventory.md](docs/inventory.md)

## 仓库约定

- 原始资料盘内容只记录路径和版本，不复制进仓库。
- rosbag、模型权重、编译产物、缓存不提交 Git。
- 所有命令尽量脚本化；每个文档都包含预期结果与失败处置。
