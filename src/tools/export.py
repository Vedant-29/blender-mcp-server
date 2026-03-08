"""Scene export MCP tools."""

from fastmcp import FastMCP
from src.blender_ops.exporter import export_scene_glb
from src.storage import scene_exists, get_output_url


def register_export_tools(mcp: FastMCP):
    @mcp.tool()
    def export_scene(scene_id: str) -> dict:
        """Export the composed scene as a single GLB file.

        Merges all imported models with their current transforms into one GLB.
        Returns a URL to download the composed model.

        Args:
            scene_id: The scene ID from create_scene

        Returns:
            URL to the composed GLB file and object count
        """
        if not scene_exists(scene_id):
            return {"error": f"Scene {scene_id} not found"}

        result = export_scene_glb(scene_id)
        scene_url = get_output_url(scene_id)
        return {
            "scene_id": scene_id,
            "scene_url": scene_url,
            "object_count": result["object_count"],
            "status": "exported",
        }
