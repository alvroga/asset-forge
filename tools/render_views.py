# Headless Blender: render 4 views (front, right, back, left) of a GLB into one folder.
#   /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/render_views.py -- in.glb outdir [res]
import sys, math, bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
glb, outdir = argv[0], argv[1]
res = int(argv[2]) if len(argv) > 2 else 640

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector((min(p[i] for p in pts) for i in range(3)))
hi = Vector((max(p[i] for p in pts) for i in range(3)))
center, size = (lo + hi) / 2, max((hi - lo).length, 1e-3)

scene = bpy.context.scene
engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
scene.render.resolution_x = scene.render.resolution_y = res
scene.world = bpy.data.worlds.new("w"); scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.62, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(50), 0, math.radians(30)); scene.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam

for i, name in enumerate(["front", "right", "back", "left"]):
    a = math.radians(90 * i)
    cam.location = center + Vector((math.sin(a), -math.cos(a), 0.45)) * size * 1.5
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = f"{outdir}/{name}.png"
    bpy.ops.render.render(write_still=True)
