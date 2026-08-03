"""
bench.py — chạy 5 câu hỏi benchmark của nhóm (report/REPORT_NHOM.md, Phần 3)
trên MỘT chiến lược chunking cá nhân, để so sánh giữa các thành viên (CP5/CP6).

Không viết lại pipeline nạp dữ liệu: build_knowledge_base() trong ingest.py đã
làm trọn 4 việc (parse front matter -> chunk -> gắn doc_id + metadata lên từng
chunk -> nạp vào EmbeddingStore). Việc của file này chỉ còn 3 bước:
    1. Chọn chunker cá nhân (dòng DUY NHẤT nên khác giữa các thành viên).
    2. Nạp cả thư mục corpus qua build_knowledge_base().
    3. Chạy 5 query qua search()/search_with_filter(), in strategy, số chunk,
       top-3 (score, doc_id, preview) và câu trả lời của agent.

Chạy: EMBEDDING_PROVIDER=local python3 bench.py
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.embeddings import EMBEDDING_PROVIDER_ENV, LOCAL_EMBEDDING_MODEL, LocalEmbedder, _mock_embed
from src.heading_chunker import HeadingChunker

DATA_DIR = "data/k3_university"

# 5 câu hỏi đã chốt với nhóm (report/REPORT_NHOM.md, Phần 3) — không đổi sau khi
# đã có strategy chạy qua. Câu 5 bắt buộc filter theo audience=student (K3_VARIANT.md).
BENCHMARK_QUERIES: list[tuple[str, dict | None]] = [
    ("Sinh viên đăng ký học phần ở website nào và cần lưu ý gì trước khi đăng ký?", None),
    ("Sinh viên nộp học phí trực tuyến bằng những cách nào?", None),
    ("Mức học bổng khuyến khích học tập tối đa là bao nhiêu?", None),
    ("Kho sách ngoại văn của thư viện nằm ở tầng nào?", None),
    (
        "Sinh viên bị ốm phải điều trị dài ngày thì việc học được giải quyết thế nào?",
        {"audience": "student"},
    ),
]


def demo_llm(prompt: str) -> str:
    """LLM giả lập (không cần API key) — giống main.py, chỉ để xem prompt/context đã lắp đúng chưa."""
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] {preview}..."


def select_embedder():
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception as error:
            print(f"Local embedder không sẵn sàng ({error}); tạm dùng mock.")
            return _mock_embed
    return _mock_embed


def run(chunker, embedder) -> None:
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    strategy_desc = f"{chunker.__class__.__name__}({vars(chunker)})"

    print(f"Strategy: {strategy_desc}")
    print(f"Embedder: {backend}")

    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
    print(f"Đã nạp {store.get_collection_size()} chunk từ {DATA_DIR}")

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    for index, (query, metadata_filter) in enumerate(BENCHMARK_QUERIES, start=1):
        print("\n" + "=" * 80)
        print(f"Q{index}: {query}")
        if metadata_filter:
            print(f"   metadata_filter={metadata_filter}")
            results = store.search_with_filter(query, top_k=3, metadata_filter=metadata_filter)
        else:
            results = store.search(query, top_k=3)

        for rank, result in enumerate(results, start=1):
            preview = result["content"][:150].replace("\n", " ")
            print(f"  #{rank} score={result['score']:.3f} doc_id={result['metadata'].get('doc_id')}")
            print(f"      {preview}...")

        answer = agent.answer(query, top_k=3)
        print(f"Agent answer: {answer[:200]}...")


if __name__ == "__main__":
    # 1. Chọn chunker cá nhân — dòng khác biệt so với bạn cùng nhóm
    #    (bạn cùng nhóm dùng FixedSizeChunker(500, 50) làm baseline).
    my_chunker = HeadingChunker(chunk_size=800)

    # 2. embedding_fn là tham số bắt buộc thứ hai của build_knowledge_base().
    my_embedder = select_embedder()

    # 3. Nạp + chạy 5 query, in kết quả.
    run(my_chunker, my_embedder)
