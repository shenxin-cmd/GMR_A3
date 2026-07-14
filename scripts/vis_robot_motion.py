import argparse
import os
import pathlib
import sys

import imageio
import mujoco as mj
import numpy as np
from scipy.spatial.transform import Rotation as R
from tqdm import tqdm

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from general_motion_retargeting import (
    ROBOT_BASE_DICT,
    ROBOT_XML_DICT,
    VIEWER_CAM_DISTANCE_DICT,
    RobotMotionViewer,
    load_robot_motion,
)


FOOT_BODY_NAMES = ("left_ankle_roll_Link", "right_ankle_roll_Link")


def compute_ground_z_offset(model, data, root_pos, root_rot, dof_pos, foot_body_ground_z):
    set_qpos(model, data, root_pos, root_rot, dof_pos, root_z_offset=0.0)
    foot_z = []
    for body_name in FOOT_BODY_NAMES:
        try:
            foot_z.append(float(data.xpos[model.body(body_name).id][2]))
        except KeyError:
            pass
    if not foot_z:
        return 0.0
    return foot_body_ground_z - min(foot_z)


def set_qpos(model, data, root_pos, root_rot, dof_pos, root_z_offset=0.0):
    data.qpos[:3] = root_pos
    data.qpos[2] += root_z_offset
    data.qpos[3:7] = root_rot
    data.qpos[7:] = dof_pos
    mj.mj_forward(model, data)


def camera_for_robot(model, data, robot_type, camera, z_offset):
    base_body = ROBOT_BASE_DICT[robot_type]
    camera.lookat = data.xpos[model.body(base_body).id].copy()
    camera.lookat[2] += z_offset
    camera.distance = VIEWER_CAM_DISTANCE_DICT[robot_type]
    camera.elevation = -10
    camera.azimuth = 180


def draw_frame_axes(scene, pos, quat, scale, width):
    mat = R.from_quat(quat, scalar_first=True).as_matrix()
    colors = (
        np.array([1.0, 0.0, 0.0, 1.0]),
        np.array([0.0, 1.0, 0.0, 1.0]),
        np.array([0.0, 0.2, 1.0, 1.0]),
    )
    for axis_idx, color in enumerate(colors):
        if scene.ngeom >= scene.maxgeom:
            return
        start = np.asarray(pos, dtype=float)
        end = start + scale * mat[:, axis_idx]
        geom = scene.geoms[scene.ngeom]
        mj.mjv_connector(
            geom,
            type=mj.mjtGeom.mjGEOM_ARROW,
            width=width,
            from_=start,
            to=end,
        )
        geom.rgba[:] = color
        scene.ngeom += 1


def draw_human_motion(scene, human_frame, scale, width):
    for pos, quat in human_frame.values():
        draw_frame_axes(scene, pos, quat, scale, width)


