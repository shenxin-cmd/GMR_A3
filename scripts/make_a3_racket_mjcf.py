from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path("/data/home/shenx/code_repositories/GMR_A3/assets/agibot_a3")
MESH_SRC = Path("/data/home/shenx/code_repositories/GMR/a3_31dof_rev_1_0_bundle/meshes")
MESH_DST = ROOT / "meshes"
BASE_XML = ROOT / "mjcf" / "a3_t2d0.xml"
RACKET_XML = ROOT / "mjcf" / "a3_t2d0_racket.xml"
SCENE_XML = ROOT / "mjcf" / "scene_floor_racket.xml"

for mesh_name in ["right_hand_pingpong_Link.STL", "pingpong_red_Link.STL", "pingpong_black_Link.STL"]:
    target = MESH_SRC / mesh_name
    link = MESH_DST / mesh_name
    if not link.exists():
        link.symlink_to(target)

tree = ET.parse(BASE_XML)
root = tree.getroot()
asset = root.find("asset")
if asset is None:
    raise RuntimeError("asset not found")

mesh_names = {
    "right_hand_pingpong_Link": "right_hand_pingpong_Link.STL",
    "pingpong_red_Link": "pingpong_red_Link.STL",
    "pingpong_black_Link": "pingpong_black_Link.STL",
}
existing_meshes = {mesh.attrib.get("name") for mesh in asset.findall("mesh")}
for name, file_name in mesh_names.items():
    if name not in existing_meshes:
        ET.SubElement(asset, "mesh", {"name": name, "content_type": "model/stl", "file": file_name})

for material in asset.findall("material"):
    rgba = material.attrib.get("rgba")
    if rgba:
        parts = rgba.split()
        if len(parts) == 4:
            parts[3] = "1"
            material.set("rgba", " ".join(parts))

for geom in root.iter("geom"):
    if geom.attrib.get("class") == "visual" and "rgba" in geom.attrib:
        parts = geom.attrib["rgba"].split()
        if len(parts) == 4:
            parts[3] = "1"
            geom.set("rgba", " ".join(parts))

target_body = None
for body in root.iter("body"):
    if body.attrib.get("name") == "right_wrist_yaw_Link":
        target_body = body
        break
if target_body is None:
    raise RuntimeError("right_wrist_yaw_Link not found")

for geom in list(target_body.findall("geom")):
    if geom.attrib.get("mesh") == "right_hand_palm_Link":
        target_body.remove(geom)

existing_geoms = {geom.attrib.get("mesh") for geom in target_body.findall("geom")}
if "right_hand_pingpong_Link" not in existing_geoms:
    target_body.append(
        ET.Element(
            "geom",
            {
                "class": "visual",
                "type": "mesh",
                "rgba": "1 1 1 1",
                "mesh": "right_hand_pingpong_Link",
            },
        )
    )
if "pingpong_red_Link" not in existing_geoms:
    target_body.append(
        ET.Element(
            "geom",
            {
                "class": "visual",
                "type": "mesh",
                "pos": "0.21021 0.032078 0.032036",
                "rgba": "1 0 0 1",
                "mesh": "pingpong_red_Link",
            },
        )
    )
if "pingpong_black_Link" not in existing_geoms:
    target_body.append(
        ET.Element(
            "geom",
            {
                "class": "visual",
                "type": "mesh",
                "pos": "0.21021 0.032078 0.032036",
                "rgba": "0.05 0.05 0.05 1",
                "mesh": "pingpong_black_Link",
            },
        )
    )

tree.write(RACKET_XML, encoding="unicode")

scene = SCENE_XML
scene.write_text(
    """<mujoco model=\"scene\">\n  <include file=\"a3_t2d0_racket.xml\"/>\n\n  <statistic center=\"1.0 0.7 1.5\" extent=\"0.8\"/>\n\n  <visual>\n    <map force=\"0.1\" fogend=\"20\" fogstart=\"10\" shadowclip=\"5\" />\n    <headlight diffuse=\"0.3 0.3 0.3\" ambient=\"0.3 0.3 0.3\" specular=\"0.9 0.9 0.9\"/>\n    <global offwidth=\"1280\" offheight=\"960\" azimuth=\"-140\" elevation=\"-20\"/>\n    <quality shadowsize=\"16384\"/>\n  </visual>\n\n  <asset>\n    <texture type=\"skybox\" builtin=\"gradient\" rgb1=\"0.9176 0.9216 0.9294\" rgb2=\"0.9176 0.9216 0.9294\" width=\"100\" height=\"100\"/>\n    <texture builtin=\"checker\" height=\"100\" width=\"100\" name=\"texplane\" rgb1=\"0.7490 0.8392 0.8353\" rgb2=\"0.7490 0.8392 0.8353\" type=\"2d\" mark=\"edge\" markrgb=\"1 1 1\"/>\n    <material name=\"MatPlane\" reflectance=\"0.0\" shininess=\"2\" specular=\"1\" texrepeat=\"120 120\" texture=\"texplane\"/>\n    <material name=\"MatCyclorama\" rgba=\"0.36 0.36 0.38 1\" reflectance=\"0\" specular=\"0.05\" shininess=\"0.1\"/>\n  </asset>\n\n  <worldbody>\n    <light pos=\"3.5 3 3.5\" dir=\"-1 -1 -1\" directional=\"true\"/>\n    <geom name=\"floor\" size=\"30 30 0.125\" type=\"plane\" conaffinity=\"7\" material=\"MatPlane\"/>\n  </worldbody>\n\n</mujoco>\n""",
    encoding="utf-8",
)
print(RACKET_XML)
print(SCENE_XML)
