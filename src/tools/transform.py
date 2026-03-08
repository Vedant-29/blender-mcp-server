"""Transform MCP tools."""

from typing import Optional
from fastmcp import FastMCP
from src.blender_ops.transform import set_object_transform
from src.storage import scene_exists


def register_transform_tools(mcp: FastMCP):
    @mcp.tool()
    def set_transform(
        scene_id: str,
        object_name: str,
        position: Optional[list[float]] = None,
        rotation: Optional[list[float]] = None,
        scale: Optional[list[float]] = None,
    ) -> dict:
        """Set the position, rotation, and/or scale of an object in the scene.

        Args:
            scene_id: The scene ID from create_scene
            object_name: Name of the object to transform
            position: [x, y, z] position in meters. Y is up.
            rotation: [x, y, z] rotation in degrees
            scale: [x, y, z] scale factors (1.0 = original size)

        Returns:
            Updated transform of the object
        """
        if not scene_exists(scene_id):
            return {"error": f"Scene {scene_id} not found"}

        result = set_object_transform(scene_id, object_name, position, rotation, scale)
        return result
