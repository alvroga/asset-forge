# Auto-rig an A-pose humanoid GLB with a lean deform skeleton, add idle + walk, export GLB, render checks.
#   Blender -b -P tools/rig_humanoid.py -- in.glb outdir [--name NAME]
# Writes: outdir/rigged.glb, outdir/rig_report.json, outdir/debug_joints.png, outdir/walk_*.png
# Convention after glTF import: character faces -Y, Z up, character's LEFT is +X.
import sys, math, json, bpy, bmesh
from mathutils import Vector, Quaternion, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
glb, outdir = argv[0], argv[1]
report = {"warnings": []}


def warn(msg):
    print("WARN", msg); report["warnings"].append(msg)


# ---------- import & normalise ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb, merge_vertices=True)  # UV-seam splits would break bone-heat weighting
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in meshes:
    o.parent = None if o.parent is None else o.parent
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
if len(meshes) > 1:
    bpy.ops.object.join()
mesh = bpy.context.view_layer.objects.active
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=1e-5)  # exported GLB is triangle soup; bone heat needs a connected mesh
bpy.ops.object.mode_set(mode="OBJECT")
for o in list(bpy.context.scene.objects):
    if o.type != "MESH":
        bpy.data.objects.remove(o, do_unlink=True)

V = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
zmin, zmax = min(v.z for v in V), max(v.z for v in V)
H = zmax - zmin
# stand the feet on z=0
mesh.location.z -= zmin
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=True)
V = [v - Vector((0, 0, zmin)) for v in V]
xc = (min(v.x for v in V) + max(v.x for v in V)) / 2
report["height"] = H


# ---------- joint detection from silhouette ----------
def slab(z0, z1):
    return [v for v in V if z0 <= v.z < z1]


def width(z0, z1):
    s = slab(z0, z1)
    return (max(v.x for v in s) - min(v.x for v in s)) if s else 0.0


N = 100
step = H / N
prof = [width(i * step, (i + 1) * step) for i in range(N)]

# crotch: scan down from 55% height for the first slab where there is a gap at x~xc
def has_gap(z0, z1, half=0.02 * H):
    s = slab(z0, z1)
    return bool(s) and not any(abs(v.x - xc) < half for v in s)

crotch_z = 0.45 * H
# the crotch is the top of the highest slab (below 60% height) that still has a gap between the legs
gaps = [i for i in range(1, int(0.60 * N)) if has_gap(i * step, (i + 1) * step)]
if gaps:
    # contiguous run of gap slabs ending at the top
    top = max(gaps)
    crotch_z = (top + 1) * step
else:
    warn("no leg gap found; crotch at 45% height")

# neck: narrowest slab between 72% and 92% height
cand = range(int(0.72 * N), int(0.92 * N))
neck_i = min(cand, key=lambda i: prof[i] if prof[i] > 0 else 9e9)
neck_z = (neck_i + 0.5) * step
neck_w = prof[neck_i]
head_top = zmax - zmin

# arms: hand tips = extreme +-x vertices at/above the crotch
def tip(sign):
    s = [v for v in V if v.z > crotch_z]
    return max(s, key=lambda v: sign * (v.x - xc))

hand_L, hand_R = tip(+1), tip(-1)

# shoulder height: just under the neck; shoulder x = torso half-width at that height
sh_z = neck_z - 0.07 * H
torso_half = max(width(sh_z - step, sh_z + step) / 2, neck_w / 2)
arm_len_x = hand_L.x - xc

# torso half-width at chest height excluding arms: use width at 'neck+' region is head. Use median x spread of central 40% verts
chest_s = [v for v in slab(sh_z - 3 * step, sh_z) if abs(v.x - xc) < arm_len_x * 0.55]
if chest_s:
    torso_half = max(abs(v.x - xc) for v in chest_s)
torso_half = min(torso_half, arm_len_x * 0.6)

# feet: lowest slabs; toe direction is -Y (character faces -Y); leg centres at crotch
def leg_center(sign):
    s = [v for v in slab(crotch_z - 4 * step, crotch_z) if sign * (v.x - xc) > 0]
    return sum(v.x for v in s) / len(s) if s else xc + sign * 0.06 * H

legx_L, legx_R = leg_center(+1), leg_center(-1)
body_y = sum(v.y for v in slab(0.3 * H, 0.6 * H)) / max(1, len(slab(0.3 * H, 0.6 * H)))
foot_s = slab(0, 0.04 * H)
toe_y = min(v.y for v in foot_s) if foot_s else body_y - 0.08 * H

