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

        try:
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection(
                name=self._collection_name
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Build a normalized record containing an ID, content, metadata,
        and embedding.
        """
        content = getattr(doc, "content", None)

        if content is None:
            content = getattr(doc, "text", "")

        metadata = getattr(doc, "metadata", None) or {}
        metadata = dict(metadata)

        document_id = (
            getattr(doc, "id", None)
            or getattr(doc, "doc_id", None)
            or metadata.get("id")
            or metadata.get("doc_id")
        )

        if document_id is not None:
            metadata.setdefault("doc_id", str(document_id))

        record_id = f"{self._collection_name}-{self._next_index}"
        self._next_index += 1

        content = str(content)
        embedding = self._embedding_fn(content)

        return {
            "id": record_id,
            "content": content,
            "text": content,
            "metadata": metadata,
            "embedding": embedding,
        }

    def _search_records(
        self,
        query: str,
        records: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """
        Run an in-memory dot-product similarity search.
        """
        if not query or not query.strip() or top_k <= 0:
            return []

        query_embedding = self._embedding_fn(query)

        scored_records: list[dict[str, Any]] = []

        for record in records:
            embedding = record.get("embedding", [])

            if len(query_embedding) != len(embedding):
                continue

            score = _dot(query_embedding, embedding)

            scored_records.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "text": record["content"],
                    "metadata": dict(record.get("metadata", {})),
                    "score": score,
                }
            )

        scored_records.sort(
            key=lambda record: record["score"],
            reverse=True,
        )

        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(
            ids=[...],
            documents=[...],
            embeddings=[...]
        ).

        For in-memory: append dicts to self._store.
        """
        if not docs:
            return

        records = [self._make_record(doc) for doc in docs]

        if self._use_chroma and self._collection is not None:
            try:
                self._collection.add(
                    ids=[record["id"] for record in records],
                    documents=[record["content"] for record in records],
                    embeddings=[record["embedding"] for record in records],
                    metadatas=[record["metadata"] for record in records],
                )
                return
            except Exception:
                # Fall back to memory if Chroma fails at runtime.
                self._use_chroma = False
                self._collection = None

        self._store.extend(records)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding versus all
        stored embeddings.
        """
        if not query or not query.strip() or top_k <= 0:
            return []

        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            output: list[dict[str, Any]] = []

            for index, record_id in enumerate(ids):
                content = documents[index] if index < len(documents) else ""
                metadata = (
                    metadatas[index]
                    if index < len(metadatas) and metadatas[index] is not None
                    else {}
                )
                distance = (
                    distances[index]
                    if index < len(distances)
                    else None
                )

                # Chroma normally returns distance, where smaller is better.
                # Convert it into a score where larger is better.
                score = -distance if distance is not None else 0.0

                output.append(
                    {
                        "id": record_id,
                        "content": content,
                        "text": content,
                        "metadata": metadata,
                        "score": score,
                    }
                )

            return output

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return int(self._collection.count())

        return len(self._store)

    def search_with_filter(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity
        search.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        if not query or not query.strip() or top_k <= 0:
            return []

        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=metadata_filter,
                include=["documents", "metadatas", "distances"],
            )

            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            output: list[dict[str, Any]] = []

            for index, record_id in enumerate(ids):
                content = documents[index] if index < len(documents) else ""
                metadata = (
                    metadatas[index]
                    if index < len(metadatas) and metadatas[index] is not None
                    else {}
                )
                distance = (
                    distances[index]
                    if index < len(distances)
                    else None
                )

                output.append(
                    {
                        "id": record_id,
                        "content": content,
                        "text": content,
                        "metadata": metadata,
                        "score": -distance if distance is not None else 0.0,
                    }
                )

            return output

        filtered_records = [
            record
            for record in self._store
            if all(
                record.get("metadata", {}).get(key) == expected_value
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
                include=[],
            )

            matching_ids = matching.get("ids", [])

            if not matching_ids:
                return False

            self._collection.delete(ids=matching_ids)
            return True

        original_size = len(self._store)

        self._store = [
            record
            for record in self._store
            if str(record.get("metadata", {}).get("doc_id")) != str(doc_id)
        ]

        return len(self._store) < original_size