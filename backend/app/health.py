from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db
from .rag.store import INDEX_PATH

router = APIRouter(tags=["ops"])


@router.get("/health")
def health():
    """Liveness: process zinda hai. Koi dependency nahi chhoota."""
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    """Readiness: DB se baat ho sakti hai?"""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database not ready")
    # rag_index sirf info hai: index na ho toh baaki app chalti hai, sirf /rag/ask 503 dega
    return {"status": "ready", "rag_index": INDEX_PATH.exists()}
