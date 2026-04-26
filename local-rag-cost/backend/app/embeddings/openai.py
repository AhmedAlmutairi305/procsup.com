from .base import Embedder


class OpenAIEmbedder(Embedder):
    embedder_id = "openai"

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError("OpenAI embedder deferred to future phase")
