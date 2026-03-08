"""Local disk storage for scene .blend files and exported GLBs."""

import os
from pathlib import Path

SCENES_DIR = Path(os.environ.get("SCENES_DIR", "/app/scenes"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/app/output"))
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")


def get_scene_path(scene_id: str) -> Path:
    """Get the .blend file path for a scene."""
    scene_dir = SCENES_DIR / scene_id
    scene_dir.mkdir(parents=True, exist_ok=True)
    return scene_dir / "scene.blend"


def get_output_path(scene_id: str, filename: str = "composed.glb") -> Path:
    """Get the output file path for an exported scene."""
    output_dir = OUTPUT_DIR / scene_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / filename


def get_output_url(scene_id: str, filename: str = "composed.glb") -> str:
    """Get the public URL for an exported file."""
    return f"{BASE_URL}/output/{scene_id}/{filename}"


def scene_exists(scene_id: str) -> bool:
    """Check if a scene .blend file exists."""
    return get_scene_path(scene_id).exists()
