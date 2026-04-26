from .base import Embedder


class VoyageEmbedder(Embedder):
    embedder_id = "voyage"

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Voyage embedder deferred to future phase")
