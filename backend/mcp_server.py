from mcp.server.mcpserver import MCPServer

from app import mcp_tools
from app.database import get_db
from app.rag.embedder import Embedder
from app.rag.store import INDEX_PATH, VectorStore

mcp = MCPServer("foodops")
_cache: dict = {}


@mcp.tool()
def search_restaurants(query: str, limit: int = 3) -> list[dict]:
    """Naam ya cuisine se FoodOps restaurants dhoondho (public data)."""
    gen = get_db()
    db = next(gen)
    try:
        return mcp_tools.search_restaurants(db, query, limit)
    finally:
        gen.close()


@mcp.tool()
def search_policies(query: str, limit: int = 3) -> list[dict]:
    """FoodOps policy docs se relevant passages (refund, delivery, cancellation, payment...)."""
    if not INDEX_PATH.exists():
        return [{"error": "Index nahi bana. Run: python -m app.rag.build_index"}]
    if "store" not in _cache:
        _cache["store"], _cache["emb"] = VectorStore.load(INDEX_PATH), Embedder()
    return mcp_tools.search_policies(_cache["store"], _cache["emb"], query, limit)


if __name__ == "__main__":
    mcp.run()  # default: stdio. print() mat karo, logging stderr par jaati hai