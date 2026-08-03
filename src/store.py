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
            # pyrefly: ignore [missing-import]
            import chromadb  # noqa: F401
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(name=self._collection_name)
             
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": doc.metadata,
            "embedding": self._embedding_fn(doc.content)
        }
    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        from .chunking import compute_similarity
        query_emb = self._embedding_fn(query)
        scored_records = []
        for r in records:
            score = compute_similarity(query_emb, r["embedding"])
            r_copy = r.copy()
            r_copy["score"] = score
            scored_records.append((score, r_copy))
        scored_records.sort(key=lambda x: x[0], reverse=True)
        return [r for score, r in scored_records[:top_k]]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if self._use_chroma and self._collection:
            self._collection.add(
                ids=[doc.id for doc in docs],
                documents=[doc.content for doc in docs],
                metadatas=[doc.metadata for doc in docs],
                embeddings=[self._embedding_fn(doc.content) for doc in docs]
            )
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
            
            out = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    out.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                    })
            return out
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
        if metadata_filter is None:
            metadata_filter = {}
            
        if self._use_chroma and self._collection:
            query_emb = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_emb], 
                n_results=top_k, 
                where=metadata_filter
            )
            
            out = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    out.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                    })
            return out
        else:
            filtered_records = [
                r for r in self._store 
                if all(r.get("metadata", {}).get(k) == v for k, v in metadata_filter.items())
            ]
            return self._search_records(query, filtered_records, top_k)


    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection:
            try:
                initial_count = self._collection.count()
                self._collection.delete(ids=[doc_id])
                try:
                    self._collection.delete(where={"doc_id": doc_id})
                except Exception:
                    pass
                return self._collection.count() < initial_count
            except Exception:
                return False
        else:
            initial_len = len(self._store)
            self._store = [r for r in self._store if r.get("id") != doc_id and r.get("metadata", {}).get("doc_id") != doc_id]
            return len(self._store) < initial_len

