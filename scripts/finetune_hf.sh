#!/usr/bin/env bash
# Example LoRA/PEFT fine-tuning workflow (requires GPU and installed deps)
# This is a templated script — edit paths and args before running.

set -euo pipefail

MODEL="/path/to/base/model"
DATA_DIR="/path/to/dataset"
OUTPUT_DIR="/path/to/output"

python -m pip install transformers datasets accelerate peft

python -u run_clm.py \
  --model_name_or_path "$MODEL" \
  --dataset_name "$DATA_DIR" \
  --output_dir "$OUTPUT_DIR" \
  --per_device_train_batch_size 4 \
  --num_train_epochs 3 \
  --learning_rate 2e-4 \
  --fp16 \
  --do_train

echo "Training finished, upload or point HF_MODEL_PATH to $OUTPUT_DIR"
