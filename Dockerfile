FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EMBED_CACHE_DIR=/app/.cache/embed

WORKDIR /app

# Dependencies pehle: code badle toh ye layer cache se aayegi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# Non-root user
RUN useradd -m appuser && mkdir -p /app/.cache/embed && chown -R appuser /app
USER appuser

WORKDIR /app/backend

# Image banate waqt hi model download + index build
RUN python -m app.rag.build_index

EXPOSE 8000

# 1 worker: rate limiter aur agent approvals in-memory hain (Phase 14 ka gotcha)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
