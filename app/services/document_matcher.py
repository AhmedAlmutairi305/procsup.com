from pathlib import Path

from app.models.models import Document


def _score(required_key: str, doc: Document) -> float:
    tokens = set(required_key.lower().split("_"))
    searchable = f"{doc.filename} {doc.tag} {doc.extra_tags or ''}".lower()
    points = sum(1 for t in tokens if t in searchable)
    if required_key == doc.tag:
        points += 2
    return min(1.0, points / max(2, len(tokens) + 1))


def match_documents(required_docs: list[str], docs: list[Document]) -> list[dict]:
    previews: list[dict] = []
    for req in required_docs:
        best_doc = None
        best_score = 0.0
        for doc in docs:
            s = _score(req, doc)
            if s > best_score:
                best_score = s
                best_doc = doc

        warning = None
        if best_doc:
            stem = Path(best_doc.filename).stem.lower()
            if req.split("_")[0] not in stem and best_score < 0.8:
                warning = f"Possible naming mismatch for {req}: {best_doc.filename}"

        previews.append(
            {
                "requirement_key": req,
                "matched_file": best_doc.file_path if best_doc else None,
                "confidence": round(best_score, 2),
                "warning": warning if best_doc else f"Missing document for {req}",
            }
        )

    return previews
