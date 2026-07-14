import pickle
import numpy as np


path = "/data/home/shenx/code_repositories/GMR_A3/agibot_a3_racket_with_human.pkl"
with open(path, "rb") as f:
    data = pickle.load(f)

human = data["human_motion_data"]
for body in ["pelvis", "spine3", "right_wrist", "left_wrist", "left_foot", "right_foot"]:
    quats = np.array([frame[body][1] for frame in human])
    variation = np.max(np.abs(quats - quats[0]), axis=0)
    print(body, variation.tolist())
