from __future__ import annotations

import json
from pathlib import Path

from app.core.config import get_settings


def recipe_dir() -> Path:
    settings = get_settings()
    root = Path(settings.data_dir) / "recipes"
    root.mkdir(parents=True, exist_ok=True)
    return root


def load_recipe(university_slug: str | None) -> dict:
    root = recipe_dir()
    candidates = []
    if university_slug:
        candidates.append(root / f"{university_slug}.json")
    candidates.append(root / "generic.json")
    for c in candidates:
        if c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    return {"slug": "generic", "field_mappings": {}, "upload_mappings": {}, "selector_overrides": {}}


def list_recipes() -> list[str]:
    return sorted([p.name for p in recipe_dir().glob("*.json")])
