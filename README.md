# Agibot A3 Racket Retargeting README

本文档说明如何把 GVHMR 输出的人体运动重定位到带乒乓球拍的 Agibot A3 机器人，并录制可视化视频。当前流程输出的是 GMR `pkl` 参考运动文件，可作为后续回放、数据转换或训练参考运动的输入。

## 1. 环境与路径

远程项目目录：

```bash
cd /data/home/shenx/code_repositories/GMR_A3
```

推荐环境：

```bash
conda activate gmr
```

如果通过非交互命令运行，也可以使用：

```bash
/data/home/shenx/miniconda3/bin/conda run -n gmr <command>
```

当前带球拍 A3 的 robot 名称：

```text
agibot_a3_racket
```

对应 MuJoCo 模型：

```text
assets/agibot_a3/mjcf/scene_floor_racket.xml
```

IK 配置复用：

```text
general_motion_retargeting/ik_configs/smplx_to_agibot_a3.json
```

## 2. 重定位生成 pkl

示例命令：

```bash
cd /data/home/shenx/code_repositories/GMR_A3

python scripts/gvhmr_to_robot.py \
  --robot agibot_a3_racket \
  --gvhmr_pred_file /data/home/shenx/code_repositories/GVHMR/outputs/raw_batch/4/hmr4d_results.pt \
  --save_path ./agibot_a3_racket_with_human.pkl \
  --no_viewer
```

输出：

```text
./agibot_a3_racket_with_human.pkl
```

该 pkl 包含：

- `fps`: 运动帧率。
- `root_pos`: 机器人浮动基座位置，shape 为 `(T, 3)`。
- `root_rot`: 机器人浮动基座四元数，保存格式为 `xyzw`。
- `dof_pos`: 机器人 30 个关节位置，shape 为 `(T, 30)`。
- `human_motion_data`: 每帧输入人体专家数据，用于可视化人体局部坐标轴。

### 参数说明

`--robot`

指定目标机器人。带球拍 A3 使用：

```text
agibot_a3_racket
```

普通 A3 使用：

```text
agibot_a3
```

`--gvhmr_pred_file`

GVHMR 输出的 `hmr4d_results.pt` 文件路径。该文件来自视频到 SMPL/SMPLX 的人体运动估计。

`--save_path`

重定位结果保存路径。建议使用 `.pkl` 后缀。

`--no_viewer`

不打开 MuJoCo 可视化窗口，只离线计算并保存 pkl。远程服务器没有 `DISPLAY` 时推荐始终使用该参数。

`--ik_config_path`

可选参数，用于临时指定某个 IK 配置文件，不覆盖正式配置。例如调参时可以使用：

```bash
--ik_config_path general_motion_retargeting/ik_configs/calib_agibot_a3/s05_full_two_stage.json
```

## 3. 录制可视化 mp4

示例命令：

```bash
cd /data/home/shenx/code_repositories/GMR_A3

MUJOCO_GL=egl python scripts/vis_robot_motion.py \
  --robot agibot_a3_racket \
  --robot_motion_path ./agibot_a3_racket_with_human.pkl \
  --record_video \
  --no_viewer \
  --show_human_data \
  --align_feet_to_ground \
  --max_loops 1 \
  --video_path videos/agibot_a3_racket_opaque_human_ground.mp4 \
  --video_width 1280 \
  --video_height 720 \
  --camera_z_offset -0.35 \
  --human_frame_scale 0.16 \
  --human_frame_width 0.003
```

输出：

```text
videos/agibot_a3_racket_opaque_human_ground.mp4
```

### 参数说明

`MUJOCO_GL=egl`

启用 MuJoCo 离屏渲染。远程无显示器或无 `DISPLAY` 时录制 mp4 需要使用。

`--robot`

指定可视化机器人，应与 pkl 的目标机器人一致。带球拍 A3 使用：

```text
agibot_a3_racket
```

`--robot_motion_path`

要回放或录制的视频 pkl 路径。

`--record_video`

开启视频录制。

`--no_viewer`

不打开 GLFW 窗口，直接离屏渲染视频。远程服务器推荐使用。

`--show_human_data`

显示输入人体专家数据的局部坐标轴。去掉该参数则只显示机器人。

`--align_feet_to_ground`

根据左右 `ankle_roll` body 的高度自动给 root z 加偏移，使脚更接近地面。用于解决可视化中脚陷进地面的问题。

`--foot_body_ground_z`

脚贴地自动对齐的目标高度，默认 `0.04`。如果脚仍然陷地，可稍微增大：

```bash
--foot_body_ground_z 0.06
```

如果脚浮空，可减小：

```bash
--foot_body_ground_z 0.02
```

`--root_z_offset`

手动给机器人 root z 加偏移，单位是米。例如整体抬高 3 cm：

```bash
--root_z_offset 0.03
```

该参数可以和 `--align_feet_to_ground` 叠加使用。

`--max_loops`

视频循环次数。`1` 表示录制一遍动作，`3` 表示循环三遍。交互 viewer 模式下 `0` 表示无限循环。

`--video_path`

mp4 输出路径。

`--video_width` / `--video_height`

输出视频分辨率。

`--camera_z_offset`

相机 look-at 点在 z 方向的偏移，单位是米。负数表示相机视线往下移，更容易看到腿和脚。例如：

```bash
--camera_z_offset -0.35
```

如果腿仍然看不全，可改成：

```bash
--camera_z_offset -0.55
```

`--human_frame_scale`

人体局部坐标轴长度。当前推荐：

```bash
--human_frame_scale 0.16
```

如果坐标轴太长，可减小到 `0.10`。

`--human_frame_width`

人体局部坐标轴粗细。当前推荐：

```bash
--human_frame_width 0.003
```

如果坐标轴太细，可增大到 `0.005`。

## 4. 只看机器人，不显示人体坐标轴

去掉 `--show_human_data` 即可：

```bash
MUJOCO_GL=egl python scripts/vis_robot_motion.py \
  --robot agibot_a3_racket \
  --robot_motion_path ./agibot_a3_racket_with_human.pkl \
  --record_video \
  --no_viewer \
  --align_feet_to_ground \
  --max_loops 1 \
  --video_path videos/agibot_a3_racket_robot_only.mp4
```

## 5. 注意事项

1. `agibot_a3_racket` 当前主要用于可视化和 pkl 数据生成。IK 约束仍然跟踪右腕 `right_wrist`，球拍是挂在右手末端的可视化模型。
2. 如果后续需要更精确的击球动作，应增加球拍击球点或拍面方向约束，而不是只跟踪手腕。
3. 老版本 pkl 可能不包含 `human_motion_data`。如果需要显示人体专家坐标轴，请用新版 `gvhmr_to_robot.py` 重新生成 pkl。
4. `root_rot` 在 pkl 中保存为 `xyzw`，加载回 MuJoCo 时脚本会自动转成 `wxyz`。
5. `--align_feet_to_ground` 只影响可视化/录制阶段，不会修改原始 pkl。如果希望永久改变 pkl 的 root 高度，需要另写 pkl 后处理脚本。
