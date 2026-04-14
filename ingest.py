from __future__ import annotations

import csv
import json
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

import docx
import fitz  # PyMuPDF
from PIL import Image

from config import Settings
from utils import normalize_text, sha1_file


TEXT_EXTENSIONS = {".txt", ".md", ".tex", ".py", ".json", ".csv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass
class DocumentUnit:
    doc_id: str
    file_path: str
    file_type: str
    modified_time: float
    file_hash: str
    page_number: Optional[int]
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)


class Ingestor:
    def __init__(self, settings: Settings):
        self.settings = settings

    def scan_paths(self, paths: List[str]) -> List[Path]:
        discovered: List[Path] = []
        for raw in paths:
            p = Path(raw).expanduser().resolve()
            if not p.exists():
                continue
            if p.is_file() and self._is_supported(p):
                discovered.append(p)
            elif p.is_dir():
                for f in p.rglob("*"):
                    if not f.is_file():
                        continue
                    if not self.settings.include_hidden_files and any(part.startswith(".") for part in f.parts):
                        continue
                    if self._is_supported(f):
                        discovered.append(f)
        return sorted(set(discovered))

    def ingest_paths(self, paths: List[str]) -> List[DocumentUnit]:
        units: List[DocumentUnit] = []
        for file_path in self.scan_paths(paths):
            units.extend(self._ingest_file(file_path))
        return units

    def _is_supported(self, p: Path) -> bool:
        return p.suffix.lower() in self.settings.supported_extensions

    def _ingest_file(self, path: Path) -> List[DocumentUnit]:
        ext = path.suffix.lower()
        mtime = path.stat().st_mtime
        file_hash = sha1_file(path)

        if ext in TEXT_EXTENSIONS:
            text = self._read_text_file(path, ext)
            return [self._make_unit(path, ext, mtime, file_hash, text)] if text else []
        if ext == ".pdf":
            return self._read_pdf(path, mtime, file_hash)
        if ext == ".docx":
            text = self._read_docx(path)
            return [self._make_unit(path, ext, mtime, file_hash, text)] if text else []
        if ext in IMAGE_EXTENSIONS:
            text = self._image_descriptor(path)
            meta = {"mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream"}
            return [self._make_unit(path, ext, mtime, file_hash, text, metadata=meta)]

        return []

    def _make_unit(
        self,
        path: Path,
        ext: str,
        mtime: float,
        file_hash: str,
        text: str,
        page_number: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> DocumentUnit:
        doc_id = f"{path.as_posix()}::{page_number if page_number is not None else 'full'}::{file_hash[:10]}"
        return DocumentUnit(
            doc_id=doc_id,
            file_path=path.as_posix(),
            file_type=ext,
            modified_time=mtime,
            file_hash=file_hash,
            page_number=page_number,
            text=normalize_text(text),
            metadata=metadata or {},
        )

    def _read_text_file(self, path: Path, ext: str) -> str:
        if ext == ".json":
            try:
                return json.dumps(json.loads(path.read_text(encoding="utf-8", errors="ignore")), indent=2)
            except json.JSONDecodeError:
                return path.read_text(encoding="utf-8", errors="ignore")

        if ext == ".csv":
            rows: List[str] = []
            with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    rows.append(", ".join(row))
                    if i > 5000:
                        break
            return "\n".join(rows)

        return path.read_text(encoding="utf-8", errors="ignore")

    def _read_pdf(self, path: Path, mtime: float, file_hash: str) -> List[DocumentUnit]:
        units: List[DocumentUnit] = []
        with fitz.open(path.as_posix()) as pdf:
            for i, page in enumerate(pdf):
                text = page.get_text("text") or ""
                if text.strip():
                    units.append(
                        self._make_unit(path, ".pdf", mtime, file_hash, text, page_number=i + 1)
                    )

                # Register image references per page for vision mode later.
                image_list = page.get_images(full=True)
                if image_list:
                    idx_text = f"[Page {i + 1}] Contains {len(image_list)} embedded image(s)."
                    units.append(
                        self._make_unit(
                            path,
                            ".pdf",
                            mtime,
                            file_hash,
                            idx_text,
                            page_number=i + 1,
                            metadata={"has_images": "true"},
                        )
                    )
        return units

    def _read_docx(self, path: Path) -> str:
        d = docx.Document(path.as_posix())
        parts = [p.text for p in d.paragraphs if p.text.strip()]
        return "\n".join(parts)

    def _image_descriptor(self, path: Path) -> str:
        with Image.open(path.as_posix()) as img:
            w, h = img.size
            mode = img.mode
        return f"Image file: {path.name}. Dimensions: {w}x{h}. Mode: {mode}."
