"""Benchmark tái lập kết quả retrieval trong REPORT_CANHAN.md.

Chạy từ thư mục gốc của bài lab:

    .venv\Scripts\python.exe bench.py

Script dùng MockEmbedder để chạy hoàn toàn offline và cho điểm số xác định.
Điểm mock chỉ chứng minh pipeline hoạt động; để đánh giá ngữ nghĩa thực tế,
hãy thay EMBEDDER bên dưới bằng LocalEmbedder sau khi đã cài mô hình.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, compute_similarity
from src.embeddings import MockEmbedder


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "k3_university"
CHUNKER = FixedSizeChunker(chunk_size=500, overlap=50)
TOP_K = 3


@dataclass(frozen=True)
class BenchmarkCase:
    """Một câu hỏi, tài liệu kỳ vọng và từ khóa cần xuất hiện trong chunk."""

    query: str
    expected_doc_id: str
    evidence_terms: tuple[str, ...]


# Các câu hỏi này chỉ yêu cầu thông tin thật sự có trong data/k3_university.
CASES = (
    BenchmarkCase(
        "Ai có thể sử dụng dịch vụ thư viện?",
        "k3-library-services",
        ("sinh viên", "giảng viên", "nhân viên"),
    ),
    BenchmarkCase(
        "Người dùng cần mang gì khi mượn tài liệu ở thư viện?",
        "k3-library-services",
        ("thẻ định danh hợp lệ",),
    ),
    BenchmarkCase(
        "Sinh viên đăng ký học phần ở đâu?",
        "k3-course-registration",
        ("cổng học vụ",),
    ),
    BenchmarkCase(
        "Trước khi xác nhận đăng ký học phần, sinh viên cần kiểm tra gì?",
        "k3-course-registration",
        ("học phần tiên quyết", "điều kiện"),
    ),
    BenchmarkCase(
        "Khi gặp lỗi trùng lịch, sinh viên cần làm gì?",
        "k3-course-registration",
        ("điều chỉnh lớp học phần", "thời hạn điều chỉnh"),
    ),
)

SIMILARITY_CASES = (
    ("Python là ngôn ngữ lập trình bậc cao.", "Python là một ngôn ngữ lập trình cấp cao."),
    ("Sinh viên có thể gia hạn sách ở thư viện.", "Thư viện hỗ trợ mượn và gia hạn tài liệu."),
    ("Hạn cuối đăng ký học phần là khi nào?", "Khi nào sinh viên phải đóng học phí?"),
    ("Học bổng xét dựa trên thành tích học tập.", "Điểm số tốt có thể là tiêu chí nhận học bổng."),
    ("Ký túc xá có chỗ đỗ xe không?", "Quy trình đăng ký môn học gồm những bước nào?"),
)


def _one_line(text: str, limit: int = 150) -> str:
    """Tạo tóm tắt một dòng phù hợp để dán vào bảng Markdown."""
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else f"{clean[:limit - 3]}..."


def _is_relevant(result: dict, case: BenchmarkCase) -> bool:
    """Đánh giá minh bạch: đúng tài liệu nguồn và chứa ít nhất một bằng chứng."""
    metadata = result.get("metadata") or {}
    content = result.get("content", "").casefold()
    return (
        metadata.get("doc_id") == case.expected_doc_id
        and any(term.casefold() in content for term in case.evidence_terms)
    )


def _extractive_demo_llm(prompt: str) -> str:
    """LLM giả lập quyết định, trả lại phần ngữ cảnh để kiểm tra RAG offline."""
    context = prompt.partition("Context:\n")[2].partition("\n\nQuestion:")[0]
    return _one_line(context, limit=220)


def run_benchmark() -> int:
    """In bảng bằng chứng và trả về 0 khi mọi câu có bằng chứng trong top-3."""
    embedder = MockEmbedder()
    store = build_knowledge_base(
        DATA_DIR, embedding_fn=embedder, chunker=CHUNKER, collection_name="bench"
    )
    agent = KnowledgeBaseAgent(store=store, llm_fn=_extractive_demo_llm)

    print("# Kết quả benchmark retrieval")
    print(f"- Dữ liệu: `{DATA_DIR.relative_to(ROOT)}`")
    print(f"- Embedder: `{embedder._backend_name}`")
    print(f"- Chunker: `FixedSizeChunker(chunk_size=500, overlap=50)`")
    print(f"- Số chunk: {store.get_collection_size()}\n")

    print("## Độ tương tự của 5 cặp câu trong báo cáo")
    print("| # | Điểm cosine |")
    print("|---|---:|")
    for number, (sentence_a, sentence_b) in enumerate(SIMILARITY_CASES, start=1):
        score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
        print(f"| {number} | {score:.4f} |")

    print("\n## Kết quả retrieval")
    print("| # | Câu hỏi | Top-1 chunk (tóm tắt) | Score | Liên quan top-1? | Có bằng chứng trong top-3? |")
    print("|---|---|---|---:|---|---|")

    passed = 0
    for number, case in enumerate(CASES, start=1):
        results = store.search(case.query, top_k=TOP_K)
        if not results:
            print(f"| {number} | {case.query} | Không có kết quả | — | Không | Không |")
            continue

        top_1 = results[0]
        top_1_relevant = _is_relevant(top_1, case)
        top_3_relevant = any(_is_relevant(result, case) for result in results)
        passed += top_3_relevant
        print(
            f"| {number} | {case.query} | {_one_line(top_1['content'])} | "
            f"{top_1['score']:.4f} | {'Có' if top_1_relevant else 'Không'} | "
            f"{'Có' if top_3_relevant else 'Không'} |"
        )
        print(f"  - Agent (extractive demo): {agent.answer(case.query, top_k=TOP_K)}")

        print("  - Top-3 nguồn:")
        for rank, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            print(
                f"    {rank}. doc_id={metadata.get('doc_id', '—')}, "
                f"score={result['score']:.4f}, "
                f"relevant={'Có' if _is_relevant(result, case) else 'Không'}"
            )

    print(f"\nKết luận: {passed}/{len(CASES)} câu có chunk chứa bằng chứng trong top-{TOP_K}.")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    # PowerShell/Windows có thể mặc định CP1252 và không in được tiếng Việt.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(run_benchmark())
