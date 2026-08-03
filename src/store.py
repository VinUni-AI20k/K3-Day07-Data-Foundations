from __future__ import annotations

import os
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

            # CHROMA_PERSIST_DIR (tùy chọn, xem .env.example): có thì lưu xuống đĩa,
            # không có thì dùng client trong RAM cho mỗi lần chạy.
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "").strip()
            if persist_dir:
                client = chromadb.PersistentClient(path=persist_dir)
            else:
                client = chromadb.EphemeralClient()
                # EphemeralClient chia sẻ DB trong RAM giữa các lần khởi tạo trong
                # cùng process, nên collection cũ vẫn còn dữ liệu. Xóa đi để mỗi
                # store mới bắt đầu từ trạng thái rỗng, giống nhánh in-memory.
                try:
                    client.delete_collection(name=collection_name)
                except Exception:
                    pass  # chưa tồn tại -> không cần xóa
            # hnsw:space=cosine -> distance = 1 - cosine, nên score quy đổi được
            # về đúng thang cosine của nhánh in-memory (xem _query_chroma).
            self._collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        """Chuẩn hóa một `Document` thành record để lưu (kèm vector đã nhúng).

        Hai điểm quan trọng:
        - `doc_id` luôn được bơm vào metadata (nếu chưa có) để `delete_document()`
          và lọc theo tài liệu vẫn hoạt động khi caller không truyền metadata.
        - `id` lưu trữ có thêm số thứ tự tăng dần, nhờ đó hai chunk/tài liệu
          trùng id gốc vẫn là hai record riêng biệt (ChromaDB yêu cầu id duy nhất).
        """
        metadata = self._normalize_metadata(doc.metadata)
        metadata.setdefault("doc_id", doc.id)

        record = {
            "id": f"{doc.id}#{self._next_index}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Tìm kiếm tương tự trong RAM trên đúng tập `records` được truyền vào."""
        if not records or top_k <= 0:
            return []

        query_embedding = self._embedding_fn(query)
        # Mọi embedder trong lab (mock/local/openai) đều trả vector đã chuẩn hóa,
        # nên tích vô hướng chính là cosine similarity.
        scored = [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": record["metadata"],
                "score": _dot(query_embedding, record["embedding"]),
            }
            for record in records
        ]
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        records = [self._make_record(doc) for doc in docs]

        if self._use_chroma and self._collection is not None:
            self._collection.add(
                ids=[record["id"] for record in records],
                documents=[record["content"] for record in records],
                embeddings=[record["embedding"] for record in records],
                metadatas=[record["metadata"] for record in records],
            )
            return

        self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            return self._query_chroma(query, top_k)
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return int(self._collection.count())
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        if self._use_chroma and self._collection is not None:
            return self._query_chroma(query, top_k, where=self._build_where(metadata_filter))

        # Lọc TRƯỚC rồi mới xếp hạng: top_k được tính trên tập đã lọc, nên
        # bộ lọc không bị các chunk điểm cao ngoài phạm vi chiếm chỗ.
        matched = [
            record
            for record in self._store
            if all(record["metadata"].get(key) == value for key, value in metadata_filter.items())
        ]
        return self._search_records(query, matched, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            existing = self._collection.get(where={"doc_id": doc_id})
            ids = existing.get("ids") or []
            if not ids:
                return False
            self._collection.delete(ids=ids)
            return True

        remaining = [record for record in self._store if record["metadata"].get("doc_id") != doc_id]
        if len(remaining) == len(self._store):
            return False
        self._store = remaining
        return True

    def _query_chroma(self, query: str, top_k: int, where: dict | None = None) -> list[dict[str, Any]]:
        """Truy vấn ChromaDB và quy đổi distance về cùng thang điểm với nhánh in-memory."""
        if top_k <= 0:
            return []
        count = int(self._collection.count())
        if count == 0:
            return []

        response = self._collection.query(
            query_embeddings=[self._embedding_fn(query)],
            n_results=min(top_k, count),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {
                "id": chunk_id,
                "content": content,
                "metadata": dict(metadata or {}),
                "score": 1.0 - float(distance),  # cosine space: distance = 1 - cosine
            }
            for chunk_id, content, metadata, distance in zip(
                response["ids"][0],
                response["documents"][0],
                response["metadatas"][0],
                response["distances"][0],
            )
        ]

    @staticmethod
    def _normalize_metadata(metadata: dict | None) -> dict[str, Any]:
        """Ép metadata về các giá trị vô hướng (scalar) để lọc được nhất quán.

        `ingest.parse_front_matter()` dùng pyyaml khi có sẵn, nên `retrieved_at: 2026-08-02`
        trở thành `datetime.date` chứ không phải chuỗi. Hai hệ quả: ChromaDB từ chối
        giá trị không phải scalar, và `metadata_filter={"retrieved_at": "2026-08-02"}`
        sẽ không khớp vì đang so chuỗi với `date`. Ở đây quy đổi mọi giá trị lạ về
        `str()` (date -> "2026-08-02") và bỏ các khóa `None` (không dùng để lọc được).
        """
        normalized: dict[str, Any] = {}
        for key, value in (metadata or {}).items():
            if value is None:
                continue
            normalized[str(key)] = value if isinstance(value, (str, int, float, bool)) else str(value)
        return normalized

    @staticmethod
    def _build_where(metadata_filter: dict) -> dict:
        """Đổi filter phẳng thành cú pháp `where` của Chroma (nhiều khóa cần $and)."""
        clauses = [{key: value} for key, value in metadata_filter.items()]
        return clauses[0] if len(clauses) == 1 else {"$and": clauses}
