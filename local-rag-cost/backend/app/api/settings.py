from fastapi import APIRouter
from ..llm.registry import list_providers

router = APIRouter(prefix="/api/settings")


@router.get("/providers")
def providers():
    return {"providers": list_providers()}
