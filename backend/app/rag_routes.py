from functools import lru_cache

import anthropic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .assistant import check_rate_limit, get_client
from .auth import get_current_user
from .rag.answer import answer_question
from .rag.embedder import Embedder
from .rag.store import INDEX_PATH, VectorStore

router = APIRouter(prefix="/rag", tags=["rag"])


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=300)


class Source(BaseModel):
    n: int
    title: str
    source: str
    chunk_id: str


class AskResponse(BaseModel):
    reply: str
    sources: list[Source]
    grounded: bool


@lru_cache
def _embedder() -> Embedder:
    return Embedder()


@lru_cache
def _store() -> VectorStore:
    if not INDEX_PATH.exists():
        raise HTTPException(
            status_code=503, detail="Index nahi bana. Run: python -m app.rag.build_index"
        )
    return VectorStore.load(INDEX_PATH)


@router.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    user=Depends(get_current_user),
    client=Depends(get_client),
):
    check_rate_limit(user.id)
    store = _store()
    try:
        r = answer_question(body.question, store, _embedder(), client)
    except anthropic.AnthropicError:
        raise HTTPException(status_code=502, detail="AI service abhi available nahi hai")
    return AskResponse(reply=r.reply, sources=r.sources, grounded=r.grounded)