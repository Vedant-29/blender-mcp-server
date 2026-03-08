"""Blender MCP Server — HTTP MCP server with Blender headless for scene composition."""

import os
import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from src.storage import OUTPUT_DIR
from src.tools.scene import register_scene_tools
from src.tools.import_tool import register_import_tools
from src.tools.transform import register_transform_tools
from src.tools.physics import register_physics_tools
from src.tools.export import register_export_tools

# Create MCP server
mcp = FastMCP(
    name="blender",
    instructions=(
        "Blender MCP Server for 3D scene composition. "
        "Use create_scene to start, import_model to add GLBs, "
        "set_transform to arrange, run_physics for simulation, "
        "and export_scene to get the final composed GLB."
    ),
)

# Register all tools
register_scene_tools(mcp)
register_import_tools(mcp)
register_transform_tools(mcp)
register_physics_tools(mcp)
register_export_tools(mcp)

# Create Starlette app to serve both MCP and static output files
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = Starlette(
    routes=[
        # Serve exported GLBs as static files
        Mount("/output", app=StaticFiles(directory=str(OUTPUT_DIR)), name="output"),
    ],
)

# Mount MCP at /mcp
mcp_app = mcp.http_app(path="/mcp")
app.mount("/mcp", mcp_app)


@app.route("/health")
async def health(request):
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
