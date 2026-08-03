from __future__ import annotations

from typing import Any, Callable

from .chunking_2A202601037 import _dot
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
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=self._collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        from .chunking_2A202601037 import compute_similarity
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": doc.metadata,
            "embedding": self._embedding_fn(doc.content)
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        from .chunking_2A202601037 import compute_similarity
        query_emb = self._embedding_fn(query)
        results = []
        for r in records:
            score = compute_similarity(query_emb, r["embedding"])
            results.append({
                "id": r["id"],
                "content": r["content"],
                "metadata": r["metadata"],
                "score": score
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if self._use_chroma and self._collection:
            ids = []
            documents = []
            metadatas = []
            embeddings = []
            for doc in docs:
                ids.append(doc.id)
                documents.append(doc.content)
                metadatas.append(doc.metadata)
                embeddings.append(self._embedding_fn(doc.content))
            self._collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        else:
            for doc in docs:
                self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection:
            query_emb = self._embedding_fn(query)
            results = self._collection.query(query_embeddings=[query_emb], n_results=top_k)
            ret = []
            if results and results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    ret.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": 1.0 - results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                    })
            return ret
        else:
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma and self._collection:
            query_emb = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_emb], 
                n_results=top_k, 
                where=metadata_filter if metadata_filter else None
            )
            ret = []
            if results and results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    ret.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": 1.0 - results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                    })
            return ret
        else:
            records = self._store
            if metadata_filter:
                filtered_records = []
                for r in records:
                    match = True
                    for k, v in metadata_filter.items():
                        if r["metadata"].get(k) != v:
                            match = False
                            break
                    if match:
                        filtered_records.append(r)
                records = filtered_records
            return self._search_records(query, records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection:
            try:
                count_before = self._collection.count()
                self._collection.delete(ids=[doc_id])
                return self._collection.count() < count_before
            except Exception:
                return False
        else:
            initial_len = len(self._store)
            new_store = []
            for r in self._store:
                if r["id"] == doc_id or str(r.get("id", "")).startswith(f"{doc_id}_") or r.get("metadata", {}).get("doc_id") == doc_id:
                    continue
                new_store.append(r)
            deleted = len(new_store) < initial_len
            self._store = new_store
            return deleted
