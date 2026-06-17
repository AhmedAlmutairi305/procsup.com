def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk_words = words[i : i + chunk_size]
        if not chunk_words:
            continue
        chunks.append(" ".join(chunk_words))
        if i + chunk_size >= len(words):
            break
    return chunks
