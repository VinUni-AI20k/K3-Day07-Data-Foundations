"""Benchmark retrieval quality with OpenAI embeddings."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.src_DoanNhatBinh_02018.chunking import FixedSizeChunker
from src.src_DoanNhatBinh_02018.embeddings import (
    OPENAI_EMBEDDING_MODEL,
    OpenAIEmbedder,
)


DATA_DIR = os.getenv("LAB_DATA_DIR", "data/k3_university")


def main() -> int:
    load_dotenv(override=False)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY chưa được thiết lập. "
            "Hãy đặt biến này hoặc thêm vào file .env."
        )

    model_name = os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL)
    embedder = OpenAIEmbedder(model_name=model_name)

    if "mock" in getattr(embedder, "_backend_name", "").lower():
        raise RuntimeError("Không được dùng mock embedding cho benchmark này.")

    store = build_knowledge_base(
        DATA_DIR,
        embedding_fn=embedder,
        chunker=FixedSizeChunker(chunk_size=500, overlap=50),
    )

    queries = [
        {
            "id": 1,
            "query": "Mỗi học kỳ, sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ?",
            "gold_doc": "k3-course-registration",
            "gold_keywords": ["08", "16", "tín chỉ"],
        },
        {
            "id": 2,
            "query": "Nếu sinh viên còn nợ học phí của học kỳ trước thì điều gì xảy ra khi đăng ký học kỳ tiếp theo?",
            "gold_doc": "k3-tuition-payment",
            "gold_keywords": ["không được đăng ký học phần"],
        },
        {
            "id": 3,
            "query": "Sinh viên đạt học bổng khuyến khích học tập Loại A được nhận bao nhiêu phần trăm học phí đã nộp?",
            "gold_doc": "k3-scholarship-policy",
            "gold_keywords": ["50%"],
            "filter": {"audience": "student"},
        },
        {
            "id": 4,
            "query": "Chi phí ở ký túc xá phòng 8 sinh viên là bao nhiêu mỗi tháng?",
            "gold_doc": "k3-dormitory-policy",
            "gold_keywords": ["350.000"],
        },
        {
            "id": 5,
            "query": "Khu tự học ở tầng 6 của thư viện mở cửa vào những khung giờ nào?",
            "gold_doc": "k3-library-services",
            "gold_keywords": ["6h30", "22h"],
        },
    ]

    total = 0
    print(f"Backend: {embedder._backend_name}")
    print(f"Model: {model_name}")
    print(f"Data: {DATA_DIR}")
    print(f"Collection size: {store.get_collection_size()} chunks")

    for item in queries:
        if item.get("filter"):
            results = store.search_with_filter(
                item["query"],
                top_k=3,
                metadata_filter=item["filter"],
            )
        else:
            results = store.search(item["query"], top_k=3)

        relevant = [
            result
            for result in results
            if result["metadata"].get("doc_id") == item["gold_doc"]
        ]
        joined = " ".join(result["content"].lower() for result in results)
        answer_found = all(
            keyword.lower() in joined for keyword in item["gold_keywords"]
        )

        score = 2 if relevant and answer_found else 1 if relevant else 0
        total += score

        print("\n" + "=" * 80)
        print(f"Q{item['id']}: {item['query']}")
        print(f"Relevant in top-3: {bool(relevant)}")
        print(f"Gold keywords found: {answer_found}")
        print(f"Score: {score}/2")

        for rank, result in enumerate(results, 1):
            print(
                f"{rank}. score={result['score']:.4f}, "
                f"id={result['id']}, "
                f"doc_id={result['metadata'].get('doc_id')}"
            )
            print("   " + result["content"][:180].replace("\n", " "))

    print("\n" + "=" * 80)
    print(f"TOTAL: {total}/10")
    print(f"AVERAGE: {total / len(queries):.2f}/2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
