from backend.app.retrieve.vector_store import VectorStore


def test_hash_dedup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    store = VectorStore("demo")
    h = "abc"
    store.add_chunk(h, "hello", "a.txt", 0, [1.0, 0.0])
    assert store.has_hash(h)
    store.add_chunk(h, "hello", "a.txt", 0, [1.0, 0.0])
    rows = store.conn.execute("SELECT COUNT(*) FROM chunks WHERE hash='abc'").fetchone()[0]
    assert rows == 1
