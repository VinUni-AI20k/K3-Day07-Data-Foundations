from __future__ import annotations

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

        try:
            import chromadb  # noqa: F401

            self._collection = chromadb.Client().get_or_create_collection(name=self._collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """
        Create a record for storage, including embedding and metadata.

        Returns a dict with keys: 'id', 'content', 'embedding', 'metadata'.
        """
        embedding = self._embedding_fn(doc.content)
        record = {
            "id": doc.id,
            "content": doc.content,
            "embedding": embedding,
            "metadata": doc.metadata,
        }
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """
        Search among a list of records for the top_k most similar to the query.

        Returns a list of dicts with keys: 'id', 'content', 'metadata', 'score'.
        """
        query_embedding = self._embedding_fn(query)
        scored_records = []
        for record in records:
            similarity = compute_similarity(query_embedding, record["embedding"])
            scored_records.append({**record, "score": similarity})

        scored_records.sort(key=lambda r: r["score"], reverse=True)
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        for doc in docs:
            record = self._make_record(doc)
            if self._use_chroma and self._collection is not None:
                self._collection.add(
                    ids=[record["id"]],
                    documents=[record["content"]],
                    embeddings=[record["embedding"]],
                    metadatas=[record["metadata"]],
                )
            else:
                self._store.append(record)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
            )
            # ChromaDB returns a dict with keys: 'ids', 'documents', 'metadatas', 'distances'
            return [
                {
                    "id": id_,
                    "content": content,
                    "metadata": metadata,
                    "score": 1 - distance,  # assuming distance is in [0, 1]
                }
                for id_, content, metadata, distance in zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        else:
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        else:
            return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if metadata_filter is None:
            metadata_filter = {}

        if self._use_chroma and self._collection is not None:
            # ChromaDB supports filtering via the 'where' parameter
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                where=metadata_filter,
            )
            return [
                {
                    "id": id_,
                    "content": content,
                    "metadata": metadata,
                    "score": 1 - distance,  # assuming distance is in [0, 1]
                }
                for id_, content, metadata, distance in zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        else:
            # In-memory filtering
            filtered_records = [
                record for record in self._store
                if all(record["metadata"].get(k) == v for k, v in metadata_filter.items())
            ]
            return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            # ChromaDB supports deletion by IDs
            self._collection.delete(ids=[doc_id])
            return True  # Assume deletion was successful
        else:
            initial_count = len(self._store)
            self._store = [record for record in self._store if record["id"] != doc_id]
            return len(self._store) < initial_count
