from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.chat import router as chat_router
from .api.costs import router as costs_router
from .api.settings import router as settings_router

app = FastAPI(title="local-rag-cost")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(costs_router)
app.include_router(settings_router)


@app.get("/health")
def health():
    return {"ok": True}
