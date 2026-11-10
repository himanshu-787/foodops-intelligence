import uuid
from typing import Literal

import anthropic
from fastapi import APIRouter, Depends, HTTPException
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .agent.graph import build_graph, resume, start
from .assistant import check_rate_limit, get_client
from .auth import get_current_user
from .database import get_db

router = APIRouter(prefix="/agent", tags=["agent"])

_saver = MemorySaver()  # in-memory, single process
_owners: dict[str, int] = {}  # thread_id -> user_id (TTL cleanup baad mein)


class AgentChat(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class AgentResume(BaseModel):
    thread_id: str
    approved: bool


class AgentResponse(BaseModel):
    status: Literal["done", "needs_approval"]
    thread_id: str
    reply: str | None = None
    approval: dict | None = None


@router.post("/chat", response_model=AgentResponse)
def agent_chat(
    body: AgentChat,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    client=Depends(get_client),
):
    check_rate_limit(user.id)
    tid = uuid.uuid4().hex
    _owners[tid] = user.id
    try:
        out = start(build_graph(db, user, client, _saver), tid, body.message)
    except anthropic.AnthropicError:
        _owners.pop(tid, None)
        raise HTTPException(status_code=502, detail="AI service abhi available nahi hai")
    if out["status"] == "done":
        _owners.pop(tid, None)
    return AgentResponse(thread_id=tid, **out)


@router.post("/resume", response_model=AgentResponse)
def agent_resume(
    body: AgentResume,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    client=Depends(get_client),
):
    if _owners.get(body.thread_id) != user.id:  # exist hi nahi ya kisi aur ka
        raise HTTPException(status_code=404, detail="Pending action nahi mila")
    check_rate_limit(user.id)
    try:
        out = resume(build_graph(db, user, client, _saver), body.thread_id, body.approved)
    except anthropic.AnthropicError:
        _owners.pop(body.thread_id, None)  # retry fresh chat se; cancel idempotent hai
        raise HTTPException(status_code=502, detail="AI service abhi available nahi hai")
    if out["status"] == "done":
        _owners.pop(body.thread_id, None)
    return AgentResponse(thread_id=body.thread_id, **out)