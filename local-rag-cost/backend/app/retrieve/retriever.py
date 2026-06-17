from .vector_store import VectorStore


def retrieve(workspace_id: str, query_embedding: list[float], k: int = 10):
    return VectorStore(workspace_id).search(query_embedding, k=k)
