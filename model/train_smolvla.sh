#!/usr/bin/env bash
set -euo pipefail

POLICY_PATH="${POLICY_PATH:-lerobot/smolvla_base}"
DATASET_REPO="${DATASET_REPO:?set DATASET_REPO}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/smolvla_r550}"
STEPS="${STEPS:-30000}"
BATCH_SIZE="${BATCH_SIZE:-32}"
LORA_RANK="${LORA_RANK:-64}"

lerobot-train \
  --policy.path="$POLICY_PATH" \
  --dataset.repo_id="$DATASET_REPO" \
  --output_dir="$OUTPUT_DIR" \
  --steps="$STEPS" \
  --batch_size="$BATCH_SIZE" \
  --peft.method_type=LORA \
  --peft.r="$LORA_RANK"
