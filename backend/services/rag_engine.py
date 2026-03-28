"""
QuadraWealth RAG Engine
ChromaDB-powered vector store for financial news embedding and retrieval.
Falls back to simple keyword matching when ChromaDB is unavailable (e.g., on Render free tier).
"""
import json
import os
from pathlib import Path

from backend.config import settings

# Try to import ChromaDB — optional dependency
try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("ℹ️  ChromaDB not available — using keyword fallback for RAG")

# Global reference
_collection = None
_client = None
_news_snippets = []  # Fallback: raw list for keyword search


async def init_rag_engine():
    """Initialize ChromaDB and seed with financial news snippets."""
    global _collection, _client, _news_snippets

    # Load raw snippets (used by both paths)
    data_path = Path(__file__).parent.parent / "data" / "news_snippets.json"
    if data_path.exists():
        with open(data_path, "r") as f:
            _news_snippets = json.load(f)

    if HAS_CHROMADB:
        try:
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
            return
        except Exception as e:
            print(f"⚠️  ChromaDB init failed ({e}), using keyword fallback")

    # Fallback path
    print(f"✅ RAG Engine initialized (keyword mode) — {len(_news_snippets)} snippets loaded")


async def _seed_news_snippets():
    """Load and embed financial news snippets into ChromaDB."""
    if not _news_snippets:
        print("⚠️  No news snippets found, RAG will operate with empty context")
        return

    documents = []
    metadatas = []
    ids = []

    for i, snippet in enumerate(_news_snippets):
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
    Query for news relevant to a given text.
    Uses ChromaDB vector search when available, keyword matching otherwise.
    """
    # ChromaDB path
    if _collection is not None and _collection.count() > 0:
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

    # Keyword fallback
    return _keyword_search(query_text, n_results, sector_filter)


def _keyword_search(
    query_text: str,
    n_results: int = 5,
    sector_filter: str | None = None,
) -> list[dict]:
    """Simple keyword-based search over news snippets."""
    if not _news_snippets:
        return []

    query_words = set(query_text.lower().split())
    scored = []

    for snippet in _news_snippets:
        # Filter by sector if specified
        if sector_filter and snippet.get("sector", "").lower() != sector_filter.lower():
            continue

        text = snippet.get("text", "").lower()
        # Score = number of query words found in the snippet
        score = sum(1 for w in query_words if w in text)
        if score > 0:
            scored.append((score, snippet))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "text": s["text"],
            "category": s.get("category", ""),
            "sector": s.get("sector", ""),
            "sentiment": s.get("sentiment", "neutral"),
            "distance": 1.0 - (score / max(len(query_words), 1)),
        }
        for score, s in scored[:n_results]
    ]
