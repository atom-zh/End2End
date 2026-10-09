#!/usr/bin/env python3
"""Placeholder for SmolVLA ONNX/TensorRT export.

The recommended path is to export SmolVLA as split ONNX subgraphs (vision,
language, action generation), then build one TensorRT engine per subgraph. This
keeps dynamic axes manageable on Jetson Orin NX.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--precision", default="bf16", choices=["fp32", "fp16", "bf16"])
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "export_note.txt").write_text(
        "export entry point; wire split ONNX/TensorRT export once policy checkpoint is produced\n"
    )
    print(f"export placeholder created: {args.out}")


if __name__ == "__main__":
    main()
