"""Blender rigid body physics simulation."""

import json
from src.storage import get_scene_path


def run_rigid_body_sim(
    scene_id: str,
    duration_seconds: float = 3.0,
    ground_plane: bool = True,
) -> dict:
    """Run rigid body simulation on all mesh objects in the scene."""
    blend_path = str(get_scene_path(scene_id))
    fps = 24
    frame_count = int(duration_seconds * fps)

    script = f"""
import bpy
import json
import mathutils

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = {frame_count}
scene.render.fps = {fps}

# Add ground plane if requested
ground = None
if {str(ground_plane)}:
    bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "__ground_plane__"
    # Make ground a passive rigid body
    bpy.context.view_layer.objects.active = ground
    bpy.ops.rigidbody.object_add(type='PASSIVE')
    ground.rigid_body.collision_shape = 'BOX'
    ground.rigid_body.friction = 0.8
    ground.rigid_body.restitution = 0.1

# Make all mesh objects active rigid bodies (except ground)
for obj in scene.objects:
    if obj.type != 'MESH' or obj.name == "__ground_plane__":
        continue
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.rigidbody.object_add(type='ACTIVE')
    obj.rigid_body.collision_shape = 'CONVEX_HULL'
    obj.rigid_body.mass = 1.0
    obj.rigid_body.friction = 0.5
    obj.rigid_body.restitution = 0.2
    obj.select_set(False)

# Bake physics
bpy.ops.ptcache.bake_all(bake=True)

# Advance to last frame to get settled positions
scene.frame_set({frame_count})

# Apply visual transform (freeze the simulation result)
results = []
for obj in scene.objects:
    if obj.type != 'MESH' or obj.name == "__ground_plane__":
        continue

    # Get the visual (simulated) location
    pos = list(obj.matrix_world.translation)
    results.append({{
        "name": obj.name,
        "position": pos,
    }})

# Apply visual transforms so positions are baked in
for obj in scene.objects:
    if obj.type != 'MESH' or obj.name == "__ground_plane__":
        continue
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.visual_transform_apply()
    # Remove rigid body after baking
    bpy.ops.rigidbody.object_remove()
    obj.select_set(False)

# Remove ground plane
if ground:
    bpy.data.objects.remove(ground, do_unlink=True)

# Remove rigid body world
if scene.rigidbody_world:
    bpy.ops.rigidbody.world_remove()

# Reset to frame 1
scene.frame_set(1)

# Save
bpy.ops.wm.save_mainfile(filepath={json.dumps(blend_path)})
print("PHYSICS_JSON:" + json.dumps({{"status": "completed", "object_positions": results}}))
"""
    from src.blender_ops.scene import _run_blender_with_file
    output = _run_blender_with_file(blend_path, script)

    for line in output.split("\n"):
        if line.startswith("PHYSICS_JSON:"):
            return json.loads(line[len("PHYSICS_JSON:"):])

    return {"error": "Failed to parse physics result"}
