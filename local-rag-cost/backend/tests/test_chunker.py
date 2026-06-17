from backend.app.ingest.chunker import chunk_text


def test_chunker_overlap():
    text = " ".join(str(i) for i in range(1000))
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    first = chunks[0].split()
    second = chunks[1].split()
    assert first[-10:] == second[:10]
