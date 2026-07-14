#!/usr/bin/env bash
set -euo pipefail

cd /data/home/shenx/code_repositories/GMR_A3

GVHMR_FILE="${1:-/data/home/shenx/code_repositories/GVHMR/outputs/raw_batch/4/hmr4d_results.pt}"
OUT_DIR="outputs/agibot_a3_calib_4"
mkdir -p "${OUT_DIR}/pkl" "${OUT_DIR}/videos"

CONDA="/data/home/shenx/miniconda3/bin/conda"
export MUJOCO_GL=egl

for name in \
  s00_root_feet \
  s01_root_torso_feet \
  s02_add_legs \
  s03_arms_pos_only \
  s04_full_table1_only \
  s05_full_two_stage
do
  cfg="general_motion_retargeting/ik_configs/calib_agibot_a3/${name}.json"
  pkl="${OUT_DIR}/pkl/${name}.pkl"
  mp4="${OUT_DIR}/videos/${name}.mp4"
  echo "=== Retarget ${name}"
  "${CONDA}" run -n gmr python scripts/gvhmr_to_robot.py \
    --robot agibot_a3 \
    --gvhmr_pred_file "${GVHMR_FILE}" \
    --ik_config_path "${cfg}" \
    --save_path "${pkl}" \
    --no_viewer
  echo "=== Render ${name}"
  "${CONDA}" run -n gmr python scripts/vis_robot_motion.py \
    --robot agibot_a3 \
    --robot_motion_path "${pkl}" \
    --record_video \
    --no_viewer \
    --max_loops 1 \
    --video_path "${mp4}" \
    --video_width 1280 \
    --video_height 720
done

ls -lh "${OUT_DIR}/videos"
