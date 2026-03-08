"""Blender GLB import operations."""

import json
import tempfile
import httpx
from src.storage import get_scene_path


def import_glb(scene_id: str, model_url: str, object_name: str) -> dict:
    """Download a GLB from URL and import it into the scene."""
    blend_path = str(get_scene_path(scene_id))

    # Download GLB to a temp file
    try:
        with tempfile.NamedTemporaryFile(suffix=".glb", delete=False) as tmp:
            tmp_path = tmp.name
            print(f"[import_glb] downloading from URL (length={len(model_url)}): {model_url[:150]}...")
            response = httpx.get(model_url, follow_redirects=True, timeout=60.0)
            if response.status_code != 200:
                return {
                    "error": f"Failed to download model: HTTP {response.status_code}",
                    "url_preview": model_url[:200],
                    "response_body": response.text[:300],
                }
            tmp.write(response.content)
            print(f"[import_glb] downloaded {len(response.content)} bytes to {tmp_path}")
    except Exception as e:
        return {"error": f"Download failed: {type(e).__name__}: {str(e)}"}

    script = f"""
import bpy
import json
import mathutils

# Import GLB
bpy.ops.import_scene.gltf(filepath={json.dumps(tmp_path)})

# Get the imported objects (newly added ones)
imported = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']

if not imported:
    # Sometimes GLTF imports as EMPTY with mesh children
    imported = [obj for obj in bpy.context.selected_objects]

# Rename the root imported object
root = imported[0] if imported else None
if root:
    root.name = {json.dumps(object_name)}

    # Calculate bounding box
    bbox = [root.matrix_world @ mathutils.Vector(corner) for corner in root.bound_box]
    min_corner = [min(v[i] for v in bbox) for i in range(3)]
    max_corner = [max(v[i] for v in bbox) for i in range(3)]
    dimensions = [max_corner[i] - min_corner[i] for i in range(3)]

    result = {{
        "object_name": root.name,
        "position": list(root.location),
        "bounds": {{
            "min": min_corner,
            "max": max_corner,
            "dimensions": dimensions,
        }},
    }}
else:
    result = {{"error": "No mesh objects imported"}}

# Save scene
bpy.ops.wm.save_mainfile(filepath={json.dumps(blend_path)})
print("IMPORT_JSON:" + json.dumps(result))
"""
    from src.blender_ops.scene import _run_blender_with_file
    import subprocess
    import os

    try:
        # Run with full output capture (don't raise on non-zero)
        blend_result = subprocess.run(
            ["blender", "--background", blend_path, "--python-expr", script],
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = blend_result.stdout
        stderr = blend_result.stderr

        # Log everything for debugging
        print(f"[import_glb] returncode: {blend_result.returncode}")
        if stderr:
            print(f"[import_glb] stderr (last 500 chars): {stderr[-500:]}")
        if output:
            print(f"[import_glb] stdout (last 500 chars): {output[-500:]}")
    except Exception as e:
        return {"error": f"Blender subprocess failed: {str(e)}"}

    # Clean up temp file
    try:
        os.unlink(tmp_path)
    except OSError:
        pass

    for line in output.split("\n"):
        if line.startswith("IMPORT_JSON:"):
            return json.loads(line[len("IMPORT_JSON:"):])

    return {
        "error": "Failed to parse import result",
        "returncode": blend_result.returncode,
        "stderr_tail": stderr[-300:] if stderr else "",
        "stdout_tail": output[-300:] if output else "",
    }
