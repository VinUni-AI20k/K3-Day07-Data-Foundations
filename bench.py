"""Run a small, reproducible retrieval benchmark for the HUST corpus.

Examples:
    python3 bench.py --strategy heading --embedding mock
    python3 bench.py --strategy heading --embedding local

``mock`` is useful for checking the pipeline.  Use ``local`` when comparing
retrieval quality; it loads the multilingual sentence-transformers model.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ingest import build_knowledge_base
from src.chunking import HeadingSectionChunker, RecursiveChunker
from src.embeddings import LocalEmbedder, MockEmbedder


BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": (
            "Theo thông báo kế hoạch học tập HUST, giới hạn tín chỉ của sinh viên "
            "bình thường và sinh viên bị cảnh cáo học tập mức 2 hoặc 3 trong kỳ "
            "2026-2027 là gì?"
        ),
        "gold_answer": (
            "Mức đăng ký thông thường là 12-24 tín chỉ; sinh viên bị cảnh cáo "
            "học tập mức 2 hoặc 3 được đăng ký tối đa 14 tín chỉ."
        ),
        "expected_doc": "hust-study-plan-2026",
        "filter": {"audience": "student"},
    },
    {
        "id": 2,
        "query": "Quy trình đăng ký học phần dự định học trên CTT HUST gồm những bước nào?",
        "gold_answer": (
            "Đăng nhập CTT, chọn Đăng ký học tập rồi Đăng ký học phần, chọn học kỳ, "
            "chọn mã học phần và gửi đăng ký."
        ),
        "expected_doc": "hust-study-plan-2026",
        "filter": {"audience": "student"},
    },
    {
        "id": 3,
        "query": "HUST tính học phí của sinh viên theo cơ sở nào?",
        "gold_answer": (
            "Học phí được tính theo số tín chỉ sinh viên đăng ký trong học kỳ và "
            "thanh toán theo thời hạn thông báo."
        ),
        "expected_doc": "hust-tuition-by-credits",
        "filter": {"audience": "student"},
    },
    {
        "id": 4,
        "query": "Khi hệ thống báo lớp học đã hết chỗ, sinh viên HUST cần làm gì?",
        "gold_answer": (
            "Sinh viên cần điều chỉnh sang lớp khác còn chỗ trong thời gian hệ thống "
            "cho phép đăng ký hoặc điều chỉnh."
        ),
        "expected_doc": "hust-class-registration-20261",
        "filter": {"audience": "student"},
    },
    {
        "id": 5,
        "query": "Sinh viên SIE cần làm gì khi muốn đăng ký học phần thay thế?",
        "gold_answer": (
            "Liên hệ điều phối viên; học phần thay thế cần đúng tên, số tín chỉ hoặc "
            "có phê duyệt tương đương theo hướng dẫn của chương trình."
        ),
        "expected_doc": "hust-sie-course-substitution",
        "filter": {"audience": "sie-student"},
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark retrieval for the HUST corpus.")
    parser.add_argument(
        "--strategy",
        choices=("recursive", "heading"),
        default="heading",
        help="Chunking strategy to evaluate (default: heading).",
    )
    parser.add_argument(
        "--embedding",
        choices=("mock", "local"),
        default="mock",
        help="Embedding backend. Use local for a meaningful retrieval comparison.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/k3_university"),
        help="Directory containing the Markdown corpus.",
    )
    return parser.parse_args()


def make_chunker(strategy: str):
    if strategy == "heading":
        return HeadingSectionChunker(chunk_size=400)
    return RecursiveChunker(chunk_size=400)


def make_embedder(backend: str):
    if backend == "local":
        return LocalEmbedder()
    return MockEmbedder()


def run_benchmark(strategy: str, embedding: str, data_dir: Path) -> None:
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Corpus directory does not exist: {data_dir}")

    embedder = make_embedder(embedding)
    store = build_knowledge_base(
        str(data_dir), embedding_fn=embedder, chunker=make_chunker(strategy)
    )

    print("=" * 80)
    print("BENCHMARK RETRIEVAL RESULTS (HUST Academic Services Corpus)")
    print(f"Chunking strategy: {strategy}")
    print(f"Embedding backend: {embedding}")
    print("=" * 80)

    for item in BENCHMARK_QUERIES:
        results = store.search_with_filter(
            item["query"], top_k=3, metadata_filter=item["filter"]
        )
        doc_ids = [result["metadata"].get("doc_id") for result in results]

        print(f"\nQuery {item['id']}: {item['query']}")
        print(f"Filter applied: {item['filter']}")
        print(f"Gold answer: {item['gold_answer']}")
        print(f"Expected document: {item['expected_doc']}")
        print(f"Expected document in top-3: {item['expected_doc'] in doc_ids}")
        print("Top-3 retrieved chunks:")
        for index, result in enumerate(results, 1):
            doc_id = result["metadata"].get("doc_id")
            score = result["score"]
            snippet = result["content"][:100].replace("\n", " ")
            print(f"  [{index}] doc_id={doc_id} | score={score:.4f} | snippet={snippet}...")

    print("\n" + "=" * 80)
    print(f"Total chunks in store: {store.get_collection_size()}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    arguments = parse_args()
    run_benchmark(arguments.strategy, arguments.embedding, arguments.data_dir)
