from __future__ import annotations

import platform
from pathlib import Path


class DesktopFallbackExecutor:
    """Windows desktop fallback for native file picker or unreachable controls."""

    def __init__(self) -> None:
        self.available = platform.system().lower().startswith("win")

    def upload_via_native_dialog(self, file_path: str, target_window_title: str | None = None) -> dict:
        if not self.available:
            return {"used": False, "reason": "desktop fallback only enabled on Windows"}
        path = Path(file_path)
        if not path.exists():
            return {"used": False, "reason": f"file not found: {file_path}"}
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception:
            return {"used": False, "reason": "pywinauto not installed"}

        # MVP safety check: only interact with recognized file-open dialogs.
        try:
            desktop = Desktop(backend="uia")
            candidates = desktop.windows(title_re=".*(Open|File Upload|Choose File).*", visible_only=True)
            if not candidates:
                return {"used": False, "reason": "no native file dialog detected"}
            dialog = candidates[0]
            if target_window_title and target_window_title.lower() not in dialog.window_text().lower():
                return {"used": False, "reason": "target window mismatch"}

            dialog.set_focus()
            dialog.type_keys(str(path), with_spaces=True)
            dialog.type_keys("{ENTER}")
            return {"used": True, "reason": "native file picker handled"}
        except Exception as exc:
            return {"used": False, "reason": str(exc)}
