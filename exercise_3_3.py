#!/usr/bin/env python3
"""
Exercise 3.3: Predict cosine similarity for 5 sentence pairs.
"""
import os
os.environ["LAB_SOLUTION_PACKAGE"] = "src.src_NguyenMinhThu_01631"

from src.src_NguyenMinhThu_01631.chunking import compute_similarity
from src.src_NguyenMinhThu_01631.embeddings import _mock_embed

# 5 sentence pairs for prediction
PAIRS = [
    ("Hướng dẫn đăng ký học phần trực tuyến.", "Sinh viên đăng ký môn học trên cổng thông tin."),
    ("Thư viện cho phép gia hạn sách.", "Người học có thể gia hạn tài liệu mượn."),
    ("Học phí được nộp theo học kỳ.", "Ký túc xá có quy định giờ đóng cổng."),
    ("Vector store tìm kiếm theo embedding.", "Cơ sở dữ liệu vector hỗ trợ tìm kiếm tương tự."),
    ("Mưa lớn vào buổi chiều.", "Thuật toán chunking chia văn bản thành các đoạn."),
]

def run_predictions():
    print("=" * 70)
    print("EXERCISE 3.3: Predict cosine similarity for 5 pairs")
    print("=" * 70)
    print()

    results = []
    for i, (sent_a, sent_b) in enumerate(PAIRS, 1):
        # Get embeddings
        emb_a = _mock_embed(sent_a)
        emb_b = _mock_embed(sent_b)

        # Compute similarity
        similarity = compute_similarity(emb_a, emb_b)

        results.append({
            "pair": i,
            "sent_a": sent_a[:50] + "...",
            "sent_b": sent_b[:50] + "...",
            "similarity": similarity,
        })

        print(f"Pair {i}:")
        print(f"  A: {sent_a}")
        print(f"  B: {sent_b}")
        print(f"  Similarity: {similarity:.4f}")
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results:
        score = r["similarity"]
        if score > 0.5:
            rating = "✓ HIGH"
        elif score > 0:
            rating = "~ MEDIUM"
        else:
            rating = "✗ LOW/NEGATIVE"
        print(f"Pair {r['pair']}: {score:7.4f} {rating}")

if __name__ == "__main__":
    run_predictions()
