#!/usr/bin/env bash
set -euo pipefail

cd /data/home/shenx/code_repositories/GMR_A3/outputs/agibot_a3_calib_4/videos

ffmpeg -y \
  -ss 1.4 -i s00_root_feet.mp4 \
  -ss 1.4 -i s01_root_torso_feet.mp4 \
  -ss 1.4 -i s02_add_legs.mp4 \
  -ss 1.4 -i s03_arms_pos_only.mp4 \
  -ss 1.4 -i s04_full_table1_only.mp4 \
  -ss 1.4 -i s05_full_two_stage.mp4 \
  -filter_complex "\
    [0:v]scale=426:240,drawtext=text='s00 root feet':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6[v0];\
    [1:v]scale=426:240,drawtext=text='s01 torso feet':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6[v1];\
    [2:v]scale=426:240,drawtext=text='s02 add legs':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6[v2];\
    [3:v]scale=426:240,drawtext=text='s03 arms pos only':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6[v3];\
    [4:v]scale=426:240,drawtext=text='s04 full table1':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6[v4];\
    [5:v]scale=426:240,drawtext=text='s05 full two-stage':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6[v5];\
    [v0][v1][v2][v3][v4][v5]xstack=inputs=6:layout=0_0|426_0|0_240|426_240|0_480|426_480[out]" \
  -map "[out]" -frames:v 1 ../agibot_a3_calib_contact.jpg
