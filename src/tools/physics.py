"""Physics simulation MCP tools."""

from fastmcp import FastMCP
from src.blender_ops.physics import run_rigid_body_sim
from src.storage import scene_exists


def register_physics_tools(mcp: FastMCP):
    @mcp.tool()
    def run_physics(
        scene_id: str,
        duration_seconds: float = 3.0,
        ground_plane: bool = True,
    ) -> dict:
        """Run rigid body physics simulation to naturally settle objects.

        Objects will fall under gravity and collide with each other and the ground.
        Useful for making objects sit naturally on surfaces.

        Args:
            scene_id: The scene ID from create_scene
            duration_seconds: How long to simulate (1-5 seconds recommended)
            ground_plane: Whether to add an invisible ground plane at Y=0

        Returns:
            Final positions of all objects after simulation
        """
        if not scene_exists(scene_id):
            return {"error": f"Scene {scene_id} not found"}

        result = run_rigid_body_sim(scene_id, duration_seconds, ground_plane)
        return result
