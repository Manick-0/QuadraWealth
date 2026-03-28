"""
QuadraWealth RAG Engine
ChromaDB-powered vector store for financial news embedding and retrieval.
Used by the Stocks module to provide context-aware recommendations.
"""
import json
import os
import chromadb
from pathlib import Path

from backend.config import settings

# Global reference
_collection = None
_client = None


async def init_rag_engine():
    """Initialize ChromaDB and seed with financial news snippets."""
    global _collection, _client

    persist_dir = settings.CHROMA_PERSIST_DIR
    os.makedirs(persist_dir, exist_ok=True)

    _client = chromadb.PersistentClient(path=persist_dir)
    _collection = _client.get_or_create_collection(
        name="financial_news",
        metadata={"hnsw:space": "cosine"},
    )

    # Seed if empty
    if _collection.count() == 0:
        await _seed_news_snippets()

    print(f"✅ RAG Engine initialized — {_collection.count()} documents in vector store")


async def _seed_news_snippets():
    """Load and embed financial news snippets into ChromaDB."""
    data_path = Path(__file__).parent.parent / "data" / "news_snippets.json"
    if not data_path.exists():
        print("⚠️  No news snippets found, RAG will operate with empty context")
        return

    with open(data_path, "r") as f:
        snippets = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for i, snippet in enumerate(snippets):
        documents.append(snippet["text"])
        metadatas.append({
            "category": snippet.get("category", "general"),
            "sector": snippet.get("sector", "general"),
            "sentiment": snippet.get("sentiment", "neutral"),
            "date": snippet.get("date", "2026-03-28"),
        })
        ids.append(f"news_{i}")

    _collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    print(f"📰 Seeded {len(documents)} news snippets into vector store")


def query_relevant_news(
    query_text: str,
    n_results: int = 5,
    sector_filter: str | None = None,
) -> list[dict]:
    """
    Query the vector store for news relevant to a given text.
    Returns list of {text, category, sector, sentiment, distance}.
    """
    if _collection is None or _collection.count() == 0:
        return []

    where_filter = None
    if sector_filter:
        where_filter = {"sector": sector_filter}

    try:
        results = _collection.query(
            query_texts=[query_text],
            n_results=min(n_results, _collection.count()),
            where=where_filter,
        )
    except Exception:
        # Fallback without filter if sector doesn't exist
        results = _collection.query(
            query_texts=[query_text],
            n_results=min(n_results, _collection.count()),
        )

    output = []
    if results and results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "text": doc,
                "category": meta.get("category", ""),
                "sector": meta.get("sector", ""),
                "sentiment": meta.get("sentiment", "neutral"),
                "distance": dist,
            })

    return output
