#!/usr/bin/env python3
"""Convert a Gazebo 2D LaserScan into a synthetic 16-line PointCloud2.

The Leishen C16 has 16 channels distributed over a vertical field of view. This
node takes the horizontal 2D scan and replicates each range across 16 vertical
angles, producing the same `/point_cloud_raw` topic shape used by the real car.
"""

from __future__ import annotations

import math

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, PointCloud2, PointField
from sensor_msgs_py import point_cloud2


class ScanTo16Line(Node):
    def __init__(self) -> None:
        super().__init__("scan_to_16line")

        self.declare_parameter("num_channels", 16)
        self.declare_parameter("vertical_min_deg", -15.0)
        self.declare_parameter("vertical_max_deg", 15.0)

        num_channels = int(self.get_parameter("num_channels").value)
        v_min = math.radians(float(self.get_parameter("vertical_min_deg").value))
        v_max = math.radians(float(self.get_parameter("vertical_max_deg").value))
        self.vertical_angles = np.linspace(v_min, v_max, num_channels)

        self.publisher = self.create_publisher(PointCloud2, "/point_cloud_raw", 10)
        self.subscription = self.create_subscription(
            LaserScan, "/scan", self.on_scan, 10
        )

    def on_scan(self, scan: LaserScan) -> None:
        ranges = np.asarray(scan.ranges, dtype=np.float32)
        valid = np.isfinite(ranges) & (ranges > scan.range_min) & (ranges < scan.range_max)
        indices = np.flatnonzero(valid)
        if indices.size == 0:
            self.publisher.publish(point_cloud2.create_cloud_xyz32(scan.header, []))
            return

        azimuth = scan.angle_min + indices * scan.angle_increment
        rr = ranges[indices]
        cos_az = np.cos(azimuth)
        sin_az = np.sin(azimuth)

        points = []
        for vangle in self.vertical_angles:
            cos_v = math.cos(vangle)
            sin_v = math.sin(vangle)
            xy = rr * cos_v
            points.extend(
                zip(
                    (xy * cos_az).tolist(),
                    (xy * sin_az).tolist(),
                    (rr * sin_v).tolist(),
                )
            )

        self.publisher.publish(point_cloud2.create_cloud_xyz32(scan.header, points))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ScanTo16Line()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
