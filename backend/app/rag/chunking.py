import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    title: str
    text: str


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def chunk_markdown(md: str, source: str, max_chars: int = 600) -> list[Chunk]:
    """'## ' heading par split. Bada section ho toh paragraphs par todo."""
    sections = re.split(r"^## ", md, flags=re.MULTILINE)[1:]  # [0] = doc ka title, skip
    chunks: list[Chunk] = []
    for sec in sections:
        title, _, body = sec.partition("\n")
        title = title.strip()
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]

        parts, buf = [], ""
        for p in paras:
            if buf and len(buf) + len(p) + 2 > max_chars:
                parts.append(buf)
                buf = p
            else:
                buf = f"{buf}\n\n{p}" if buf else p
        if buf:
            parts.append(buf)

        for i, part in enumerate(parts):
            chunks.append(Chunk(f"{slugify(title)}-{i}", source, title, part))
    return chunks