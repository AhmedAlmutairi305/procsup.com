from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime
from pathlib import Path

from ..workspaces.manager import workspace_dir


class VectorStore:
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.db_path = workspace_dir(workspace_id) / "index.sqlite"
        self.conn = sqlite3.connect(self.db_path)
        self._init_schema()

    def _init_schema(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                text TEXT,
                source_path TEXT,
                source_offset INTEGER,
                embedding BLOB,
                ws_id TEXT,
                created_at TEXT
            )
            """
        )
        self.conn.commit()

    def has_hash(self, chunk_hash: str) -> bool:
        row = self.conn.execute("SELECT 1 FROM chunks WHERE hash = ?", [chunk_hash]).fetchone()
        return bool(row)

    def add_chunk(self, chunk_hash: str, text: str, source_path: str, source_offset: int, embedding: list[float]):
        self.conn.execute(
            "INSERT OR IGNORE INTO chunks(hash, text, source_path, source_offset, embedding, ws_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [chunk_hash, text, source_path, source_offset, json.dumps(embedding).encode("utf-8"), self.workspace_id, datetime.utcnow().isoformat()],
        )
        self.conn.commit()

    def search(self, query_embedding: list[float], k: int = 10) -> list[dict]:
        rows = self.conn.execute("SELECT id, text, source_path, source_offset, embedding FROM chunks").fetchall()
        scored = []
        for row in rows:
            emb = json.loads(row[4].decode("utf-8"))
            score = self._cosine_similarity(query_embedding, emb)
            scored.append({"id": row[0], "text": row[1], "source_path": row[2], "source_offset": row[3], "score": score})
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:k]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0
