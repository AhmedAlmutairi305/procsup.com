# Local Multimodal Document Workspace (Claude + Hybrid RAG)

A production-oriented, local-first document workspace for research/thesis/project folders.
It supports recursive ingestion, hybrid retrieval (dense + BM25), optional reranking, multimodal handling (images), and Claude-powered answers.

## What this project provides

- **RAG mode** for large corpora (retrieve top chunks, then answer).
- **Full-context mode** for smaller corpora (include all relevant context when safe).
- **Recursive local indexing** for files and folders.
- **Supported input types**:
  - Text/code/data: `.txt .md .tex .py .json .csv`
  - Documents: `.pdf .docx`
  - Images: `.png .jpg .jpeg .webp`
- **Hybrid retrieval**:
  - Dense vector retrieval (SentenceTransformers + FAISS)
  - Sparse keyword retrieval (BM25)
  - Optional local reranker (CrossEncoder)
- **Incremental indexing**: unchanged files are reused.
- **Source citations** in responses.
- **Vision-aware answering path**: image files are passed to Claude when query indicates figure/diagram/screenshot intent.
- **CLI-first UX** with `index`, `ask`, `chat`, `rebuild`, `inspect` commands.
- **Logging and debugability** via local log files.

## Project layout

```text
.
├── chat.py        # CLI, ask/chat workflows, Claude calls
├── config.py      # Env-driven settings + defaults
├── ingest.py      # Recursive scanning + file parsers
├── index.py       # Chunking + incremental indexing + FAISS/BM25 persistence
├── retriever.py   # Hybrid retrieval + optional reranking + citations
├── utils.py       # Logging, chunking utilities, helpers
├── requirements.txt
└── README.md
```

## Installation

1. Create venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables (`.env` supported):

```bash
ANTHROPIC_API_KEY=your_key_here
MODEL_NAME=claude-sonnet-4-20250514
WORKSPACE_DIR=./.docws
CHUNK_SIZE=900
CHUNK_OVERLAP=180
TOP_K_DENSE=12
TOP_K_SPARSE=12
TOP_K_FINAL=8
USE_RERANKER=true
MAX_FULL_CONTEXT_CHARS=140000
OUTPUT_PATH=./text.tex
```

## Usage

### 1) Build / update index

```bash
python chat.py index /path/to/thesis /path/to/notes
```

Incremental behavior:
- unchanged files are kept
- changed files are re-chunked and re-embedded
- deleted files are removed from manifest/chunk set

### 2) Force full rebuild

```bash
python chat.py rebuild /path/to/thesis
```

### 3) Ask a question (RAG)

```bash
python chat.py ask "Summarize related work on diffusion models" --mode rag
```

### 4) Ask in full-context mode

```bash
python chat.py ask "Draft a concise abstract" --mode full
```

If context size exceeds `MAX_FULL_CONTEXT_CHARS`, it auto-falls back to RAG mode.

### 5) LaTeX output and save to file

```bash
python chat.py ask "Write findings in LaTeX" --output latex --save text.tex
```

Append mode:

```bash
python chat.py ask "Add limitations section" --output latex --save text.tex --append
```

### 6) Interactive chat

```bash
python chat.py chat --mode rag
```

### 7) Inspect index

```bash
python chat.py inspect
```

## Vision flow details

When the query appears image-related (e.g., contains “figure”, “diagram”, “screenshot”, “chart”), the system:

1. Retrieves relevant chunks as usual (hybrid retrieval).
2. Collects image files among top hits.
3. Sends image blocks + context text together to Claude.

This keeps image-aware QA integrated with normal retrieval behavior.

## Operational notes

- Index artifacts are stored under `WORKSPACE_DIR/index`.
- Logs are stored under `WORKSPACE_DIR/logs`.
- Default FAISS setup is `IndexFlatIP` with normalized embeddings (cosine-like retrieval).
- BM25 uses simple whitespace tokenization; easy to replace with custom analyzer.

## Extending to PPTX / XLSX / audio / video

The architecture is intentionally split so modality support can be added safely:

- Add new parser functions in `ingest.py` and register extension handlers.
- Emit `DocumentUnit` with rich metadata (timestamps, slide/page/frame references).
- For audio/video, add transcription/OCR stage before chunking.
- For scanned PDFs, add OCR renderer path (e.g., page rasterization + OCR), then feed both text and image blocks.

## Example end-to-end session

```bash
python chat.py index ~/research/thesis
python chat.py ask "What are the key assumptions in Chapter 3?" --mode rag
python chat.py ask "Turn that into a LaTeX subsection" --output latex --save text.tex --append
python chat.py chat --mode full
```

## Production readiness checklist

- [x] Modular code with clear responsibilities
- [x] Type hints across main code paths
- [x] Incremental indexing support
- [x] Persistent local index and sparse index
- [x] Local logs for ingestion/retrieval/chat
- [x] CLI command surface for daily workflows
- [x] Designed for extension to additional modalities

