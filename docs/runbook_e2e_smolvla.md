# R550 SmolVLA 端到端自动驾驶运行手册

本手册覆盖 R550 PLUS 阿克曼车使用 SmolVLA 进行语言条件化端到端驾驶的数据采集、微调、仿真评估、TensorRT 部署和实车迁移。

## 1. 目标与适用范围

- 输入：RGB 图像、底盘状态、IMU、速度/转角、自然语言指令。
- 输出：速度与前轮转角，经安全仲裁后转成 `/cmd_vel`。
- 场景：室内与园区低速驾驶，安全层独立于模型。

## 2. 为什么选 SmolVLA

`lerobot/smolvla_base` 约 450M 参数，是 Hugging Face 提供的轻量 VLA 基础模型：

- LeRobot 原生支持，训练脚本统一。
- 单张 GPU 可训练，LoRA 微调成本低。
- 社区已在 8GB Jetson Orin Nano 上通过拆分 ONNX + TensorRT 运行，R550 的 Orin NX 16G 具备部署条件。
- 输入图像、机器人状态和语言指令，输出动作，匹配“端到端 + VLA”目标。

OpenVLA 7B 不适合直接上车实时推理，仅作为后续离线蒸馏或云端对照。

## 3. 环境准备

开发机或训练 GPU 机器：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r data_pipeline/requirements.txt
pip install "lerobot[smolvla]"
```

验证：

```bash
python -c "import lerobot; print(lerobot.__version__)"
python -c "import rosbags, h5py, cv2"
```

## 4. 数据采集

### 4.1 统一话题

实车和仿真必须发布相同话题与 frame：

```text
/camera/color/image_raw
/point_cloud_raw
/sensing/imu/imu_data
/odom
/joy
```

动作采用：

```text
速度 speed (m/s)
前轮转角 steering_angle (rad)
```

### 4.2 实车录包

先启动传感器和遥操作：

```bash
ros2 launch common_wheeltec_sensor_launch imu_launch.py use_wheeltec_imu:=true
ros2 launch common_wheeltec_sensor_launch lslidar_cx_launch.py
ros2 launch astra_camera astra_pro_plus.launch.py
ros2 run joy joy_node
```

录制：

```bash
ros2 bag record \
  /camera/color/image_raw \
  /camera/depth/points \
  /point_cloud_raw \
  /sensing/imu/imu_data \
  /odom \
  /joy \
  -o demo_$(date +%Y%m%d_%H%M%S)
```

### 4.3 仿真录包

在 Gazebo 中启动 R550 阿克曼模型、传感器插件和 joystick，然后执行同样的 `ros2 bag record`。仿真与实车的话题名、单位和 frame 必须完全一致。

## 5. 数据集转换与质检

仓库提供转换脚本：

```bash
source .venv/bin/activate
python data_pipeline/bag_to_lerobot.py \
  --bag demo_2026 \
  --out data/demo_hdf5 \
  --instruction "沿当前车道低速直行，遇到障碍物停车"
```

输出 `data/demo_hdf5/dataset.h5` 和 `manifest.json`。转换后运行质检：

```bash
python data_pipeline/check_dataset.py --dataset data/demo_hdf5
```

检查项：

- 视频帧率、分辨率一致。
- 动作频率一致。
- 时间戳单调递增。
- 图像亮度/色彩无明显异常。
- 动作值在速度和转角安全范围内。

当前输出是项目原生 HDF5 中间格式；进入 SmolVLA 训练前，再通过 LeRobot 适配器把 `dataset.h5` 转成 LeRobot 数据集。这样可以在不依赖 LeRobot 版本细节的情况下先完成录包和质检。

转换为 LeRobot 数据集：

```bash
python data_pipeline/hdf5_to_lerobot.py \
  --hdf5 data/demo_hdf5/dataset.h5 \
  --manifest data/demo_hdf5/manifest.json \
  --repo-id r550/demo \
  --fps 20
```

## 6. SmolVLA 微调

### 6.1 小样本过拟合

```bash
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=<your_dataset_repo> \
  --output_dir=outputs/smolvla_smoke \
  --steps=500 \
  --batch_size=32
```

若小样本 loss 不能显著下降，先检查数据格式和动作频率，不要直接全量训练。

### 6.2 正式微调

```bash
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --dataset.repo_id=<your_dataset_repo> \
  --output_dir=outputs/smolvla_r550 \
  --steps=30000 \
  --batch_size=32 \
  --peft.method_type=LORA \
  --peft.r=64
```

推荐策略：冻结 VLM 主干，训练动作头和投影层；若显存不足，降低 `batch_size` 或图像分辨率。

## 7. 仿真评估

评估路线：

- 室内 5 条：直行、转弯、避障、停车、窄通道。
- 园区 3 条：环线、长直道、复杂交叉口。

指标：

- 任务成功率。
- 横向误差和纵向速度误差。
- 碰撞次数。
- 单次任务完成时间。

输出保存到 `model/eval/`，每轮保留评估结果和回放 bag。

## 8. 部署到 Orin NX

### 8.1 导出 ONNX/TensorRT

推荐导出后拆分为视觉、语言、动作若干 ONNX 子图，逐个子图构建 TensorRT engine，避免单一图超出显存或动态形状导致失败。

```bash
python deploy/export_smolvla.py \
  --policy outputs/smolvla_r550 \
  --out deploy/engines \
  --precision bf16
```

### 8.2 车端推理节点

推理节点发布：

```text
ackermann_msgs/AckermannDriveStamped -> /vla/command
```

`vehicle_command_gate` 对 VLA、遥操作和急停做仲裁，最终发布 `/cmd_vel`。

```bash
ros2 run r550_vla_deploy smolvla_infer_node
ros2 run r550_safety vehicle_command_gate
```

### 8.3 推理时延监控

```bash
ros2 topic hz /vla/command
```

记录每步推理时延和 GPU/内存占用。若单步推理低于控制频率要求，采用异步推理，即边执行当前动作块边预测下一块。

## 9. 实车迁移

顺序：

1. 台架空转，确认输出映射正确。
2. 室内低速，速度上限从低值开始。
3. 园区低速，避开行人与机动车。

每次实车试验都录制全量 bag，失败片段标记后回灌训练集。

## 10. 安全与故障排查

安全要求：

- 物理急停优先于任何软件输出。
- 遥控接管优先于 VLA。
- 推理超时自动停车。
- 设置最大速度和最大转向角。

| 现象 | 检查 |
|---|---|
| 输出抖动 | 检查动作频率、图像时间戳、低通滤波参数 |
| 推理过慢 | 拆分 ONNX、TensorRT 精度、输入分辨率 |
| 实车表现差于仿真 | 检查 sim-to-real 数据分布、相机标定、底盘响应 |
| 节点无输出 | 检查模型路径、TensorRT engine 是否匹配 Orin 架构 |
| 急停失效 | 立即停止测试，修复物理急停链路后再继续 |