ankle_z = 0.06 * H
hips_z = crotch_z + 0.03 * H
spine_z = hips_z + (sh_z - hips_z) * 0.35
chest_z = hips_z + (sh_z - hips_z) * 0.75
head_z = neck_z + 0.01 * H


def P(x, z, y=None):
    return Vector((x, body_y if y is None else y, z))


J = {}
J["Hips"] = P(xc, hips_z)
J["Spine"] = P(xc, spine_z)
J["Chest"] = P(xc, chest_z)
J["Neck"] = P(xc, neck_z)
J["Head"] = P(xc, head_z)
J["HeadTop"] = P(xc, zmax - zmin)
for side, sgn, hand, legx in (("L", +1, hand_L, legx_L), ("R", -1, hand_R, legx_R)):
    shoulder = P(xc + sgn * torso_half, sh_z)
    wrist_pos = Vector((hand.x - sgn * 0.09 * H, hand.y, hand.z + 0.0))
    # keep wrist between shoulder and the hand tip
    elbow = (shoulder + wrist_pos) / 2
    J[f"Clavicle.{side}"] = P(xc + sgn * 0.02 * H, sh_z + 0.01 * H)
    J[f"UpperArm.{side}"] = shoulder
    J[f"LowerArm.{side}"] = elbow
    J[f"Hand.{side}"] = wrist_pos
    J[f"HandEnd.{side}"] = hand.copy()
    hip = P(legx, hips_z)
    ankle = P(legx, ankle_z, body_y)
    knee = (hip + ankle) / 2
    knee.y -= 0.01 * H  # slight forward knee bias for stable IK-ish solve
    J[f"UpperLeg.{side}"] = hip
    J[f"LowerLeg.{side}"] = knee
    J[f"Foot.{side}"] = ankle
    J[f"Toe.{side}"] = P(legx, 0.02 * H, toe_y + 0.3 * abs(toe_y - body_y))
    J[f"ToeEnd.{side}"] = P(legx, 0.02 * H, toe_y)
report["joints"] = {k: [round(c, 4) for c in v] for k, v in J.items()}

# ---------- armature ----------
arm_data = bpy.data.armatures.new("Armature")
arm = bpy.data.objects.new("Armature", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones

chain = [  # (name, head joint, tail joint, parent)
    ("Hips", "Hips", "Spine", None),
    ("Spine", "Spine", "Chest", "Hips"),
    ("Chest", "Chest", "Neck", "Spine"),
    ("Neck", "Neck", "Head", "Chest"),
    ("Head", "Head", "HeadTop", "Neck"),
]
for s in ("L", "R"):
    chain += [
        (f"Clavicle.{s}", f"Clavicle.{s}", f"UpperArm.{s}", "Chest"),
        (f"UpperArm.{s}", f"UpperArm.{s}", f"LowerArm.{s}", f"Clavicle.{s}"),
        (f"LowerArm.{s}", f"LowerArm.{s}", f"Hand.{s}", f"UpperArm.{s}"),
        (f"Hand.{s}", f"Hand.{s}", f"HandEnd.{s}", f"LowerArm.{s}"),
        (f"UpperLeg.{s}", f"UpperLeg.{s}", f"LowerLeg.{s}", "Hips"),
        (f"LowerLeg.{s}", f"LowerLeg.{s}", f"Foot.{s}", f"UpperLeg.{s}"),
        (f"Foot.{s}", f"Foot.{s}", f"Toe.{s}", f"LowerLeg.{s}"),
        (f"Toe.{s}", f"Toe.{s}", f"ToeEnd.{s}", f"Foot.{s}"),
    ]
for name, hj, tj, parent in chain:
    b = eb.new(name)
    b.head, b.tail = J[hj], J[tj]
    if (b.tail - b.head).length < 1e-4:
        b.tail = b.head + Vector((0, 0, 0.01))
    if parent:
        b.parent = eb[parent]
        b.use_connect = (b.parent.tail - b.head).length < 1e-4
bpy.ops.object.mode_set(mode="OBJECT")

# ---------- skin ----------
bpy.ops.object.select_all(action="DESELECT")
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
try:
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e:
    warn(f"auto weights failed ({e}); falling back to envelope weights")
    bpy.ops.object.parent_set(type="ARMATURE_ENVELOPE")
unweighted = sum(1 for v in mesh.data.vertices if not any(g.weight > 0.001 for g in v.groups))
report["verts"] = len(mesh.data.vertices)
report["unweighted_verts"] = unweighted
if unweighted:
    warn(f"{unweighted} vertices have no weights")


# ---------- animation ----------
def wq(bone_name, axis_world, angle):
    """Local pose rotation that rotates bone about a WORLD/armature-space axis."""
    b = arm.data.bones[bone_name]
    ax = b.matrix_local.to_3x3().inverted() @ Vector(axis_world)
    return Quaternion(ax.normalized(), angle)


bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)


