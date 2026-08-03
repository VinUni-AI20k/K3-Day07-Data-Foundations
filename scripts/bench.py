#!/usr/bin/env python3
"""
bench.py — Lab 7 K3 (UEH corpus).

Chốt 5 benchmark query + gold answer; mỗi thành viên chỉ đổi dòng chọn chunker
rồi chạy cùng corpus / cùng query / cùng embedder.

Usage:
    python scripts/bench.py
    python scripts/bench.py --chunker recursive --top-k 3
    python scripts/bench.py --query 5
    EMBEDDING_PROVIDER=local python scripts/bench.py

Copy bộ query này vào report/REPORT_NHOM.md. Không đổi query sau khi nhóm đã chạy.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, HeadingChunker, RecursiveChunker, SentenceChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.store import EmbeddingStore

DEFAULT_DATA_DIR = "data/ueh_university"


def _select_embedder():
    try:
        from dotenv import load_dotenv

        load_dotenv(override=False)
    except ImportError:
        pass

    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("Local embedder khong san sang; dung mock.")
            return _mock_embed
    if provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            print("OpenAI embedder khong san sang; dung mock.")
            return _mock_embed
    return _mock_embed


def demo_llm(prompt: str) -> str:
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] Generated answer from prompt preview: {preview}..."


@dataclass(frozen=True)
class BenchmarkQuery:
    """Một câu hỏi đánh giá với gold answer trích từ corpus."""

    id: int
    query: str
    gold_answer: str
    expected_doc_id: str
    kind: str
    metadata_filter: dict | None = None
    verify_keywords: tuple[str, ...] = ()

    def search(self, store: EmbeddingStore, top_k: int) -> list[dict]:
        if self.metadata_filter:
            return store.search_with_filter(self.query, top_k=top_k, metadata_filter=self.metadata_filter)
        return store.search(self.query, top_k=top_k)


# --- 5 benchmark queries (chốt nhóm) ---
# Đa dạng: ngoại lệ, điều kiện, quy trình, điều kiện+filter audience, số liệu+filter version.
# Query #4: cần filter audience=student — tài liệu faculty (quy định tư vấn học tập) cũng nhắc
# "kết quả rèn luyện", "khen thưởng–kỷ luật" gần nghĩa với điều kiện xét bổng → gây nhiễu.
# Query #5: corpus có ueh-dorm-fee-2025 và ueh-dorm-fee-2026-q3 cùng chủ đề Quý III
# (tháng 7,8,9) — cần filter document_version=2026-q3 mới trả lời đúng năm 2026.
BENCHMARK_QUERIES: tuple[BenchmarkQuery, ...] = (
    BenchmarkQuery(
        id=1,
        kind="ngoại lệ",
        query="Sinh viên có được đăng ký mã học phần đang chờ lịch thi hoặc chờ kết quả điểm thi không?",
        gold_answer="Không được phép đăng ký mã học phần đang chờ lịch thi hoặc chờ kết quả điểm thi.",
        expected_doc_id="ueh-course-registration-plan-hk-cuoi-2025",
        verify_keywords=("không được phép đăng ký", "chờ lịch thi"),
    ),
    BenchmarkQuery(
        id=2,
        kind="điều kiện",
        query="Sinh viên không nộp học phí đúng hạn trong kỳ đăng ký học kỳ cuối 2025 sẽ bị xử lý thế nào?",
        gold_answer="Bị xóa tên khỏi danh sách lớp đã đăng ký.",
        expected_doc_id="ueh-course-registration-plan-hk-cuoi-2025",
        verify_keywords=("xóa tên", "danh sách lớp"),
    ),
    BenchmarkQuery(
        id=3,
        kind="quy trình",
        query="Các bước đăng ký cấp thẻ sinh viên nhựa tại UEH là gì?",
        gold_answer=(
            "Bước 1: truy cập Cổng giao dịch điện tử UEH mục Đăng ký cấp thẻ sinh viên; "
            "Bước 2: điền thông tin; Bước 3: thanh toán 100,000 đồng/1 thẻ; "
            "Bước 4: Phòng CNTT in thẻ cuối ngày; "
            "Bước 5: nhận email và lấy thẻ tại A203 – 59C Nguyễn Đình Chiểu "
            "(chiều thứ 3 hoặc sáng thứ 5)."
        ),
        expected_doc_id="ueh-student-card-services",
        verify_keywords=("Cổng giao dịch điện tử", "100,000", "A203"),
    ),
    BenchmarkQuery(
        id=4,
        kind="điều kiện / filter audience",
        query="Điều kiện để sinh viên UEH được xét cấp học bổng khuyến khích học tập là gì?",
        gold_answer=(
            "Đang trong thời gian 8 học kỳ chính; kết quả học tập và rèn luyện từ loại khá trở lên; "
            "không bị kỷ luật từ mức khiển trách trở lên; đạt từ 5 điểm trở lên tất cả học phần; "
            "số tín chỉ đăng ký >= số tín chỉ theo kế hoạch đào tạo."
        ),
        expected_doc_id="ueh-scholarship-regulation",
        metadata_filter={"audience": "student"},
        verify_keywords=("loại khá", "khiển trách", "5 điểm"),
    ),
    BenchmarkQuery(
        id=5,
        kind="số liệu / filter document_version",
        query="Thời gian thanh toán nội trú phí KTX UEH Quý III (tháng 7, 8, 9) là khi nào?",
        gold_answer="Từ 00h00 ngày 01/7/2026 đến 23h59 ngày 13/7/2026.",
        expected_doc_id="ueh-dorm-fee-2026-q3",
        metadata_filter={"document_version": "2026-q3"},
        verify_keywords=("01/7/2026", "13/7/2026"),
    ),
)


def _select_chunker(name: str):
    # DÒNG chiến lược: mỗi thành viên đổi tham số / class chunker tại đây (qua --chunker hoặc sửa mặc định).
    chunkers = {
        "fixed_size": FixedSizeChunker(chunk_size=500, overlap=50),
        "sentences": SentenceChunker(max_sentences_per_chunk=3),
        "recursive": RecursiveChunker(chunk_size=500),
        "heading": HeadingChunker(max_chunk_size=1500, include_parents=True),
    }
    if name not in chunkers:
        raise SystemExit(f"Chunker không hợp lệ: {name}. Chọn: {', '.join(chunkers)}")
    return chunkers[name]


def _doc_id_in_top_k(results: list[dict], expected_doc_id: str, top_k: int) -> tuple[bool, int | None]:
    for rank, item in enumerate(results[:top_k], start=1):
        if item.get("metadata", {}).get("doc_id") == expected_doc_id:
            return True, rank
    return False, None


def _keywords_in_text(text: str, keywords: tuple[str, ...]) -> bool:
    if not keywords:
        return True
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def run_benchmark(
    data_dir: str,
    chunker_name: str = "recursive",
    top_k: int = 3,
    query_ids: list[int] | None = None,
    llm_fn: Callable[[str], str] | None = None,
) -> int:
    data_path = Path(data_dir)
    if not data_path.is_dir():
        print(f"Không tìm thấy corpus: {data_dir}")
        return 1

    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    chunker = _select_chunker(chunker_name)

    print("=== Lab 7 bench.py ===")
    print(f"Corpus     : {data_dir}")
    print(f"Chunker    : {chunker_name} ({chunker.__class__.__name__})")
    print(f"Embedder   : {backend}")
    print(f"Top-k      : {top_k}")
    if backend == "mock embeddings fallback":
        print("Canh bao   : mock embedder — ket qua retrieval khong phan anh ngữ nghia.")
        print("             Dat EMBEDDING_PROVIDER=local de benchmark co y nghia.\n")
    else:
        print()

    # 1) Chọn chunker (ở trên) — đây là chỗ duy nhất khác giữa thành viên.
    # 2) Nạp corpus qua ingest (không viết lại pipeline).
    store = build_knowledge_base(data_dir, embedding_fn=embedder, chunker=chunker)
    agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn or demo_llm)
    print(f"Da nap {store.get_collection_size()} chunk vao store.\n")

    selected = BENCHMARK_QUERIES
    if query_ids:
        wanted = set(query_ids)
        selected = tuple(q for q in BENCHMARK_QUERIES if q.id in wanted)
        if not selected:
            print(f"Khong tim thay query id: {query_ids}")
            return 1

    hits_top1 = 0
    hits_topk = 0

    # 3) Chạy 5 query: top-3 + agent answer
    for item in selected:
        print("=" * 72)
        print(f"#{item.id} [{item.kind}] {item.query}")
        if item.metadata_filter:
            print(f"    filter: {item.metadata_filter}")
        print(f"    gold  : {item.gold_answer}")
        print(f"    expect: {item.expected_doc_id}")

        results = item.search(store, top_k=top_k)
        if not results:
            print("    >>> Khong co ket qua retrieval.")
            print()
            continue

        in_topk, rank = _doc_id_in_top_k(results, item.expected_doc_id, top_k)
        if in_topk:
            hits_topk += 1
            if rank == 1:
                hits_top1 += 1

        for index, result in enumerate(results[:top_k], start=1):
            doc_id = result.get("metadata", {}).get("doc_id", "?")
            marker = " <-- expected" if doc_id == item.expected_doc_id else ""
            preview = result["content"][:140].replace("\n", " ")
            print(f"    Top-{index} score={result['score']:.4f} doc_id={doc_id}{marker}")
            print(f"            {preview}...")

        top1 = results[0]
        kw_ok = _keywords_in_text(top1["content"], item.verify_keywords)
        status = []
        status.append("top-k OK" if in_topk else "top-k MISS")
        status.append("keywords OK" if kw_ok else "keywords MISS")
        print(f"    [{', '.join(status)}]")

        # Dùng đúng kết quả đã (có thể) filter — tránh agent.search() bỏ qua metadata_filter.
        if not results:
            answer = "No relevant context found in the knowledge base."
        else:
            context_blocks = []
            for index, result in enumerate(results[:top_k], start=1):
                meta = result.get("metadata", {})
                doc_id = meta.get("doc_id") or "unknown"
                context_blocks.append(f"[{index}] (doc_id: {doc_id}) {result['content']}")
            prompt = (
                "Instruction: Answer using only the context below. "
                "If the context is insufficient, say clearly that you do not know.\n\n"
                f"Context:\n{chr(10).join(context_blocks)}\n\n"
                f"Question: {item.query}\n\n"
                "Answer:"
            )
            answer = agent.llm_fn(prompt)
        print(f"    agent : {answer[:220]}{'...' if len(answer) > 220 else ''}")
        print()

    total = len(selected)
    print("=" * 72)
    print(f"Tong ket: expected doc_id trong top-{top_k}: {hits_topk}/{total}")
    print(f"          expected doc_id o top-1        : {hits_top1}/{total}")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Chay 5 benchmark query tren corpus UEH (bench.py).")
    parser.add_argument(
        "--data-dir",
        default=os.getenv("LAB_DATA_DIR", DEFAULT_DATA_DIR),
        help="Thu muc corpus (mac dinh: data/ueh_university)",
    )
    parser.add_argument(
        "--chunker",
        choices=("fixed_size", "sentences", "recursive", "heading"),
        default=os.getenv("LAB_CHUNKER", "recursive"),
        help="Chien luoc chunking — moi thanh vien chi doi o day",
    )
    parser.add_argument("--top-k", type=int, default=3, help="So chunk lay ve moi cau hoi")
    parser.add_argument(
        "--query",
        type=int,
        action="append",
        dest="queries",
        metavar="ID",
        help="Chi chay mot hoac nhieu cau (1-5); lap lai flag de chon nhieu cau",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="In danh sach benchmark query + gold answer roi thoat",
    )
    args = parser.parse_args()

    if args.list:
        print("Benchmark queries (copy vao REPORT_NHOM.md):\n")
        for item in BENCHMARK_QUERIES:
            filt = f" filter={item.metadata_filter}" if item.metadata_filter else ""
            print(f"{item.id}. [{item.kind}] {item.query}")
            print(f"   gold   : {item.gold_answer}")
            print(f"   doc_id : {item.expected_doc_id}{filt}\n")
        return 0

    return run_benchmark(
        data_dir=args.data_dir,
        chunker_name=args.chunker,
        top_k=args.top_k,
        query_ids=args.queries,
    )


if __name__ == "__main__":
    raise SystemExit(main())
