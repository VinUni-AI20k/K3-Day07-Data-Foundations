"""bench.py — chạy 5 câu hỏi đánh giá của nhóm trên nhiều chiến lược chunking.

    python3 bench.py                      # chạy mọi chiến lược có sẵn
    python3 bench.py --strategy fixed     # chỉ một chiến lược
    EMBEDDING_PROVIDER=local python3 bench.py

Chấm ở **mức chunk**, không chỉ ở mức `doc_id`: mỗi câu hỏi khai báo trước một
CHUỖI BẰNG CHỨNG phải xuất hiện trong context top-3. Một chiến lược hoàn toàn
có thể chiếm cả 3 slot bằng đúng tài liệu gold mà không chunk nào chứa câu trả
lời — chấm bằng `doc_id` sẽ không phát hiện ra điều đó.

Chọn chuỗi bằng chứng là cụm NGẮN NHẤT chứng minh đáp án có mặt, không phải chi
tiết ngoại vi: ban đầu nhóm dùng "Bộ Y tế" cho Q5 và điều đó phạt oan
HeadingChunker 1 điểm, vì chunk trả lời đúng lại không chứa cụm đó.
"""
from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src import (
    EMBEDDING_PROVIDER_ENV,
    FixedSizeChunker,
    KnowledgeBaseAgent,
    LocalEmbedder,
    RecursiveChunker,
    SentenceChunker,
    _mock_embed,
)

DATA_DIR = "data/k3_university"

# (câu hỏi, metadata_filter, doc_id gold, chuỗi bằng chứng)
QUERIES = [
    ("Sinh viên đăng ký học phần ở website nào và cần lưu ý gì trước khi đăng ký?",
     None, "huong-dan-dang-ky-hoc-phan", "dkhp.iuh.edu.vn"),
    ("Sinh viên nộp học phí trực tuyến bằng những cách nào?",
     None, "huong-dan-nop-hoc-phi-truc-tuyen", "tất cả ngân hàng"),
    ("Mức học bổng khuyến khích học tập tối đa là bao nhiêu?",
     None, "che-do-hoc-bong-sinh-vien", "130%"),
    ("Kho sách ngoại văn của thư viện nằm ở tầng nào?",
     None, "huong-dan-su-dung-thu-vien", "Lầu 3"),
    ("Sinh viên bị ốm phải điều trị dài ngày thì việc học được giải quyết thế nào?",
     {"audience": "student"}, "quy-dinh-nghi-hoc-tam-thoi", "nghỉ học tạm thời"),
]


def build_strategies() -> dict:
    strategies = {
        "fixed": ("FixedSize(500,50)", FixedSizeChunker(chunk_size=500, overlap=50)),
        "sentence": ("Sentence(3 câu)", SentenceChunker(max_sentences_per_chunk=3)),
        "recursive": ("Recursive(500)", RecursiveChunker(chunk_size=500)),
    }
    try:  # chiến lược custom của thành viên 3 — chỉ có nếu file tồn tại
        from src.heading_chunker import HeadingChunker

        strategies["heading"] = ("Heading(800)", HeadingChunker(chunk_size=800))
    except ImportError:
        pass
    return strategies


def select_embedder():
    load_dotenv(override=False)
    if os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower() == "local":
        try:
            return LocalEmbedder()
        except Exception:
            print("Local embedder không sẵn sàng; tạm dùng mock.")
    return _mock_embed


def grade(results: list[dict], gold: str, evidence: str) -> tuple[int, str]:
    """2đ nếu bằng chứng ở chunk hạng 1, 1đ nếu ở hạng 2-3 (hoặc chỉ có gold doc), 0đ nếu không."""
    if not results:
        return 0, "không có kết quả"
    docs = [r["metadata"].get("doc_id") for r in results]
    hits = [i for i, r in enumerate(results, start=1) if evidence.lower() in r["content"].lower()]
    if not hits:
        return (1, "có gold doc nhưng KHÔNG chunk nào chứa đáp án") if gold in docs else (0, "trượt hoàn toàn")
    return (2, "đáp án ở hạng 1") if hits[0] == 1 else (1, f"đáp án ở hạng {hits[0]}, không phải hạng 1")


def run(label: str, chunker, embedder, index: int) -> tuple[int, int]:
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker,
                                 collection_name=f"bench_{index}")
    agent = KnowledgeBaseAgent(store=store, llm_fn=lambda prompt: prompt)
    print(f"\n{'=' * 72}\n## {label} — {store.get_collection_size()} chunk\n{'=' * 72}")

    doc_total = chunk_total = 0
    for number, (query, mfilter, gold, evidence) in enumerate(QUERIES, start=1):
        results = store.search_with_filter(query, top_k=3, metadata_filter=mfilter) if mfilter \
            else store.search(query, top_k=3)
        points, reason = grade(results, gold, evidence)
        chunk_total += points
        docs = [r["metadata"].get("doc_id") for r in results]
        doc_total += 2 if docs and docs[0] == gold else (1 if gold in docs else 0)

        print(f"\nQ{number} [{points}đ] {reason}   (cần: {evidence!r})")
        for rank, r in enumerate(results, start=1):
            mark = "✓" if evidence.lower() in r["content"].lower() else " "
            print(f"  {mark} {rank}. {r['score']:.3f}  {r['metadata'].get('doc_id')}"
                  f"  chunk={r['metadata'].get('chunk_index')}")

        if mfilter:  # A/B: bộ lọc có thực sự đổi gì không?
            plain = store.search(query, top_k=3)
            same = [r["id"] for r in plain] == [r["id"] for r in results]
            print(f"   A/B filter: {'GIỐNG HỆT — bộ lọc không đổi gì' if same else 'KHÁC'}")
            if not same:
                for rank, r in enumerate(plain, start=1):
                    print(f"      không lọc {rank}. {r['score']:.3f}  {r['metadata'].get('doc_id')}"
                          f"  audience={r['metadata'].get('audience')}")

        agent.answer(query, top_k=3)  # kiểm tra đường RAG chạy được đầu-cuối

    print(f"\n-> {label}: doc-level {doc_total}/10 | CHUNK-LEVEL {chunk_total}/10")
    return doc_total, chunk_total


def main() -> int:
    strategies = build_strategies()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strategy", choices=sorted(strategies), help="chỉ chạy một chiến lược")
    args = parser.parse_args()

    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", type(embedder).__name__)
    print(f"Backend nhúng: {backend}")
    if backend == "mock embeddings fallback":
        print("CẢNH BÁO: mock cho điểm gần như ngẫu nhiên — đặt EMBEDDING_PROVIDER=local "
              "để so sánh chiến lược có ý nghĩa.")

    chosen = {args.strategy: strategies[args.strategy]} if args.strategy else strategies
    summary = {}
    for index, (label, chunker) in enumerate(chosen.values()):
        summary[label] = run(label, chunker, embedder, index)

    print(f"\n{'=' * 72}\n## TỔNG HỢP\n{'=' * 72}")
    print(f"{'Chiến lược':22}{'doc-level':>12}{'chunk-level':>13}")
    for label, (doc_total, chunk_total) in summary.items():
        print(f"{label:22}{doc_total:>9}/10{chunk_total:>10}/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
