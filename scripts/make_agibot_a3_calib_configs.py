import copy
import json
from pathlib import Path


ROOT = Path("general_motion_retargeting/ik_configs")
SRC = ROOT / "smplx_to_agibot_a3.json"
OUT = ROOT / "calib_agibot_a3"


def load_config():
    with SRC.open("r") as f:
        return json.load(f)


def write_config(name, cfg):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.json"
    with path.open("w") as f:
        json.dump(cfg, f, indent=4)
        f.write("\n")
    print(path)


def one_stage(cfg, table):
    cfg = copy.deepcopy(cfg)
    cfg["use_ik_match_table1"] = True
    cfg["use_ik_match_table2"] = False
    cfg["ik_match_table1"] = table
    cfg["ik_match_table2"] = {}
    used_human_bodies = {entry[0] for entry in table.values()}
    cfg["human_scale_table"] = {
        name: scale
        for name, scale in cfg["human_scale_table"].items()
        if name in used_human_bodies
    }
    return cfg


def zero_rot(entry):
    entry = copy.deepcopy(entry)
    entry[2] = 0
    return entry


def zero_pos(entry):
    entry = copy.deepcopy(entry)
    entry[1] = 0
    return entry


base = load_config()
table = base["ik_match_table1"]

root_feet = {
    "pelvis_link": table["pelvis_link"],
    "left_ankle_roll_Link": table["left_ankle_roll_Link"],
    "right_ankle_roll_Link": table["right_ankle_roll_Link"],
}
write_config("s00_root_feet", one_stage(base, root_feet))

root_torso_feet = copy.deepcopy(root_feet)
root_torso_feet["torso_Link"] = table["torso_Link"]
root_torso_feet["head_yaw_Link"] = zero_rot(table["head_yaw_Link"])
write_config("s01_root_torso_feet", one_stage(base, root_torso_feet))

legs = copy.deepcopy(root_torso_feet)
for key in [
    "left_hip_yaw_Link",
    "left_knee_Link",
    "right_hip_yaw_Link",
    "right_knee_Link",
]:
    legs[key] = table[key]
write_config("s02_add_legs", one_stage(base, legs))

arms_pos_only = copy.deepcopy(legs)
for key in [
    "left_shoulder_yaw_Link",
    "left_elbow_Link",
    "left_wrist_yaw_Link",
    "right_shoulder_yaw_Link",
    "right_elbow_Link",
    "right_wrist_yaw_Link",
]:
    arms_pos_only[key] = zero_rot(table[key])
    arms_pos_only[key][1] = 5 if "wrist" not in key else 20
write_config("s03_arms_pos_only", one_stage(base, arms_pos_only))

full_table1 = one_stage(base, table)
write_config("s04_full_table1_only", full_table1)

full_two_stage = copy.deepcopy(base)
write_config("s05_full_two_stage", full_two_stage)
