"""Blender GLB export operations."""

import json
from src.storage import get_scene_path, get_output_path


def export_scene_glb(scene_id: str) -> dict:
    """Export the entire scene as a single GLB file."""
    blend_path = str(get_scene_path(scene_id))
    output_path = str(get_output_path(scene_id, "composed.glb"))

    script = f"""
import bpy
import json

# Select all mesh objects for export
mesh_count = 0
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
        mesh_count += 1
    else:
        obj.select_set(False)

# Export as GLB
bpy.ops.export_scene.gltf(
    filepath={json.dumps(output_path)},
    export_format='GLB',
    use_selection=False,  # Export entire scene
    export_apply=True,    # Apply modifiers
    export_animations=False,
)

print("EXPORT_JSON:" + json.dumps({{"object_count": mesh_count, "output_path": {json.dumps(output_path)}}}))
"""
    from src.blender_ops.scene import _run_blender_with_file
    output = _run_blender_with_file(blend_path, script)

    for line in output.split("\n"):
        if line.startswith("EXPORT_JSON:"):
            return json.loads(line[len("EXPORT_JSON:"):])

    return {"error": "Failed to parse export result"}
