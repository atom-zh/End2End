# 仿真目录

此处放置 R550 阿克曼的 Gazebo 世界、URDF/Xacro、传感器插件和仿真 launch 文件。目标是与实车发布相同的话题、单位和 frame。

计划内容：

- `worlds/`：室内和园区 Gazebo 世界。
- `models/r550_ackermann/`：车辆模型。
- `launch/r550_sim.launch.py`：车辆 + 雷达 + 深度相机 + IMU + joystick。
