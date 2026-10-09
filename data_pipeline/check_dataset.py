#!/usr/bin/env python3
"""Basic quality checks for a converted LeRobot-style dataset directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path)
    args = parser.parse_args()

    manifest = args.dataset / "manifest.json"
    if not manifest.exists():
        raise SystemExit(f"manifest not found: {manifest}")

    data = json.loads(manifest.read_text())
    missing = data.get("missing_topics", [])
    if missing:
        raise SystemExit(f"dataset missing topics: {missing}")

    print("manifest ok")
    print("instruction:", data.get("instruction"))
    print("expected topics:", len(data.get("expected_topics", [])))
    print("TODO: add image/action statistical checks after real conversion")


if __name__ == "__main__":
    main()
