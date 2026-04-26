from fastapi import APIRouter
from pydantic import BaseModel

from ..query import ask

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    workspace_id: str
    query: str


@router.post("/chat")
def chat(req: ChatRequest):
    out = ask(req.workspace_id, req.query)
    return {
        "answer": out["answer"],
        "sources": [{"source_path": s["source_path"], "score": s["score"]} for s in out["sources"]],
        "cost_breakdown": out["usage"],
    }
