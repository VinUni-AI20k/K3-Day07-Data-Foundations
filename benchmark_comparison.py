#!/usr/bin/env python3
"""
Compare FixedSizeChunker vs RecursiveChunker on benchmark queries.
"""
import os
from pathlib import Path

os.environ["LAB_SOLUTION_PACKAGE"] = "src.src_NguyenMinhThu_01631"

from src.src_NguyenMinhThu_01631.chunking import FixedSizeChunker, RecursiveChunker
from src.src_NguyenMinhThu_01631.agent import KnowledgeBaseAgent
from src.src_NguyenMinhThu_01631.embeddings import _mock_embed
from ingest import build_knowledge_base

QUERIES = [
    {
        "id": 1,
        "question": "Mỗi học kỳ, sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ?",
        "gold": "Tối thiểu 08 tín chỉ, tối đa 16 tín chỉ",
    },
    {
        "id": 2,
        "question": "Nếu sinh viên còn nợ học phí của học kỳ trước thì điều gì xảy ra khi đăng ký học kỳ tiếp theo?",
        "gold": "không được đăng ký học phần",
    },
    {
        "id": 3,
        "question": "Sinh viên đạt học bổng khuyến khích học tập Loại A được nhận mức học bổng bằng bao nhiêu phần trăm?",
        "gold": "50%",
    },
    {
        "id": 4,
        "question": "Chi phí ở ký túc xá phòng 8 sinh viên là bao nhiêu mỗi tháng?",
        "gold": "350.000 VNĐ",
    },
    {
        "id": 5,
        "question": "Khu tự học ở tầng 6 của thư viện mở cửa vào những khung giờ nào?",
        "gold": "6h30–22h",
    },
]

def eval_query(store, query_text, gold_answer):
    """Check if any of top-3 results contain gold answer."""
    results = store.search(query_text, top_k=3)
    for result in results:
        content = result.get("content", "").lower()
        if gold_answer.lower() in content:
            return True
    return False

def run_comparison():
    data_dir = Path("data/k3_university")

    # Test with FixedSizeChunker
    print("=" * 70)
    print("BASELINE: FixedSizeChunker(chunk_size=500, overlap=50)")
    print("=" * 70)

    chunker1 = FixedSizeChunker(chunk_size=500, overlap=50)
    store1 = build_knowledge_base(data_dir, embedding_fn=_mock_embed, chunker=chunker1)
    print(f"Total chunks: {store1.get_collection_size()}\n")

    correct_fixed = 0
    for q in QUERIES:
        is_correct = eval_query(store1, q["question"], q["gold"])
        correct_fixed += int(is_correct)
        print(f"Q{q['id']}: {'✓' if is_correct else '✗'}")

    print(f"Score: {correct_fixed}/5 questions\n")

    # Test with RecursiveChunker
    print("=" * 70)
    print("STRATEGY 2: RecursiveChunker(separators=[...], chunk_size=500)")
    print("=" * 70)

    chunker2 = RecursiveChunker(chunk_size=500)
    store2 = build_knowledge_base(data_dir, embedding_fn=_mock_embed, chunker=chunker2)
    print(f"Total chunks: {store2.get_collection_size()}\n")

    correct_recursive = 0
    for q in QUERIES:
        is_correct = eval_query(store2, q["question"], q["gold"])
        correct_recursive += int(is_correct)
        print(f"Q{q['id']}: {'✓' if is_correct else '✗'}")

    print(f"Score: {correct_recursive}/5 questions\n")

    # Summary
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print(f"FixedSizeChunker: {correct_fixed}/5 = {correct_fixed*20}%")
    print(f"RecursiveChunker: {correct_recursive}/5 = {correct_recursive*20}%")
    print()
    if correct_recursive > correct_fixed:
        print("=> RecursiveChunker performs better")
    elif correct_fixed > correct_recursive:
        print("=> FixedSizeChunker performs better")
    else:
        print("=> Both strategies perform equally")

if __name__ == "__main__":
    run_comparison()
