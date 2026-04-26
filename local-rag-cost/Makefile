.PHONY: install run backend frontend ingest query test

install:
	uv sync --extra dev
	cd frontend && npm install

backend:
	uv run uvicorn backend.app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev -- --host --port 5173

run:
	bash -lc 'set -e; trap "kill 0" EXIT; uv run uvicorn backend.app.main:app --reload --port 8000 & cd frontend && npm run dev -- --host --port 5173 & wait'

ingest:
	uv run python -m backend.app.ingest $(DIR) --workspace $(WS)

query:
	uv run python -m backend.app.query $(WS) "$(Q)"

test:
	uv run pytest -q