def key(frame, pose):
    for pb in arm.pose.bones:
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))
    for name, (axis, ang) in pose.items():
        arm.pose.bones[name].rotation_quaternion = wq(name, axis, math.radians(ang))
    for pb in arm.pose.bones:
        pb.keyframe_insert("rotation_quaternion", frame=frame)


def new_action(name):
    a = bpy.data.actions.new(name)
    arm.animation_data_create().action = a
    return a


# NOTE on sign: rotating a down-pointing bone about +X swings it toward +Y (backwards, since character faces -Y).
# So forward swing of a leg/arm = NEGATIVE angle about X. Knees bend by swinging the shin backwards = POSITIVE.
idle = new_action("Idle")
key(1, {"Chest": (X, 0), "Head": (X, 0), "UpperArm.L": (Y, 0)})
key(25, {"Chest": (X, -2), "Head": (X, 2), "Spine": (X, -1)})
key(49, {"Chest": (X, 0), "Head": (X, 0), "UpperArm.L": (Y, 0)})

walk = new_action("Walk")
def wpose(ph):  # ph in [0,1)
    s = math.sin(2 * math.pi * ph)
    c = math.cos(2 * math.pi * ph)
    thigh = 28
    p = {
        "UpperLeg.L": (X, -thigh * s), "UpperLeg.R": (X, thigh * s),
        "LowerLeg.L": (X, max(0, 35 * math.sin(2 * math.pi * ph + 1.3))), "LowerLeg.R": (X, max(0, 35 * math.sin(2 * math.pi * ph + 1.3 + math.pi))),
        "UpperArm.L": (X, 22 * s), "UpperArm.R": (X, -22 * s),
        "LowerArm.L": (X, -15 - 8 * c), "LowerArm.R": (X, -15 + 8 * c),
        "Spine": (Z, 4 * s), "Chest": (Z, -4 * s), "Hips": (Z, 3 * s),
    }
    return p
for i in range(0, 25):
    key(1 + i, wpose(i / 24))
bpy.ops.object.mode_set(mode="OBJECT")
arm.animation_data.action = walk
walk.use_fake_user = idle.use_fake_user = True
arm.animation_data.action = None

# ---------- export ----------
bpy.ops.object.select_all(action="DESELECT")
mesh.select_set(True); arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=f"{outdir}/rigged.glb", export_format="GLB", use_selection=True,
                          export_animations=True, export_animation_mode="ACTIONS", export_skins=True,
                          export_force_sampling=True)

# ---------- debug renders ----------
scene = bpy.context.scene
engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
scene.render.resolution_x = scene.render.resolution_y = 640
scene.world = bpy.data.worlds.new("w"); scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.62, 1)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(50), 0, math.radians(30)); scene.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
center = Vector((xc, body_y, H / 2))


def shoot(path, az):
    a = math.radians(az)
    cam.location = center + Vector((math.sin(a), -math.cos(a), 0.1)) * H * 2.2
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


# joint markers + bone lines, x-ray, front view
bm = bmesh.new()
vm = {}
for k, v in J.items():
    vm[k] = bm.verts.new(v)
for name, hj, tj, parent in chain:
    bm.edges.new((vm[hj], vm[tj]))
for k, v in J.items():
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.02 * H, matrix=Matrix.Translation(v))
mk_mesh = bpy.data.meshes.new("markers"); bm.to_mesh(mk_mesh); bm.free()
mk = bpy.data.objects.new("markers", mk_mesh); scene.collection.objects.link(mk)
wf = mk.modifiers.new("wf", "WIREFRAME"); wf.thickness = 0.008 * H; wf.use_boundary = True
mat = bpy.data.materials.new("red"); mat.diffuse_color = (1, 0.1, 0.1, 1); mk.data.materials.append(mat)
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"; scene.display.shading.color_type = "TEXTURE"
scene.display.shading.show_xray = True; scene.display.shading.xray_alpha = 0.35
shoot(f"{outdir}/debug_joints.png", 0)
shoot(f"{outdir}/debug_joints_side.png", 90)
mk.hide_render = True
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
# walk poses seen from the side (+X), at 4 phases
arm.animation_data.action = walk
for ph, f in ((0, 1), (6, 7), (12, 13), (18, 19)):
    scene.frame_set(f)
    shoot(f"{outdir}/walk_{ph:02d}.png", 90)
(open(f"{outdir}/rig_report.json", "w")).write(json.dumps(report, indent=2))
print("RIG DONE", json.dumps({k: v for k, v in report.items() if k != "joints"}))