def record_headless(
    robot_type,
    root_pos,
    root_rot,
    dof_pos,
    fps,
    video_path,
    width,
    height,
    max_loops,
    camera_z_offset,
    human_motion_data=None,
    show_human_data=False,
    human_frame_scale=0.14,
    human_frame_width=0.004,
    root_z_offset=0.0,
    align_feet_to_ground=False,
    foot_body_ground_z=0.04,
):
    xml_path = ROBOT_XML_DICT[robot_type]
    model = mj.MjModel.from_xml_path(str(xml_path))
    data = mj.MjData(model)
    renderer = mj.Renderer(model, height=height, width=width)
    camera = mj.MjvCamera()
    ground_z_offset = 0.0
    if align_feet_to_ground:
        ground_z_offset = compute_ground_z_offset(
            model,
            data,
            root_pos[0],
            root_rot[0],
            dof_pos[0],
            foot_body_ground_z,
        )
        print(f"Ground alignment z offset: {ground_z_offset:.4f}")

    video_dir = os.path.dirname(video_path)
    if video_dir:
        os.makedirs(video_dir, exist_ok=True)

    total_frames = len(root_pos) * max_loops
    with imageio.get_writer(video_path, fps=fps) as writer:
        for idx in tqdm(range(total_frames), desc="Recording"):
            frame_idx = idx % len(root_pos)
            set_qpos(
                model,
                data,
                root_pos[frame_idx],
                root_rot[frame_idx],
                dof_pos[frame_idx],
                root_z_offset=root_z_offset + ground_z_offset,
            )
            camera_for_robot(model, data, robot_type, camera, camera_z_offset)
            renderer.update_scene(data, camera=camera)
            if show_human_data:
                if human_motion_data is None:
                    raise ValueError(
                        "Motion pkl does not contain human_motion_data. Re-run gvhmr_to_robot.py to regenerate it."
                    )
                draw_human_motion(renderer.scene, human_motion_data[frame_idx], human_frame_scale, human_frame_width)
            writer.append_data(renderer.render())

    print(f"Video saved to {video_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", type=str, default="unitree_g1")
    parser.add_argument("--robot_motion_path", type=str, required=True)
    parser.add_argument("--record_video", action="store_true")
    parser.add_argument("--video_path", type=str, default="videos/example.mp4")
    parser.add_argument("--video_width", type=int, default=1280)
    parser.add_argument("--video_height", type=int, default=720)
    parser.add_argument("--camera_z_offset", type=float, default=-0.35, help="Vertical look-at offset in meters.")
    parser.add_argument("--show_human_data", action="store_true", help="Draw input human expert local coordinate frames.")
    parser.add_argument("--human_frame_scale", type=float, default=0.14, help="Axis length for human frame visualization.")
    parser.add_argument("--human_frame_width", type=float, default=0.004, help="Axis arrow width for human frame visualization.")
    parser.add_argument("--root_z_offset", type=float, default=0.0, help="Manual vertical offset added to root position in meters.")
    parser.add_argument("--align_feet_to_ground", action="store_true", help="Lift/lower root so ankle roll bodies align to the ground.")
    parser.add_argument("--foot_body_ground_z", type=float, default=0.04, help="Target z for the lower ankle roll body when aligning.")
    parser.add_argument("--max_loops", type=int, default=0, help="0 means loop forever in viewer mode.")
    parser.add_argument("--no_viewer", action="store_true", help="Render offscreen without opening a GLFW viewer.")
    parser.add_argument("--no_rate_limit", action="store_true", help="Play as fast as possible in viewer mode.")

    args = parser.parse_args()

    if not os.path.exists(args.robot_motion_path):
        raise FileNotFoundError(f"Motion file {args.robot_motion_path} not found")

    motion_data, motion_fps, motion_root_pos, motion_root_rot, motion_dof_pos, _, _ = load_robot_motion(
        args.robot_motion_path
    )
    human_motion_data = motion_data.get("human_motion_data")

    no_viewer = args.no_viewer or (args.record_video and os.environ.get("DISPLAY") is None)
    if no_viewer:
        if not args.record_video:
            raise ValueError("--no_viewer requires --record_video because there is no interactive window.")
        max_loops = args.max_loops if args.max_loops > 0 else 1
        record_headless(
            args.robot,
            motion_root_pos,
            motion_root_rot,
            motion_dof_pos,
            motion_fps,
            args.video_path,
            args.video_width,
            args.video_height,
            max_loops,
            args.camera_z_offset,
            human_motion_data,
            args.show_human_data,
            args.human_frame_scale,
            args.human_frame_width,
            args.root_z_offset,
            args.align_feet_to_ground,
            args.foot_body_ground_z,
        )
    else:
        env = RobotMotionViewer(
            robot_type=args.robot,
            motion_fps=motion_fps,
            camera_follow=False,
            record_video=args.record_video,
            video_path=args.video_path,
            video_width=args.video_width,
            video_height=args.video_height,
        )

        frame_idx = 0
        loop_count = 0
        try:
            while True:
                env.step(
                    motion_root_pos[frame_idx],
                    motion_root_rot[frame_idx],
                    motion_dof_pos[frame_idx],
                    rate_limit=not args.no_rate_limit,
                )
                frame_idx += 1
                if frame_idx >= len(motion_root_pos):
                    frame_idx = 0
                    loop_count += 1
                    if args.max_loops > 0 and loop_count >= args.max_loops:
                        break
        finally:
            env.close()
