import argparse
import pickle

import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()

with open(args.path, "rb") as f:
    data = pickle.load(f)

root_rot = data["root_rot"]
dof = data["dof_pos"]
quat_norm = np.linalg.norm(root_rot, axis=1)
dof_step = np.abs(np.diff(dof, axis=0))

print("fps", data["fps"])
print("frames", len(root_rot))
print("root_pos_shape", data["root_pos"].shape)
print("root_rot_shape", root_rot.shape)
print("dof_pos_shape", dof.shape)
print("has_nan", bool(np.isnan(data["root_pos"]).any() or np.isnan(root_rot).any() or np.isnan(dof).any()))
print("quat_norm_minmax", float(quat_norm.min()), float(quat_norm.max()))
print("dof_minmax", float(dof.min()), float(dof.max()))
print("dof_step_max", float(dof_step.max()) if len(dof_step) else 0.0)
print("dof_step_p99", float(np.quantile(dof_step, 0.99)) if len(dof_step) else 0.0)
