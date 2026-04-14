from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import faiss
import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

from config import Settings
from index import ChunkRecord
from utils import setup_logging


@dataclass
class RetrievalHit:
    chunk: ChunkRecord
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rerank_score: float = 0.0
    final_score: float = 0.0


class HybridRetriever:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = setup_logging(settings.log_dir / "retriever.log")

        self.embedder = SentenceTransformer(settings.embedding_model)
        self.reranker = CrossEncoder(settings.reranker_model) if settings.use_reranker else None

        self.chunk_path = settings.index_dir / "chunks.pkl"
        self.bm25_path = settings.index_dir / "bm25.pkl"
        self.faiss_path = settings.index_dir / "faiss.index"

        self.chunks = self._load_chunks()
        self.bm25 = self._load_bm25()
        self.faiss = self._load_faiss()

    def _load_chunks(self) -> List[ChunkRecord]:
        with self.chunk_path.open("rb") as f:
            return pickle.load(f)

    def _load_bm25(self):
        with self.bm25_path.open("rb") as f:
            return pickle.load(f)

    def _load_faiss(self):
        return faiss.read_index(str(self.faiss_path))

    def retrieve(self, query: str) -> List[RetrievalHit]:
        dense_hits = self._dense_retrieve(query)
        sparse_hits = self._sparse_retrieve(query)

        merged: Dict[str, RetrievalHit] = {}
        for idx, score in dense_hits:
            chunk = self.chunks[idx]
            hit = merged.setdefault(chunk.chunk_id, RetrievalHit(chunk=chunk))
            hit.dense_score = float(score)

        for idx, score in sparse_hits:
            chunk = self.chunks[idx]
            hit = merged.setdefault(chunk.chunk_id, RetrievalHit(chunk=chunk))
            hit.sparse_score = float(score)

        hits = list(merged.values())

        for h in hits:
            h.final_score = 0.6 * h.dense_score + 0.4 * h.sparse_score

        hits.sort(key=lambda x: x.final_score, reverse=True)
        hits = hits[: max(self.settings.top_k_dense, self.settings.top_k_sparse)]

        if self.reranker and hits:
            pairs = [(query, h.chunk.text) for h in hits]
            rr = self.reranker.predict(pairs)
            for h, s in zip(hits, rr):
                h.rerank_score = float(s)
                h.final_score = 0.25 * h.final_score + 0.75 * h.rerank_score
            hits.sort(key=lambda x: x.final_score, reverse=True)

        final = hits[: self.settings.top_k_final]
        self.logger.info(
            "query=%r results=%s",
            query,
            [
                {
                    "file": Path(h.chunk.file_path).name,
                    "page": h.chunk.page_number,
                    "score": round(h.final_score, 4),
                }
                for h in final
            ],
        )
        return final

    def _dense_retrieve(self, query: str) -> List[Tuple[int, float]]:
        vec = self.embedder.encode([query], normalize_embeddings=True)
        vec = np.asarray(vec, dtype=np.float32)
        k = min(self.settings.top_k_dense, len(self.chunks))
        if k == 0:
            return []
        scores, ids = self.faiss.search(vec, k)
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i >= 0]

    def _sparse_retrieve(self, query: str) -> List[Tuple[int, float]]:
        if not self.chunks:
            return []
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        ranked = np.argsort(scores)[::-1][: self.settings.top_k_sparse]
        return [(int(i), float(scores[i])) for i in ranked]

    @staticmethod
    def format_citations(hits: List[RetrievalHit]) -> List[str]:
        cites: List[str] = []
        for h in hits:
            path = Path(h.chunk.file_path)
            loc = f"page {h.chunk.page_number}" if h.chunk.page_number else "chunk"
            cites.append(f"{path.name} ({loc})")
        return cites
