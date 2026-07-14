from pathlib import Path

import mujoco as mj


paths = [
    Path("/data/home/shenx/code_repositories/GMR_A3/assets/agibot_a3_racket/a3_31dof_rev_1_0_mujoco.urdf"),
    Path("/data/home/shenx/code_repositories/GMR/a3_31dof_rev_1_0_bundle/a3_31dof_rev_1_0.urdf"),
    Path("/data/home/shenx/code_repositories/GMR_A3/assets/agibot_a3/mjcf/scene_floor.xml"),
]

for path in paths:
    print("===", path)
    try:
        model = mj.MjModel.from_xml_path(str(path))
    except Exception as exc:
        print("LOAD_ERROR", type(exc).__name__, exc)
        continue
    print("nq nv nu njnt nbody", model.nq, model.nv, model.nu, model.njnt, model.nbody)
    print("joints")
    for idx in range(model.njnt):
        print(idx, mj.mj_id2name(model, mj.mjtObj.mjOBJ_JOINT, idx), int(model.jnt_type[idx]))
    print("bodies")
    for idx in range(model.nbody):
        print(idx, mj.mj_id2name(model, mj.mjtObj.mjOBJ_BODY, idx))
    print("actuators")
    for idx in range(model.nu):
        print(idx, mj.mj_id2name(model, mj.mjtObj.mjOBJ_ACTUATOR, idx))
