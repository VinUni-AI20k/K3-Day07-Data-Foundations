"""
bench.py — chạy 5 benchmark query (benchmarks/vinuni_course_registration.json)
qua MỘT chiến lược chunking cụ thể, trên corpus data/vinuni_course_registration.

Không viết lại phần nạp dữ liệu: ingest.build_knowledge_base() đã parse front
matter, chunk bằng chunker được truyền vào, gắn doc_id + metadata lên từng
chunk, rồi nạp vào EmbeddingStore. Việc của file này chỉ còn ba bước —
xem run_benchmark() bên dưới.

Mỗi thành viên chạy file này với CHỈ MỘT dòng khác nhau: dòng chọn `chunker`
trong __main__. Corpus, 5 query, và embedder (EMBEDDING_PROVIDER) giữ nguyên
để so sánh công bằng.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import (
    FixedSizeChunker,
    HeadingChunker,
    RecursiveChunker,
    SentenceChunker,
)
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)

DATA_DIR = os.getenv("LAB_DATA_DIR", "data/vinuni_course_registration")
BENCHMARK_FILE = Path("benchmarks/vinuni_course_registration.json")


def _select_embedder():
    """Chọn backend nhúng theo biến môi trường EMBEDDING_PROVIDER (mock | local | openai)."""
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("Local embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    if provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            print("OpenAI embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    return _mock_embed


def demo_llm(prompt: str) -> str:
    """LLM giả lập đơn giản — đủ để thử pipeline RAG mà không cần API key."""
    preview = prompt[:400].replace("\n", " ")
    return f"[DEMO LLM] {preview}..."


def _describe_chunker(chunker) -> str:
    params = {k: v for k, v in vars(chunker).items() if not k.startswith("_")}
    return f"{chunker.__class__.__name__}({params})"


def run_benchmark(chunker, data_dir: str = DATA_DIR) -> None:
    queries = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    embedding_fn = _select_embedder()
    backend = getattr(embedding_fn, "_backend_name", embedding_fn.__class__.__name__)

    # 2. Nạp cả thư mục corpus. embedding_fn là tham số bắt buộc thứ hai.
    store = build_knowledge_base(data_dir, embedding_fn, chunker=chunker)
    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    print(f"Strategy : {_describe_chunker(chunker)}")
    print(f"Backend nhúng: {backend}")
    print(f"Số chunk đã nạp: {store.get_collection_size()}")

    # 3. Chạy 5 query qua search() hoặc search_with_filter().
    for item in queries:
        metadata_filter = item.get("metadata_filter")
        print(f"\n=== [{item['id']}] {item['query']} ===")
        if metadata_filter:
            print(f"    (metadata_filter={metadata_filter})")
            results = store.search_with_filter(item["query"], top_k=3, metadata_filter=metadata_filter)
        else:
            results = store.search(item["query"], top_k=3)

        for rank, result in enumerate(results, start=1):
            preview = result["content"][:120].replace("\n", " ")
            doc_id = result["metadata"].get("doc_id")
            print(f"    top-{rank} score={result['score']:.3f} doc_id={doc_id} preview={preview}...")

        print("    Gold  :", item["gold_answer"])
        print("    Answer:", agent.answer(item["query"], top_k=3))


if __name__ == "__main__":
    if not Path(DATA_DIR).exists():
        raise SystemExit(f"Không tìm thấy thư mục dữ liệu: {DATA_DIR}")
    if not BENCHMARK_FILE.exists():
        raise SystemExit(f"Không tìm thấy file benchmark query: {BENCHMARK_FILE}")

    # 1. Chọn chunker của riêng bạn — đây là DÒNG DUY NHẤT khác với bạn cùng nhóm.
    chunker = RecursiveChunker(chunk_size=400)
    # Các lựa chọn khác cùng nhóm có thể dùng thay dòng trên (không đổi gì khác):
    #   chunker = FixedSizeChunker(chunk_size=400, overlap=50)
    #   chunker = SentenceChunker(max_sentences_per_chunk=4)
    #   chunker = HeadingChunker(chunk_size=400)

    run_benchmark(chunker)
