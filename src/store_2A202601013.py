from __future__ import annotations

import copy
from typing import Any, Callable

from .chunking import _dot, compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        text_content = doc.content if hasattr(doc, "content") else getattr(doc, "text", "")
        return {
            "id": doc.id,
            "content": text_content,
            "metadata": doc.metadata,
            "document": doc,
            "embedding": self._embedding_fn(text_content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not records:
            return []
        query_embedding = self._embedding_fn(query)
        results = []
        for record in records:
            similarity = compute_similarity(query_embedding, record["embedding"])
            results.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "document": record["document"],
                "score": similarity,
                "similarity": similarity,
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.
        """
        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)
            if self._use_chroma and self._collection is not None:
                try:
                    self._collection.add(
                        ids=[record["id"]],
                        documents=[record["content"]],
                        embeddings=[record["embedding"]],
                        metadatas=[record["metadata"]] if record["metadata"] else None,
                    )
                except Exception:
                    pass

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict | None = None) -> list[dict[str, Any]]:
        """
        Search with optional metadata pre-filtering.
        """
        if metadata_filter:
            filtered = [
                r for r in self._store
                if all(r["metadata"].get(k) == v for k, v in metadata_filter.items())
            ]
        else:
            filtered = self._store
        return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.
        """
        initial_size = len(self._store)
        self._store = [
            r for r in self._store
            if r["id"] != doc_id and r["metadata"].get("doc_id") != doc_id
        ]
        removed_count = initial_size - len(self._store)
        if self._use_chroma and self._collection is not None and removed_count > 0:
            try:
                self._collection.delete(ids=[doc_id])
            except Exception:
                pass
        return removed_count > 0
