from abc import ABC, abstractmethod


class Embedder(ABC):
    embedder_id: str

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError
