"""Blender scene management operations."""

import subprocess
import json
from src.storage import get_scene_path


def _run_blender_script(script: str) -> str:
    """Run a Python script inside Blender headless and return stdout."""
    result = subprocess.run(
        ["blender", "--background", "--python-expr", script],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Blender script failed: {result.stderr}")
    return result.stdout


def _run_blender_with_file(blend_path: str, script: str) -> str:
    """Run a Python script inside Blender with an existing .blend file."""
    result = subprocess.run(
        ["blender", "--background", blend_path, "--python-expr", script],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Blender script failed: {result.stderr}")
    return result.stdout


def create_new_scene(scene_id: str, name: str) -> None:
    """Create a new empty .blend scene and save it."""
    blend_path = str(get_scene_path(scene_id))
    script = f"""
import bpy

# Clear default scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Set scene name
bpy.context.scene.name = {json.dumps(name)}

# Set up basic scene settings
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# Save
bpy.ops.wm.save_as_mainfile(filepath={json.dumps(blend_path)})
print("SCENE_CREATED")
"""
    _run_blender_script(script)


def get_scene_objects(scene_id: str) -> list[dict]:
    """List all mesh objects in the scene with transforms and bounds."""
    blend_path = str(get_scene_path(scene_id))
    script = """
import bpy
import json
import mathutils

objects = []
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue

    # Get world-space bounding box
    bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    min_corner = [min(v[i] for v in bbox) for i in range(3)]
    max_corner = [max(v[i] for v in bbox) for i in range(3)]
    dimensions = [max_corner[i] - min_corner[i] for i in range(3)]

    objects.append({
        "name": obj.name,
        "position": list(obj.location),
        "rotation": [r for r in obj.rotation_euler],
        "scale": list(obj.scale),
        "bounds": {
            "min": min_corner,
            "max": max_corner,
            "dimensions": dimensions,
        },
    })

print("OBJECTS_JSON:" + json.dumps(objects))
"""
    output = _run_blender_with_file(blend_path, script)
    for line in output.split("\n"):
        if line.startswith("OBJECTS_JSON:"):
            return json.loads(line[len("OBJECTS_JSON:"):])
    return []
