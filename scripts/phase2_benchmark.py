from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ingest import chunk_document, load_documents
from src import (
    LOCAL_EMBEDDING_MODEL,
    EmbeddingStore,
    FixedSizeChunker,
    SentenceChunker,
    _mock_embed,
)


DEFAULT_DATA_DIR = ROOT / "data" / "quy-dinh-sinh-vien-hust"
DEFAULT_QUERIES = ROOT / "report" / "benchmark_queries.json"
DEFAULT_OUTPUT = ROOT / "report" / "benchmark_results.json"


class MarkdownHeadingChunker:
    def __init__(self, chunk_size: int = 1200) -> None:
        self.chunk_size = chunk_size
        self.fallback = FixedSizeChunker(chunk_size=chunk_size, overlap=150)

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        sections = re.split(r"(?m)(?=^#{1,6}\s+)", text)
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            heading_match = re.match(r"^(#{1,6}\s+[^\n]+)\n?", section)
            heading = heading_match.group(1) if heading_match else ""
            body = section[heading_match.end() :].strip() if heading_match else section
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            prefix = f"{heading}\n" if heading else ""
            available = max(100, self.chunk_size - len(prefix))
            for piece in FixedSizeChunker(chunk_size=available, overlap=min(150, available // 4)).chunk(body):
                chunks.append(f"{prefix}{piece}".strip())
        return chunks


class BatchedLocalEmbedder:
    def __init__(self, model_name: str = LOCAL_EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.cache: dict[str, list[float]] = {}

    def prepare(self, texts: list[str]) -> None:
        unseen = list(dict.fromkeys(text for text in texts if text not in self.cache))
        if not unseen:
            return
        embeddings = self.model.encode(
            unseen,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        for text, embedding in zip(unseen, embeddings):
            self.cache[text] = [float(value) for value in embedding]

    def __call__(self, text: str) -> list[float]:
        if text not in self.cache:
            self.prepare([text])
        return self.cache[text]


def load_queries(path: Path) -> list[dict]:
    queries = json.loads(path.read_text(encoding="utf-8"))
    if len(queries) != 5:
        raise ValueError(f"Expected exactly 5 benchmark queries, found {len(queries)}")
    return queries


def evaluate_strategy(name: str, chunker, documents, queries, embedding_fn) -> dict:
    chunks = []
    for document in documents:
        chunks.extend(chunk_document(document, chunker))
    if hasattr(embedding_fn, "prepare"):
        embedding_fn.prepare(
            [chunk.content for chunk in chunks]
            + [benchmark["query"] for benchmark in queries]
        )
    store = EmbeddingStore(collection_name=f"phase2_{name}", embedding_fn=embedding_fn)
    store.add_documents(chunks)
    query_results = []
    points = 0
    reciprocal_rank_total = 0.0

    for benchmark in queries:
        metadata_filter = benchmark.get("metadata_filter")
        if metadata_filter:
            results = store.search_with_filter(
                benchmark["query"], top_k=3, metadata_filter=metadata_filter
            )
            unfiltered_results = store.search(benchmark["query"], top_k=3)
        else:
            results = store.search(benchmark["query"], top_k=3)
            unfiltered_results = results

        gold_doc_id = benchmark["gold_doc_id"]
        rank = next(
            (
                index
                for index, result in enumerate(results, start=1)
                if result["metadata"].get("doc_id") == gold_doc_id
            ),
            None,
        )
        query_points = 2 if rank == 1 else 1 if rank in {2, 3} else 0
        points += query_points
        reciprocal_rank_total += 1.0 / rank if rank else 0.0
        query_results.append(
            {
                "id": benchmark["id"],
                "rank": rank,
                "unfiltered_rank": next(
                    (
                        index
                        for index, result in enumerate(unfiltered_results, start=1)
                        if result["metadata"].get("doc_id") == gold_doc_id
                    ),
                    None,
                ),
                "points": query_points,
                "metadata_filter": metadata_filter,
                "top_3": [
                    {
                        "rank": index,
                        "doc_id": result["metadata"].get("doc_id"),
                        "chunk_index": result["metadata"].get("chunk_index"),
                        "score": round(float(result["score"]), 6),
                        "content_preview": result["content"][:240].replace("\n", " "),
                    }
                    for index, result in enumerate(results, start=1)
                ],
            }
        )

    return {
        "strategy": name,
        "chunk_count": len(chunks),
        "average_chunk_length": round(
            sum(len(chunk.content) for chunk in chunks) / len(chunks), 2
        ),
        "hit_at_3": sum(result["rank"] is not None for result in query_results),
        "mrr": round(reciprocal_rank_total / len(queries), 4),
        "points_out_of_10": points,
        "queries": query_results,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run the K3 Phase 2 retrieval benchmark.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--provider", choices=("local", "mock"), default="local")
    args = parser.parse_args()

    documents = load_documents(args.data_dir)
    queries = load_queries(args.queries)
    embedding_fn = BatchedLocalEmbedder() if args.provider == "local" else _mock_embed
    strategies = {
        "A_fixed_900_overlap_150": FixedSizeChunker(chunk_size=900, overlap=150),
        "B_sentence_8": SentenceChunker(max_sentences_per_chunk=8),
        "C_markdown_heading_1200": MarkdownHeadingChunker(chunk_size=1200),
    }
    results = {
        "provider": args.provider,
        "data_dir": str(args.data_dir),
        "document_count": len(documents),
        "query_count": len(queries),
        "scoring": "2 points for rank 1, 1 point for rank 2-3, 0 otherwise",
        "strategies": [
            evaluate_strategy(name, chunker, documents, queries, embedding_fn)
            for name, chunker in strategies.items()
        ],
    }
    args.output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
