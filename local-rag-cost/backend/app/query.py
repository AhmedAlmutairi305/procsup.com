import argparse
import hashlib
from datetime import datetime, timedelta

from .embeddings.ollama import OllamaEmbedder
from .llm.registry import get_provider
from .observability.meter import Meter, MeterRow
from .retrieve.retriever import retrieve


DEFAULT_MODEL = "claude-haiku-4-5"


def ask(workspace_id: str, question: str) -> dict:
    meter = Meter()
    query_hash = hashlib.sha256(f"{workspace_id}:{question}".encode()).hexdigest()

    embedder = OllamaEmbedder()
    q_emb = embedder.embed(question)
    chunks = retrieve(workspace_id, q_emb, k=10)
    context = "\n\n".join(c["text"] for c in chunks)
    messages = [
        {"role": "user", "content": f"Answer using the context below.\n\nContext:\n{context}\n\nQuestion:\n{question}"}
    ]

    provider = get_provider("anthropic")
    resp = provider.generate(messages, model=DEFAULT_MODEL, max_tokens=1024)
    computed_cost = meter.compute_cost(resp.model_id, resp.input_tokens, resp.output_tokens)

    meter.write_row(
        MeterRow(
            timestamp=datetime.utcnow(),
            workspace_id=workspace_id,
            user_id="cli",
            provider="anthropic",
            model=resp.model_id,
            op_type="generate",
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
            cost_usd=computed_cost,
            latency_ms=resp.latency_ms,
            cache_hit=False,
            query_hash=query_hash,
        )
    )
    usage = meter.get_usage(workspace_id, datetime.utcnow() - timedelta(days=3650), datetime.utcnow())
    return {"answer": resp.raw_text, "sources": chunks, "cost": computed_cost, "usage": usage}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument("question")
    args = parser.parse_args()
    result = ask(args.workspace, args.question)
    print(result["answer"])
    print(f"Cost USD: {result['cost']}")


if __name__ == "__main__":
    main()
