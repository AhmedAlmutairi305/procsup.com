from __future__ import annotations

import hashlib
from pathlib import Path

from .chunker import chunk_text
from .parsers import parse_path
from ..embeddings.ollama import OllamaEmbedder
from ..retrieve.vector_store import VectorStore
from ..observability.meter import Meter, MeterRow
from datetime import datetime


SUPPORTED = {".pdf", ".md", ".txt"}


def ingest_folder(folder: str, workspace_id: str, chunk_size: int = 512, overlap: int = 64) -> dict:
    base = Path(folder)
    embedder = OllamaEmbedder()
    store = VectorStore(workspace_id)
    meter = Meter()

    indexed = 0
    skipped = 0

    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        text = parse_path(path)
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        for idx, chunk in enumerate(chunks):
            h = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            if store.has_hash(h):
                skipped += 1
                continue
            emb = embedder.embed(chunk)
            store.add_chunk(h, chunk, str(path), idx, emb)
            meter.write_row(
                MeterRow(
                    timestamp=datetime.utcnow(),
                    workspace_id=workspace_id,
                    user_id="system",
                    provider="ollama",
                    model="nomic-embed-text",
                    op_type="embed",
                    input_tokens=len(chunk.split()),
                    output_tokens=0,
                    cost_usd=0.0,
                    latency_ms=0,
                    cache_hit=False,
                    query_hash=h,
                )
            )
            indexed += 1

    return {"indexed": indexed, "skipped": skipped}
