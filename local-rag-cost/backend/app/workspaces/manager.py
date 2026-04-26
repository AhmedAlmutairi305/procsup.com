from pathlib import Path


def workspace_dir(workspace_id: str) -> Path:
    path = Path("data") / "workspaces" / workspace_id
    path.mkdir(parents=True, exist_ok=True)
    return path
