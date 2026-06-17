from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import duckdb
import yaml

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MeterRow:
    timestamp: datetime
    workspace_id: str
    user_id: str
    provider: str
    model: str
    op_type: str
    input_tokens: int
    output_tokens: int
    cost_usd: float | None
    latency_ms: int
    cache_hit: bool
    query_hash: str


class Meter:
    def __init__(self, db_path: Path | None = None, pricing_path: Path | None = None) -> None:
        self.db_path = db_path or settings.observability_db
        self.pricing_path = pricing_path or settings.pricing_config
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _conn(self):
        return duckdb.connect(str(self.db_path))

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS meter (
                    timestamp TIMESTAMP,
                    workspace_id VARCHAR,
                    user_id VARCHAR,
                    provider VARCHAR,
                    model VARCHAR,
                    op_type VARCHAR,
                    input_tokens BIGINT,
                    output_tokens BIGINT,
                    cost_usd DOUBLE,
                    latency_ms BIGINT,
                    cache_hit BOOLEAN,
                    query_hash VARCHAR
                )
                """
            )

    def _pricing(self) -> dict:
        if not self.pricing_path.exists():
            return {}
        return yaml.safe_load(self.pricing_path.read_text()) or {}

    def compute_cost(self, model: str, input_tokens: int, output_tokens: int) -> float | None:
        pricing = self._pricing().get("models", {})
        entry = pricing.get(model)
        if not entry:
            logger.warning("model missing from pricing config: %s", model)
            return None
        input_rate = float(entry.get("input_per_million", 0))
        output_rate = float(entry.get("output_per_million", 0))
        return (input_tokens / 1_000_000 * input_rate) + (output_tokens / 1_000_000 * output_rate)

    def write_row(self, row: MeterRow) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO meter VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    row.timestamp,
                    row.workspace_id,
                    row.user_id,
                    row.provider,
                    row.model,
                    row.op_type,
                    row.input_tokens,
                    row.output_tokens,
                    row.cost_usd,
                    row.latency_ms,
                    row.cache_hit,
                    row.query_hash,
                ],
            )

    def get_usage(self, workspace_id: str, since: datetime, until: datetime) -> dict:
        with self._conn() as conn:
            out = conn.execute(
                """
                SELECT
                    COUNT(*) AS calls,
                    COALESCE(SUM(input_tokens), 0) AS input_tokens,
                    COALESCE(SUM(output_tokens), 0) AS output_tokens,
                    SUM(cost_usd) AS cost_usd
                FROM meter
                WHERE workspace_id = ? AND timestamp BETWEEN ? AND ?
                """,
                [workspace_id, since, until],
            ).fetchone()
        return {
            "calls": int(out[0]),
            "input_tokens": int(out[1]),
            "output_tokens": int(out[2]),
            "cost_usd": None if out[3] is None else float(out[3]),
        }
