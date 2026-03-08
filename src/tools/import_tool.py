"""Model import MCP tools."""

from fastmcp import FastMCP
from src.blender_ops.loader import import_glb
from src.storage import scene_exists


def register_import_tools(mcp: FastMCP):
    @mcp.tool()
    def import_model(scene_id: str, model_url: str, object_name: str) -> dict:
        """Import a GLB model into the scene from a URL.

        Downloads the GLB file and imports it into the Blender scene.
        Returns the object's bounding box dimensions for positioning.

        Args:
            scene_id: The scene ID from create_scene
            model_url: Presigned URL to download the GLB model
            object_name: Name for the imported object (e.g. "sofa", "table")

        Returns:
            Object name, bounding box dimensions, and initial position
        """
        if not scene_exists(scene_id):
            return {"error": f"Scene {scene_id} not found"}

        result = import_glb(scene_id, model_url, object_name)
        return result
