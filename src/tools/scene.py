"""Scene management MCP tools."""

import uuid
from fastmcp import FastMCP
from src.blender_ops.scene import create_new_scene, get_scene_objects
from src.storage import scene_exists


def register_scene_tools(mcp: FastMCP):
    @mcp.tool()
    def create_scene(name: str) -> dict:
        """Create a new empty Blender scene for composing 3D models.

        Args:
            name: Descriptive name for the scene (e.g. "living room")

        Returns:
            scene_id and status
        """
        scene_id = str(uuid.uuid4())
        create_new_scene(scene_id, name)
        return {"scene_id": scene_id, "name": name, "status": "created"}

    @mcp.tool()
    def list_objects(scene_id: str) -> dict:
        """List all objects in a scene with their transforms and bounding boxes.

        Args:
            scene_id: The scene ID from create_scene

        Returns:
            List of objects with position, rotation, scale, and bounds
        """
        if not scene_exists(scene_id):
            return {"error": f"Scene {scene_id} not found"}

        objects = get_scene_objects(scene_id)
        return {"scene_id": scene_id, "objects": objects}
