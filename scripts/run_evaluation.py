"""
Run the 5 group evaluation questions on the personal solution
using RecursiveChunker (chunk_size=300) — the strategy chosen by Nguyen The Anh.

Usage:
    python scripts/run_evaluation.py
"""
from __future__ import annotations

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import _mock_embed

DATA_DIR = "data/k3_university"

# The 5 group evaluation questions (must match REPORT_NHOM.md — Phần 3)
QUESTIONS = [
    {
        "id": 1,
        "query": "Thủ tục đăng ký học phần qua cổng học vụ như thế nào?",
        "expected_doc_id": "k3-course-registration",
        "metadata_filter": None,
    },
    {
        "id": 2,
        "query": "Làm thế nào để gia hạn sách mượn tại thư viện?",
        "expected_doc_id": "k3-library-renewal",
        "metadata_filter": None,
    },
    {
        "id": 3,
        "query": "Sinh viên cần tuân thủ quy định gì khi mượn sách thư viện?",
        "expected_doc_id": "k3-library-borrowing",
        "metadata_filter": {"audience": "student"},
    },
    {
        "id": 4,
        "query": "Điều kiện để được xét học bổng khuyến khích học tập là gì?",
        "expected_doc_id": "k3-scholarship",
        "metadata_filter": None,
    },
    {
        "id": 5,
        "query": "Quy định về ở ký túc xá yêu cầu sinh viên làm gì trước khi nhập ký túc?",
        "expected_doc_id": "k3-dormitory-rules",
        "metadata_filter": None,
    },
]


def demo_llm(prompt: str) -> str:
    """Simple LLM stub for RAG demo."""
    preview = prompt[:300].replace("\n", " ")
    return f"[DEMO LLM] Trả lời dựa trên ngữ cảnh: {preview}..."


def main() -> int:
    print("=== Building knowledge base with RecursiveChunker(chunk_size=300) ===\n")
    chunker = RecursiveChunker(chunk_size=300)
    store = build_knowledge_base(DATA_DIR, embedding_fn=_mock_embed, chunker=chunker)
    print(f"Đã nạp {store.get_collection_size()} chunk vào EmbeddingStore\n")

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    relevant_in_top3_count = 0

    for q in QUESTIONS:
        print(f"--- Câu hỏi {q['id']}: {q['query']} ---")
        print(f"    (Expected doc_id: {q['expected_doc_id']})")

        if q["metadata_filter"]:
            results = store.search_with_filter(
                q["query"], top_k=3, metadata_filter=q["metadata_filter"]
            )
            print(f"    (Metadata filter: {q['metadata_filter']})")
        else:
            results = store.search(q["query"], top_k=3)

        top1_relevant = False
        top3_relevant = False

        for idx, r in enumerate(results, start=1):
            doc_id = r["metadata"].get("doc_id", "unknown")
            score = r["score"]
            content_preview = r["content"][:120].replace("\n", " ")
            is_relevant = doc_id == q["expected_doc_id"]
            if is_relevant:
                top3_relevant = True
                if idx == 1:
                    top1_relevant = True

            print(f"    Top-{idx}: score={score:.4f} doc_id={doc_id} relevant={is_relevant}")
            print(f"           content: {content_preview}...")

        if top3_relevant:
            relevant_in_top3_count += 1

        # Agent answer
        answer = agent.answer(q["query"], top_k=3)
        print(f"    Agent answer: {answer[:200]}...")
        print(f"    Top-1 relevant: {top1_relevant} | Top-3 relevant: {top3_relevant}")
        print()

    print(f"\n=== Tổng kết ===")
    print(f"Số câu hỏi trả về chunk có liên quan trong top-3: {relevant_in_top3_count} / 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
