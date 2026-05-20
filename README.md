# AgiBot A3 Motion Retargeting

把 BVH 人体动作重定向到 AgiBot A3，并导出GMR格式的机器人运动数据文件 `pkl`。

<p align="center">
  <video src="assets/agibot_a3_retarget.mp4" controls muted loop playsinline width="100%"></video>
</p>

预览视频：[`assets/agibot_a3_retarget.mp4`](assets/agibot_a3_retarget.mp4)

## 安装

建议使用 Python 3.10 环境：

```bash
conda create -n gmr python=3.10 -y
conda activate gmr
pip install -e .
conda install -c conda-forge libstdcxx-ng -y
```

如果你只想快速验证 A3 重定向，安装完成后直接运行下面的命令即可。

## 快速开始

```bash
# LAFAN1 format
python scripts/bvh_to_robot.py \
  --bvh_file example_data/lafan1/run1_subject2.bvh \
  --robot agibot_a3 \
  --save_path outputs/lafan1-run1_subject2-gmr.pkl \
  --rate_limit \
  --format lafan1

# qingtong format
python scripts/bvh_to_robot.py \
  --bvh_file example_data/qingtong/3youzhiquan2.bvh \
  --robot agibot_a3 \
  --save_path outputs/qingtong-3youzhiquan2-gmr.pkl \
  --rate_limit \
  --format qingtong \
  --record_video --video_path outputs/qingtong-3youzhiquan2-gmr.mp4

```

运行成功后会生成：

```text
outputs/lafan1-run1_subject2-gmr.pkl
```
