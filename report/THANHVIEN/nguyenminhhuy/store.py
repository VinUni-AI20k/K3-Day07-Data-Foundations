from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
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
        self._client = None
        try:
            import chromadb

            self._client = chromadb.Client()
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata)
        metadata.setdefault("doc_id", doc.id)

        record = {
            "id": f"{doc.id}::{self._next_index}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

        self._next_index += 1
        return record

    def _search_records(
    self,
    query: str,
    records: list[dict[str, Any]],
    top_k: int,
    ) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []

        query_embedding = self._embedding_fn(query)
        results: list[dict[str, Any]] = []

        for record in records:
            score = _dot(query_embedding, record["embedding"])

            results.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": dict(record["metadata"]),
                    "score": float(score),
                }
            )

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        for doc in docs:
            record = self._make_record(doc)

            if self._use_chroma and self._collection is not None:
                self._collection.add(
                    ids=[record["id"]],
                    documents=[record["content"]],
                    metadatas=[record["metadata"]],
                    embeddings=[record["embedding"]],
                )
            else:
                self._store.append(record)

    def search(
    self,
    query: str,
    top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if top_k <= 0 or self.get_collection_size() == 0:
            return []

        if not self._use_chroma or self._collection is None:
            return self._search_records(
                query=query,
                records=self._store,
                top_k=top_k,
            )

        stored_data = self._collection.get(
            include=["documents", "metadatas", "embeddings"],
        )

        ids = stored_data.get("ids", [])
        documents = stored_data.get("documents", [])
        metadatas = stored_data.get("metadatas", [])
        embeddings = stored_data.get("embeddings", [])

        records: list[dict[str, Any]] = []

        for record_id, content, metadata, embedding in zip(
            ids,
            documents,
            metadatas,
            embeddings,
        ):
            records.append(
                {
                    "id": record_id,
                    "content": content,
                    "metadata": metadata or {},
                    "embedding": list(embedding),
                }
            )

        return self._search_records(
            query=query,
            records=records,
            top_k=top_k,
        )

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()

        return len(self._store)

    def search_with_filter(
    self,
    query: str,
    top_k: int = 3,
    metadata_filter: dict | None = None,
    ) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if metadata_filter is None:
            return self.search(query=query, top_k=top_k)

        if top_k <= 0 or self.get_collection_size() == 0:
            return []

        if not self._use_chroma or self._collection is None:
            records = self._store
        else:
            stored_data = self._collection.get(
                include=["documents", "metadatas", "embeddings"],
            )

            records = [
                {
                    "id": record_id,
                    "content": content,
                    "metadata": metadata or {},
                    "embedding": list(embedding),
                }
                for record_id, content, metadata, embedding in zip(
                    stored_data.get("ids", []),
                    stored_data.get("documents", []),
                    stored_data.get("metadatas", []),
                    stored_data.get("embeddings", []),
                )
            ]

        filtered_records = [
            record
            for record in records
            if all(
                record["metadata"].get(key) == expected_value
                for key, expected_value in metadata_filter.items()
            )
        ]

        return self._search_records(
            query=query,
            records=filtered_records,
            top_k=top_k,
        )

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            matching = self._collection.get(
                where={"doc_id": doc_id},
            )
            matching_ids = matching.get("ids", [])

            if not matching_ids:
                return False

            self._collection.delete(ids=matching_ids)
            return True

        size_before = len(self._store)

        self._store = [
            record
            for record in self._store
            if record["metadata"].get("doc_id") != doc_id
        ]

        return len(self._store) < size_before
