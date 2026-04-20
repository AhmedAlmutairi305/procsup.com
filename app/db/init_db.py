from __future__ import annotations

from sqlalchemy import text

from app.db.database import Base, engine
from app.models import models  # noqa: F401


SQLITE_MIGRATIONS = [
    "ALTER TABLE universities ADD COLUMN slug VARCHAR(120)",
    "ALTER TABLE audit_logs ADD COLUMN run_id INTEGER",
]


def _run_sqlite_best_effort_migrations() -> None:
    if not str(engine.url).startswith("sqlite"):
        return
    with engine.begin() as conn:
        for stmt in SQLITE_MIGRATIONS:
            try:
                conn.execute(text(stmt))
            except Exception:
                # best-effort compatibility for existing local DBs
                pass


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _run_sqlite_best_effort_migrations()
