from pathlib import Path
import xml.etree.ElementTree as ET


SRC = Path("/data/home/shenx/code_repositories/GMR/a3_31dof_rev_1_0_bundle/a3_31dof_rev_1_0.urdf")
DST_DIR = Path("/data/home/shenx/code_repositories/GMR_A3/assets/agibot_a3_racket")
DST = DST_DIR / "a3_31dof_rev_1_0_mujoco.urdf"

DST_DIR.mkdir(parents=True, exist_ok=True)

tree = ET.parse(SRC)
root = tree.getroot()

for joint in root.findall("joint"):
    axis = joint.find("axis")
    if axis is None:
        axis = ET.SubElement(joint, "axis")
    xyz = axis.attrib.get("xyz", "").strip()
    parts = xyz.split()
    if len(parts) != 3:
        axis.set("xyz", "0 0 1")
        continue
    try:
        vals = [float(part) for part in parts]
    except ValueError:
        axis.set("xyz", "0 0 1")
        continue
    if sum(abs(v) for v in vals) == 0:
        axis.set("xyz", "0 0 1")

tree.write(DST, encoding="UTF-8", xml_declaration=True)
print(DST)
