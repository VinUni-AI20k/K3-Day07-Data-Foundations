#!/usr/bin/env python3
"""Reproducible benchmark for the K3 group report.

The script compares three member strategies on the same HCMUT corpus and the
same five benchmark questions. It prints JSON so measured values can be copied
into REPORT_NHOM.md without relying on hand-written scores.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ingest import chunk_document, load_documents
from src import (
    ChunkingStrategyComparator,
    EmbeddingStore,
    FixedSizeChunker,
    LocalEmbedder,
    MockEmbedder,
    RecursiveChunker,
    SentenceChunker,
)


DATA_DIR = ROOT_DIR / "data/k3_university"


class HeadingSectionChunker:
    """Keep Markdown headings with their sections, then split oversized sections."""

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []

        sections = [part.strip() for part in re.split(r"(?=^#{1,6}\s)", text, flags=re.MULTILINE) if part.strip()]
        chunks: list[str] = []
        buffer = ""
        for section in sections:
            if len(section) > self.chunk_size:
                if buffer:
                    chunks.append(buffer)
                    buffer = ""
                chunks.extend(self._fallback.chunk(section))
                continue

            candidate = section if not buffer else f"{buffer}\n\n{section}"
            if len(candidate) <= self.chunk_size:
                buffer = candidate
            else:
                chunks.append(buffer)
                buffer = section

        if buffer:
            chunks.append(buffer)
        return chunks


class CorpusTfidfEmbedder:
    """Deterministic local retrieval backend fitted only on the group corpus."""

    def __init__(self, corpus: list[str]) -> None:
        self._backend_name = "local TF-IDF char_wb 3-5 grams"
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            lowercase=True,
            norm="l2",
        )
        self.vectorizer.fit(corpus)

    def __call__(self, text: str) -> list[float]:
        return self.vectorizer.transform([text]).toarray()[0].astype(float).tolist()


@dataclass(frozen=True)
class BenchmarkQuery:
    query_id: str
    question: str
    gold_answer: str
    expected_doc_id: str
    support_terms: tuple[str, ...]
    metadata_filter: dict | None = None


BENCHMARKS = [
    BenchmarkQuery(
        "Q1",
        "Sinh viên đại học được đăng ký tối đa bao nhiêu tín chỉ trong đợt 1?",
        "Sinh viên đại học được đăng ký tối đa 25 tín chỉ trong đợt 1.",
        "hcmut-course-registration-process",
        ("25", "tín chỉ"),
    ),
    BenchmarkQuery(
        "Q2",
        "Mã hủy T khi đăng ký môn học có nghĩa là gì?",
        "Mã T nghĩa là trùng giờ trong thời khóa biểu.",
        "hcmut-registration-cancellation-codes",
        ("trùng giờ",),
    ),
    BenchmarkQuery(
        "Q3",
        "Sinh viên được đăng ký rút môn trong thời gian nào và môn rút có tính học phí không?",
        "Đăng ký từ tuần thứ hai đến trước tuần thi cuối kỳ một tuần; môn rút vẫn tính học phí.",
        "hcmut-course-withdrawal",
        ("tuần thứ hai", "một tuần", "học phí"),
    ),
    BenchmarkQuery(
        "Q4",
        "Học phí học kỳ dự thính phải thanh toán khi nào?",
        "Học phí học kỳ dự thính được thanh toán trong tuần đầu tiên của học kỳ dự thính.",
        "hcmut-tuition-payment",
        ("tuần đầu tiên", "dự thính"),
    ),
    BenchmarkQuery(
        "Q5",
        "Đơn vị nào xử lý yêu cầu mở thêm lớp và điều chỉnh thời khóa biểu ở đợt 2?",
        "Sinh viên liên hệ giảng viên hoặc khoa; nếu khoa đồng ý thì gửi đề nghị tới Phòng Đào tạo, nơi xử lý khoảng một đến hai ngày làm việc.",
        "hcmut-course-registration-process",
        ("liên hệ", "khoa", "một đến hai ngày"),
        {"audience": "student"},
    ),
]


def normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(character for character in normalized if unicodedata.category(character) != "Mn")


def has_support(text: str, terms: tuple[str, ...]) -> bool:
    normalized_text = normalize(text)
    return all(normalize(term) in normalized_text for term in terms)


def make_embedder(provider: str, documents):
    if provider == "local":
        return LocalEmbedder()
    if provider == "tfidf":
        return CorpusTfidfEmbedder([document.content for document in documents])
    return MockEmbedder()


def baseline_comparison(documents) -> dict:
    selected_ids = {
        "hcmut-course-registration-rules",
        "hcmut-course-registration-process",
        "hcmut-tuition-payment",
    }
    comparator = ChunkingStrategyComparator()
    output = {}
    for document in documents:
        if document.id not in selected_ids:
            continue
        comparison = comparator.compare(document.content, chunk_size=300)
        output[document.id] = {
            name: {
                "count": stats["count"],
                "avg_length": round(stats["avg_length"], 1),
            }
            for name, stats in comparison.items()
        }
    return output


def evaluate_strategy(name: str, chunker, documents, embedder) -> dict:
    chunks = []
    for document in documents:
        chunks.extend(chunk_document(document, chunker))

    store = EmbeddingStore(collection_name=f"group_{name}", embedding_fn=embedder)
    store.add_documents(chunks)
    query_results = []
    total_score = 0

    for benchmark in BENCHMARKS:
        if benchmark.metadata_filter:
            results = store.search_with_filter(
                benchmark.question,
                top_k=3,
                metadata_filter=benchmark.metadata_filter,
            )
        else:
            results = store.search(benchmark.question, top_k=3)

        relevant_rank = next(
            (
                rank
                for rank, result in enumerate(results, start=1)
                if result["metadata"].get("doc_id") == benchmark.expected_doc_id
            ),
            None,
        )
        supporting_rank = next(
            (
                rank
                for rank, result in enumerate(results, start=1)
                if result["metadata"].get("doc_id") == benchmark.expected_doc_id
                and has_support(result["content"], benchmark.support_terms)
            ),
            None,
        )
        answer_supported = supporting_rank is not None
        score = 2 if supporting_rank == 1 else 1 if supporting_rank or relevant_rank else 0
        total_score += score

        query_results.append(
            {
                "id": benchmark.query_id,
                "question": benchmark.question,
                "gold_answer": benchmark.gold_answer,
                "expected_doc_id": benchmark.expected_doc_id,
                "metadata_filter": benchmark.metadata_filter,
                "relevant_rank": relevant_rank,
                "supporting_rank": supporting_rank,
                "answer_supported": answer_supported,
                "score": score,
                "top3": [
                    {
                        "rank": rank,
                        "doc_id": result["metadata"].get("doc_id"),
                        "chunk_index": result["metadata"].get("chunk_index"),
                        "score": round(result["score"], 4),
                        "preview": result["content"][:180].replace("\n", " "),
                    }
                    for rank, result in enumerate(results, start=1)
                ],
            }
        )

    filter_benchmark = BENCHMARKS[-1]
    filtered = store.search_with_filter(
        filter_benchmark.question,
        top_k=3,
        metadata_filter=filter_benchmark.metadata_filter,
    )
    unfiltered = store.search(filter_benchmark.question, top_k=3)

    return {
        "strategy": name,
        "chunk_count": len(chunks),
        "avg_chunk_length": round(sum(len(chunk.content) for chunk in chunks) / len(chunks), 1),
        "retrieval_score": total_score,
        "queries": query_results,
        "q5_filter_comparison": {
            "unfiltered_doc_ids": [result["metadata"].get("doc_id") for result in unfiltered],
            "filtered_doc_ids": [result["metadata"].get("doc_id") for result in filtered],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("local", "tfidf", "mock"), default="local")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    documents = load_documents(DATA_DIR)
    embedder = make_embedder(args.provider, documents)
    strategies = {
        "nguyen_huy_nghia_fixed": FixedSizeChunker(chunk_size=500, overlap=75),
        "pham_the_dung_sentence": SentenceChunker(max_sentences_per_chunk=3),
        "pham_van_luu_heading": HeadingSectionChunker(chunk_size=500),
    }

    payload = {
        "provider": getattr(embedder, "_backend_name", args.provider),
        "document_count": len(documents),
        "baseline": baseline_comparison(documents),
        "strategies": [
            evaluate_strategy(name, chunker, documents, embedder)
            for name, chunker in strategies.items()
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
