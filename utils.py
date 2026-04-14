from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional


def setup_logging(log_file: Path, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("docws")
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def sha1_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def smart_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)

        if end < n:
            split_window = text[start:end]
            best_split = max(split_window.rfind("\n\n"), split_window.rfind(". "), split_window.rfind("\n"))
            if best_split > chunk_size // 3:
                end = start + best_split + 1

        segment = text[start:end].strip()
        if segment:
            chunks.append(segment)

        if end == n:
            break
        start = max(0, end - overlap)

    return chunks


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_image_related_query(query: str) -> bool:
    q = query.lower()
    keys = [
        "figure",
        "diagram",
        "image",
        "screenshot",
        "chart",
        "plot",
        "scan",
        "visual",
        "table in image",
    ]
    return any(k in q for k in keys)


def now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Timer:
    label: str
    logger: Optional[logging.Logger] = None

    def __post_init__(self) -> None:
        self.start_ms = now_ms()

    def stop(self) -> int:
        elapsed = now_ms() - self.start_ms
        if self.logger:
            self.logger.info("%s took %dms", self.label, elapsed)
        return elapsed
