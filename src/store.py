from __future__ import annotations

from typing import Any, Callable

from .chunking import compute_similarity
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

            client = chromadb.EphemeralClient()
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except (ImportError, RuntimeError, ValueError):
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Create an isolated record without mutating the input document."""
        if not isinstance(doc, Document):
            raise TypeError("docs must contain Document instances")
        metadata = dict(doc.metadata)
        metadata.setdefault("doc_id", doc.id)
        record = {
            "id": doc.id,
            "storage_id": f"{doc.id}::{self._next_index}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": [float(value) for value in self._embedding_fn(doc.content)],
            "insertion_index": self._next_index,
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Run deterministic cosine-similarity search over *records*."""
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if not records:
            return []
        query_embedding = [float(value) for value in self._embedding_fn(query)]
        scored = [
            (
                compute_similarity(query_embedding, record["embedding"]),
                record,
            )
            for record in records
        ]
        scored.sort(key=lambda item: (-item[0], item[1]["insertion_index"]))
        return [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": dict(record["metadata"]),
                "score": float(score),
            }
            for score, record in scored[:top_k]
        ]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        records = [self._make_record(doc) for doc in docs]
        self._store.extend(records)
        if self._use_chroma and self._collection is not None and records:
            self._collection.add(
                ids=[record["storage_id"] for record in records],
                documents=[record["content"] for record in records],
                embeddings=[record["embedding"] for record in records],
                metadatas=[record["metadata"] for record in records],
            )

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        metadata_filter = metadata_filter or {}
        records = [
            record
            for record in self._store
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        matching = [record for record in self._store if record["metadata"].get("doc_id") == doc_id]
        if not matching:
            return False
        matching_ids = {record["storage_id"] for record in matching}
        self._store = [record for record in self._store if record["storage_id"] not in matching_ids]
        if self._use_chroma and self._collection is not None:
            self._collection.delete(ids=sorted(matching_ids))
        return True
