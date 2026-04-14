from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    """Runtime settings loaded from environment variables."""

    workspace_dir: Path = field(
        default_factory=lambda: Path(os.getenv("WORKSPACE_DIR", "./.docws")).resolve()
    )
    index_dir: Path = field(init=False)
    log_dir: Path = field(init=False)
    output_dir: Path = field(init=False)

    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "claude-sonnet-4-20250514"))

    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )
    reranker_model: str = field(
        default_factory=lambda: os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    )

    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "900")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "180")))
    top_k_dense: int = field(default_factory=lambda: int(os.getenv("TOP_K_DENSE", "12")))
    top_k_sparse: int = field(default_factory=lambda: int(os.getenv("TOP_K_SPARSE", "12")))
    top_k_final: int = field(default_factory=lambda: int(os.getenv("TOP_K_FINAL", "8")))
    use_reranker: bool = field(default_factory=lambda: os.getenv("USE_RERANKER", "true").lower() == "true")

    max_full_context_chars: int = field(
        default_factory=lambda: int(os.getenv("MAX_FULL_CONTEXT_CHARS", "140000"))
    )

    output_path: Path = field(default_factory=lambda: Path(os.getenv("OUTPUT_PATH", "./text.tex")))

    include_hidden_files: bool = field(default_factory=lambda: os.getenv("INCLUDE_HIDDEN_FILES", "false").lower() == "true")

    supported_extensions: List[str] = field(
        default_factory=lambda: [
            ".txt",
            ".md",
            ".tex",
            ".py",
            ".json",
            ".csv",
            ".pdf",
            ".docx",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        ]
    )

    # Reserved for future modalities
    future_extensions: List[str] = field(default_factory=lambda: [".pptx", ".xlsx", ".mp3", ".wav", ".mp4", ".mkv"])

    def __post_init__(self) -> None:
        self.index_dir = self.workspace_dir / "index"
        self.log_dir = self.workspace_dir / "logs"
        self.output_dir = self.workspace_dir / "outputs"

        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


def get_settings(override_workspace: Optional[str] = None) -> Settings:
    settings = Settings()
    if override_workspace:
        settings.workspace_dir = Path(override_workspace).resolve()
        settings.__post_init__()
    return settings
