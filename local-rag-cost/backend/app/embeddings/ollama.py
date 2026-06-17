import httpx
from .base import Embedder
from ..core.config import settings


class OllamaEmbedder(Embedder):
    embedder_id = "ollama:nomic-embed-text"

    def embed(self, text: str) -> list[float]:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
            )
            resp.raise_for_status()
            return resp.json().get("embedding", [])
