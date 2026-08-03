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
            import chromadb  # noqa: F401

            # Khởi tạo chromadb client + collection
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Tạo một bản ghi lưu trữ chuẩn hóa cho một tài liệu."""
        embedding = self._embedding_fn(doc.content)
        return {
            "id": doc.id,
            "content": doc.content,
            "embedding": embedding,
            "metadata": dict(doc.metadata) if doc.metadata else {},
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Thực hiện tìm kiếm tương tự trong bộ nhớ trên các records được cung cấp."""
        if not records:
            return []

        query_embedding = self._embedding_fn(query)

        # Tính điểm similarity cho mỗi record
        scored = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored.append({
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": score,
            })

        # Sắp xếp theo score giảm dần và trả về top_k
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

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
                    ids=[str(self._next_index)],
                    documents=[doc.content],
                    embeddings=[record["embedding"]],
                    metadatas=[{"doc_id": doc.id, **record["metadata"]}],
                )
            else:
                self._store.append(record)

            self._next_index += 1

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count()),
            )
            output = []
            for i, doc_content in enumerate(results["documents"][0]):
                output.append({
                    "content": doc_content,
                    "score": 1.0 - results["distances"][0][i],
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                })
            return output

        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if metadata_filter is None:
            # Không lọc: tìm kiếm trên toàn bộ
            return self._search_records(query, self._store, top_k)

        # Lọc trước theo metadata
        filtered_records = []
        for record in self._store:
            match = all(
                record["metadata"].get(key) == value
                for key, value in metadata_filter.items()
            )
            if match:
                filtered_records.append(record)

        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        original_size = len(self._store)
        self._store = [
            record for record in self._store
            if record["id"] != doc_id
        ]
        return len(self._store) < original_size
