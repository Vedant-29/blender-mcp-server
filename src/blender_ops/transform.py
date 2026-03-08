"""Blender transform operations."""

import json
import math
from typing import Optional
from src.storage import get_scene_path


def set_object_transform(
    scene_id: str,
    object_name: str,
    position: Optional[list[float]] = None,
    rotation: Optional[list[float]] = None,
    scale: Optional[list[float]] = None,
) -> dict:
    """Set transform properties on a named object."""
    blend_path = str(get_scene_path(scene_id))

    pos_code = f"obj.location = {position}" if position else ""
    rot_code = (
        f"obj.rotation_euler = [{rotation[0]} * math.pi / 180, "
        f"{rotation[1]} * math.pi / 180, "
        f"{rotation[2]} * math.pi / 180]"
        if rotation
        else ""
    )
    scale_code = f"obj.scale = {scale}" if scale else ""

    script = f"""
import bpy
import json
import math

obj = bpy.data.objects.get({json.dumps(object_name)})
if obj is None:
    print("TRANSFORM_JSON:" + json.dumps({{"error": "Object not found: " + {json.dumps(object_name)}}}))
else:
    {pos_code}
    {rot_code}
    {scale_code}

    result = {{
        "object_name": obj.name,
        "position": list(obj.location),
        "rotation": [math.degrees(r) for r in obj.rotation_euler],
        "scale": list(obj.scale),
    }}

    bpy.ops.wm.save_mainfile(filepath={json.dumps(blend_path)})
    print("TRANSFORM_JSON:" + json.dumps(result))
"""
    from src.blender_ops.scene import _run_blender_with_file
    output = _run_blender_with_file(blend_path, script)

    for line in output.split("\n"):
        if line.startswith("TRANSFORM_JSON:"):
            return json.loads(line[len("TRANSFORM_JSON:"):])

    return {"error": "Failed to parse transform result"}
