#!/usr/bin/env python3
"""Decimate a binary STL mesh for Gazebo/RViz visual use."""

from __future__ import annotations

import argparse
from pathlib import Path

import trimesh
from fast_simplification import simplify


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--target-reduction", type=float, default=0.95)
    args = parser.parse_args()

    mesh = trimesh.load(args.input, force="mesh")
    points, faces = simplify(
        mesh.vertices.astype("float64"),
        mesh.faces.astype("int32"),
        target_reduction=args.target_reduction,
    )
    out = trimesh.Trimesh(vertices=points, faces=faces, process=False)
    out.export(args.output)
    print(
        f"{args.input.name}: {len(mesh.faces)} -> {len(faces)} faces, "
        f"written to {args.output}"
    )


if __name__ == "__main__":
    main()
