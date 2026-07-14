import mujoco as mj
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from general_motion_retargeting import GeneralMotionRetargeting
from general_motion_retargeting.params import ROBOT_XML_DICT


robot = "agibot_a3_racket"
path = ROBOT_XML_DICT[robot]
model = mj.MjModel.from_xml_path(str(path))
print("xml", path)
print("nq nv nu nbody", model.nq, model.nv, model.nu, model.nbody)
print("has right_wrist_yaw_Link", model.body("right_wrist_yaw_Link").id)
print("has pelvis_link", model.body("pelvis_link").id)
retarget = GeneralMotionRetargeting(src_human="smplx", tgt_robot=robot, actual_human_height=1.8, verbose=False)
print("retarget_ok", retarget.model.nq, retarget.model.nv, len(retarget.tasks1), len(retarget.tasks2))
