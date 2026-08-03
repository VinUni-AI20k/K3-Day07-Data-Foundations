"""Run the reproducible five-query local multilingual retrieval benchmark."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest import build_knowledge_base  # noqa: E402
from src import FixedSizeChunker, LocalEmbedder, RecursiveChunker, SentenceChunker  # noqa: E402

DATA_DIR = ROOT / "data" / "k3_university"
QUERY_PATH = ROOT / "evaluation" / "benchmark_queries.json"
RESULT_PATH = ROOT / "evaluation" / "benchmark_results.json"
TOP_K = 3


class HeadingRecursiveChunker:
    """Split Markdown at headings, then recursively split oversized sections."""

    def __init__(self, chunk_size: int = 450) -> None:
        self.recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        sections = [section for section in re.split(r"(?m)(?=^#{1,6}\s)", text) if section.strip()]
        chunks: list[str] = []
        for section in sections or [text]:
            chunks.extend(self.recursive.chunk(section))
        return chunks

STRATEGIES = [
    {
        "strategy_id": "S1_RECURSIVE_450",
        "member": "Trương Đình Khoa",
        "chunker": RecursiveChunker(chunk_size=450),
        "parameters": {"chunk_size": 450, "separators": ["\\n\\n", "\\n", ". ", " ", ""]},
    },
    {
        "strategy_id": "S2_FIXED_450_50",
        "member": "Diêm Công Thành",
        "chunker": FixedSizeChunker(chunk_size=450, overlap=50),
        "parameters": {"chunk_size": 450, "chunk_overlap": 50},
    },
    {
        "strategy_id": "S3_SENTENCE_3",
        "member": "Nguyễn Quang Huy",
        "chunker": SentenceChunker(max_sentences_per_chunk=3),
        "parameters": {"max_sentences_per_chunk": 3},
    },
    {
        "strategy_id": "S1B_HEADING_RECURSIVE_450",
        "member": "Trương Đình Khoa (thử nghiệm bổ sung)",
        "chunker": HeadingRecursiveChunker(chunk_size=450),
        "parameters": {"heading_pattern": "^#{1,6}\\s", "chunk_size": 450},
    },
]


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def is_relevant(result: dict[str, Any], query: dict[str, Any]) -> bool:
    document_id = result.get("metadata", {}).get("doc_id")
    content = normalize(str(result.get("content", "")))
    return document_id in query["expected_document_ids"] and all(
        normalize(term) in content for term in query["expected_evidence"]
    )


def coherence_score(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    starts_cleanly = stripped[0].isupper() or stripped[0].isdigit() or stripped[0] in "#`"
    ends_cleanly = stripped[-1] in ".!?…:`" or stripped.endswith("đồng")
    return 2 if starts_cleanly and ends_cleanly else 1


def run() -> dict[str, Any]:
    queries = json.loads(QUERY_PATH.read_text(encoding="utf-8"))
    if len(queries) != 5:
        raise ValueError(f"Benchmark must contain exactly 5 queries, found {len(queries)}")

    embedder = LocalEmbedder()
    probe = embedder("Kiểm tra embedding tiếng Việt")
    if "mock" in embedder._backend_name.casefold():
        raise RuntimeError("Local embedder unexpectedly fell back to mock")

    output: dict[str, Any] = {
        "environment": {
            "python_version": sys.version.split()[0],
            "python_executable": sys.executable,
            "embedding_backend": "local",
            "embedding_model": embedder.model_name,
            "actual_backend": embedder._backend_name,
            "vector_dimension": len(probe),
            "fallback": False,
            "top_k": TOP_K,
            "query_count": len(queries),
            "corpus_document_count": len(list(DATA_DIR.glob("*.md"))),
        },
        "strategies": [],
    }

    for config in STRATEGIES:
        store = build_knowledge_base(
            DATA_DIR,
            embedding_fn=embedder,
            chunker=config["chunker"],
            collection_name=config["strategy_id"].lower(),
        )
        traces: list[dict[str, Any]] = []
        for query in queries:
            metadata_filter = query.get("metadata_filter")
            unfiltered = store.search(query["question"], top_k=TOP_K)
            results = (
                store.search_with_filter(query["question"], top_k=TOP_K, metadata_filter=metadata_filter)
                if metadata_filter
                else unfiltered
            )
            ranked: list[dict[str, Any]] = []
            first_relevant_rank = 0
            for rank, result in enumerate(results, start=1):
                relevant = is_relevant(result, query)
                if relevant and not first_relevant_rank:
                    first_relevant_rank = rank
                ranked.append(
                    {
                        "rank": rank,
                        "chunk_id": result["id"],
                        "document_id": result["metadata"].get("doc_id"),
                        "title": result["metadata"].get("title"),
                        "category": result["metadata"].get("category"),
                        "source_url": result["metadata"].get("source_url"),
                        "score": round(float(result["score"]), 6),
                        "relevant": relevant,
                        "coherence": coherence_score(result["content"]),
                        "evidence_text": result["content"],
                    }
                )
            relevant_count = sum(1 for result in ranked if result["relevant"])
            unfiltered_rank = next(
                (rank for rank, result in enumerate(unfiltered, 1) if is_relevant(result, query)), 0
            )
            traces.append(
                {
                    "query_id": query["id"],
                    "question": query["question"],
                    "gold_answer": query["gold_answer"],
                    "expected_document_ids": query["expected_document_ids"],
                    "metadata_filter": metadata_filter,
                    "results": ranked,
                    "first_relevant_rank": first_relevant_rank,
                    "unfiltered_first_relevant_rank": unfiltered_rank,
                    "hit_at_1": first_relevant_rank == 1,
                    "hit_at_3": first_relevant_rank > 0,
                    "reciprocal_rank": round(1 / first_relevant_rank, 6) if first_relevant_rank else 0.0,
                    "precision_at_3": round(relevant_count / TOP_K, 6),
                    "grounding_quality": 2 if first_relevant_rank == 1 else (1 if first_relevant_rank else 0),
                    "grounded_answer": query["gold_answer"] if first_relevant_rank else None,
                }
            )

        count = len(traces)
        coherence_values = [r["coherence"] for trace in traces for r in trace["results"]]
        metrics = {
            "hit_at_1": round(sum(t["hit_at_1"] for t in traces) / count, 4),
            "hit_at_3": round(sum(t["hit_at_3"] for t in traces) / count, 4),
            "mrr": round(sum(t["reciprocal_rank"] for t in traces) / count, 4),
            "precision_at_3": round(sum(t["precision_at_3"] for t in traces) / count, 4),
            "coherence": round(sum(coherence_values) / len(coherence_values), 4),
            "grounding": round(sum(t["grounding_quality"] for t in traces) / count, 4),
            "metadata_filter_helped": sum(
                1
                for t in traces
                if t["metadata_filter"] and t["first_relevant_rank"] and (
                    not t["unfiltered_first_relevant_rank"]
                    or t["first_relevant_rank"] < t["unfiltered_first_relevant_rank"]
                )
            ),
        }
        output["strategies"].append(
            {
                "strategy_id": config["strategy_id"],
                "member": config["member"],
                "parameters": config["parameters"],
                "chunk_count": store.get_collection_size(),
                "metrics": metrics,
                "traces": traces,
            }
        )

    RESULT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    output = run()
    print(json.dumps({
        "environment": output["environment"],
        "strategies": [
            {
                "strategy_id": item["strategy_id"],
                "member": item["member"],
                "chunk_count": item["chunk_count"],
                "metrics": item["metrics"],
            }
            for item in output["strategies"]
        ],
        "result_path": str(RESULT_PATH),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
