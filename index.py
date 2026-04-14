from __future__ import annotations

import argparse
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from config import Settings, get_settings
from ingest import DocumentUnit, Ingestor
from utils import load_json, save_json, setup_logging, smart_chunks


@dataclass
class ChunkRecord:
    chunk_id: str
    doc_id: str
    file_path: str
    file_type: str
    page_number: Optional[int]
    text: str
    token_count: int
    metadata: Dict[str, str]


class LocalIndex:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = setup_logging(settings.log_dir / "index.log")
        self.embedder = SentenceTransformer(settings.embedding_model)

        self.paths = {
            "manifest": settings.index_dir / "manifest.json",
            "chunks": settings.index_dir / "chunks.pkl",
            "bm25": settings.index_dir / "bm25.pkl",
            "faiss": settings.index_dir / "faiss.index",
        }

    def build_or_update(self, input_paths: List[str], force_rebuild: bool = False) -> Dict[str, int]:
        ingestor = Ingestor(self.settings)
        units = ingestor.ingest_paths(input_paths)
        self.logger.info("Ingested %d units", len(units))

        manifest = {} if force_rebuild else load_json(self.paths["manifest"], {})
        existing_chunks: List[ChunkRecord] = [] if force_rebuild else self._load_chunks()
        existing_by_file = self._group_chunks_by_file(existing_chunks)

        kept_chunks: List[ChunkRecord] = []
        new_chunks: List[ChunkRecord] = []

        current_files = set()
        for unit in units:
            current_files.add(unit.file_path)
            previous = manifest.get(unit.file_path)
            unchanged = (
                previous
                and previous.get("file_hash") == unit.file_hash
                and abs(float(previous.get("modified_time", 0)) - unit.modified_time) < 1e-3
            )
            if unchanged and unit.file_path in existing_by_file:
                kept_chunks.extend(existing_by_file[unit.file_path])
                continue

            chunked = self._chunk_unit(unit)
            new_chunks.extend(chunked)
            manifest[unit.file_path] = {
                "file_hash": unit.file_hash,
                "modified_time": unit.modified_time,
                "file_type": unit.file_type,
            }

        # Drop deleted files from manifest/chunks
        deleted = set(manifest.keys()) - current_files
        for d in deleted:
            manifest.pop(d, None)

        final_chunks = [c for c in kept_chunks if c.file_path in current_files] + new_chunks

        self._save_chunks(final_chunks)
        self._build_dense_index(final_chunks)
        self._build_sparse_index(final_chunks)
        save_json(self.paths["manifest"], manifest)

        return {
            "files": len(current_files),
            "chunks": len(final_chunks),
            "new_chunks": len(new_chunks),
            "kept_chunks": len(kept_chunks),
            "deleted_files": len(deleted),
        }

    def _chunk_unit(self, unit: DocumentUnit) -> List[ChunkRecord]:
        segments = smart_chunks(unit.text, self.settings.chunk_size, self.settings.chunk_overlap)
        out: List[ChunkRecord] = []
        for i, seg in enumerate(segments):
            chunk_id = f"{unit.doc_id}::chunk{i}"
            out.append(
                ChunkRecord(
                    chunk_id=chunk_id,
                    doc_id=unit.doc_id,
                    file_path=unit.file_path,
                    file_type=unit.file_type,
                    page_number=unit.page_number,
                    text=seg,
                    token_count=max(1, len(seg) // 4),
                    metadata=unit.metadata,
                )
            )
        return out

    def _build_dense_index(self, chunks: List[ChunkRecord]) -> None:
        texts = [c.text for c in chunks]
        embeddings = self.embedder.encode(texts, normalize_embeddings=True, show_progress_bar=True)
        arr = np.asarray(embeddings, dtype=np.float32)
        dim = arr.shape[1]
        index = faiss.IndexFlatIP(dim)
        if len(arr):
            index.add(arr)
        faiss.write_index(index, str(self.paths["faiss"]))

    def _build_sparse_index(self, chunks: List[ChunkRecord]) -> None:
        tokenized = [c.text.lower().split() for c in chunks]
        bm25 = BM25Okapi(tokenized)
        with self.paths["bm25"].open("wb") as f:
            pickle.dump(bm25, f)

    def _save_chunks(self, chunks: List[ChunkRecord]) -> None:
        with self.paths["chunks"].open("wb") as f:
            pickle.dump(chunks, f)

    def _load_chunks(self) -> List[ChunkRecord]:
        if not self.paths["chunks"].exists():
            return []
        with self.paths["chunks"].open("rb") as f:
            return pickle.load(f)

    def _group_chunks_by_file(self, chunks: List[ChunkRecord]) -> Dict[str, List[ChunkRecord]]:
        out: Dict[str, List[ChunkRecord]] = {}
        for c in chunks:
            out.setdefault(c.file_path, []).append(c)
        return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or update local hybrid index")
    parser.add_argument("paths", nargs="+", help="File(s) or folder(s) to index")
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--rebuild", action="store_true", help="Force full rebuild")
    args = parser.parse_args()

    settings = get_settings(args.workspace)
    idx = LocalIndex(settings)
    stats = idx.build_or_update(args.paths, force_rebuild=args.rebuild)
    print(stats)


if __name__ == "__main__":
    main()
