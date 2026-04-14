from __future__ import annotations

import argparse
import base64
from pathlib import Path
from typing import Dict, List

from anthropic import Anthropic

from config import get_settings
from index import LocalIndex
from retriever import HybridRetriever, RetrievalHit
from utils import ensure_parent, is_image_related_query, setup_logging


def build_context_from_hits(hits: List[RetrievalHit]) -> str:
    blocks: List[str] = []
    for i, h in enumerate(hits, start=1):
        label = f"[{i}] file={h.chunk.file_path} page={h.chunk.page_number}"
        blocks.append(f"{label}\n{h.chunk.text}")
    return "\n\n".join(blocks)


def claude_answer(
    client: Anthropic,
    model: str,
    question: str,
    context_text: str,
    output_mode: str,
    image_paths: List[Path],
) -> str:
    sys = (
        "You are a precise research assistant. Use only provided context. "
        "When evidence is weak, say so. Include source references like [1], [2]."
    )

    user_blocks = [
        {
            "type": "text",
            "text": f"Question: {question}\n\nOutput format: {output_mode}\n\nContext:\n{context_text}",
        }
    ]

    for img_path in image_paths:
        media_type = f"image/{img_path.suffix.lower().lstrip('.')}"
        data = base64.b64encode(img_path.read_bytes()).decode("utf-8")
        user_blocks.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": data},
            }
        )

    response = client.messages.create(
        model=model,
        max_tokens=1800,
        temperature=0.1,
        system=sys,
        messages=[{"role": "user", "content": user_blocks}],
    )
    texts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
    return "\n".join(texts).strip()


def collect_images_from_hits(hits: List[RetrievalHit], max_images: int = 4) -> List[Path]:
    paths: List[Path] = []
    for h in hits:
        p = Path(h.chunk.file_path)
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and p.exists():
            paths.append(p)
        if len(paths) >= max_images:
            break
    return paths


def run_ask(args: argparse.Namespace) -> None:
    settings = get_settings(args.workspace)
    logger = setup_logging(settings.log_dir / "chat.log")

    retriever = HybridRetriever(settings)
    hits = retriever.retrieve(args.question)

    full_context_mode = args.mode == "full"
    if full_context_mode:
        combined = "\n\n".join(h.chunk.text for h in hits)
        if len(combined) > settings.max_full_context_chars:
            logger.warning("Full context too large; falling back to RAG mode")
            full_context_mode = False

    context = (
        "\n\n".join(h.chunk.text for h in hits)
        if full_context_mode
        else build_context_from_hits(hits)
    )

    image_paths = collect_images_from_hits(hits) if is_image_related_query(args.question) else []

    client = Anthropic(api_key=settings.anthropic_api_key)
    answer = claude_answer(
        client=client,
        model=settings.model_name,
        question=args.question,
        context_text=context,
        output_mode=args.output,
        image_paths=image_paths,
    )

    citations = retriever.format_citations(hits)
    print(answer)
    if citations:
        print("\nSources:")
        for i, c in enumerate(citations, start=1):
            print(f"[{i}] {c}")

    if args.save:
        out_path = Path(args.save)
        ensure_parent(out_path)
        mode = "a" if args.append else "w"
        with out_path.open(mode, encoding="utf-8") as f:
            f.write(answer + "\n")
        print(f"Saved answer to {out_path}")


def run_chat(args: argparse.Namespace) -> None:
    print("Interactive chat mode. Type 'exit' to quit.")
    while True:
        question = input("\nYou> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        local_args = argparse.Namespace(
            workspace=args.workspace,
            question=question,
            mode=args.mode,
            output=args.output,
            save=args.save,
            append=True,
        )
        run_ask(local_args)


def run_inspect(args: argparse.Namespace) -> None:
    settings = get_settings(args.workspace)
    r = HybridRetriever(settings)
    print(f"Chunks loaded: {len(r.chunks)}")
    if r.chunks:
        print(f"Example file: {r.chunks[0].file_path}")


def run_index(args: argparse.Namespace, rebuild: bool = False) -> None:
    settings = get_settings(args.workspace)
    idx = LocalIndex(settings)
    stats = idx.build_or_update(args.paths, force_rebuild=rebuild)
    print(stats)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local multimodal document workspace")
    parser.add_argument("--workspace", default=None, help="Workspace directory for index/logs")

    sub = parser.add_subparsers(dest="command", required=True)

    sp_index = sub.add_parser("index", help="Index files/folders incrementally")
    sp_index.add_argument("paths", nargs="+")
    sp_index.set_defaults(func=lambda a: run_index(a, rebuild=False))

    sp_rebuild = sub.add_parser("rebuild", help="Force rebuild index")
    sp_rebuild.add_argument("paths", nargs="+")
    sp_rebuild.set_defaults(func=lambda a: run_index(a, rebuild=True))

    sp_ask = sub.add_parser("ask", help="Ask one question")
    sp_ask.add_argument("question")
    sp_ask.add_argument("--mode", choices=["rag", "full"], default="rag")
    sp_ask.add_argument("--output", choices=["text", "latex"], default="text")
    sp_ask.add_argument("--save", default=None, help="Save output to path (e.g., text.tex)")
    sp_ask.add_argument("--append", action="store_true", help="Append when saving")
    sp_ask.set_defaults(func=run_ask)

    sp_chat = sub.add_parser("chat", help="Interactive chat")
    sp_chat.add_argument("--mode", choices=["rag", "full"], default="rag")
    sp_chat.add_argument("--output", choices=["text", "latex"], default="text")
    sp_chat.add_argument("--save", default=None)
    sp_chat.set_defaults(func=run_chat)

    sp_inspect = sub.add_parser("inspect", help="Inspect local index")
    sp_inspect.set_defaults(func=run_inspect)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
