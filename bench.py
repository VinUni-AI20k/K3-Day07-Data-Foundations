import sys
sys.stdout.reconfigure(encoding='utf-8')

from ingest import build_knowledge_base
from src.chunking import RecursiveChunker
from src.embeddings import LocalEmbedder, MockEmbedder
from src.agent import KnowledgeBaseAgent

def dummy_llm(prompt: str) -> str:
    """Hàm LLM giả để phục vụ test retrieval (không gọi API tốn phí)."""
    return "[DUMMY LLM] Tôi đã đọc context ở trên và có thể trả lời câu hỏi..."

def main():
    print("=== BENCHMARK THỬ NGHIỆM ===")
    
    # 1. Chọn chunker (Dòng duy nhất khác biệt)
    chunk_size = 400
    chunker = RecursiveChunker(chunk_size=chunk_size)
    print(f"Strategy: RecursiveChunker")
    print(f"Tham số: chunk_size={chunk_size}")

    # Khởi tạo Embedder (ưu tiên LocalEmbedder nếu đã cài xong sentence-transformers)
    try:
        embedding_fn = LocalEmbedder()
        print("Embedder: LocalEmbedder (paraphrase-multilingual-MiniLM-L12-v2)")
    except Exception:
        embedding_fn = MockEmbedder()
        print("Embedder: MockEmbedder (Fallback)")
    # embedding_fn = MockEmbedder()
    # 2. Nạp dữ liệu
    print("\nĐang nạp dữ liệu từ data/k3_university...")
    store = build_knowledge_base("data/k3_university", embedding_fn, chunker=chunker)
    print(f"-> Đã nạp thành công {store.get_collection_size()} chunks vào EmbeddingStore.")

    agent = KnowledgeBaseAgent(store, dummy_llm)

    # 5 câu hỏi benchmark đã chốt (từ benchmark.csv)
    queries = [
        "Tất cả sinh viên đại học nhập học từ năm 2025 đến năm 2030 sẽ nhận được mức hỗ trợ học phí là bao nhiêu?",
        "Ứng viên nữ theo đuổi lĩnh vực khoa học công nghệ có thể nhận loại học bổng nào và trị giá bao nhiêu?",
        "Kỳ tuyển sinh sớm (Early Round) hệ đại học năm 2026 của VinUni diễn ra vào khoảng thời gian nào?",
        "Sinh viên ứng tuyển vào kỳ Tuyển sinh sớm (Early Round) và tham gia VinUni Open Day sẽ nhận được đặc quyền tài chính gì?",
        "Chương trình Tiến sĩ tại VinUni tập trung nghiên cứu chuyên sâu vào những lĩnh vực trọng yếu nào?"
    ]

    print("\n--- KẾT QUẢ TRUY XUẤT 5 QUERIES ---")
    for i, q in enumerate(queries, 1):
        print(f"\n[Query {i}]: {q}")
        
        # Truy xuất Top-3 Chunks
        results = store.search(q, top_k=3)
        for rank, r in enumerate(results, 1):
            score = r.get('score', 0)
            doc_id = r['metadata'].get('doc_id', 'unknown')
            preview = r['content'].replace('\n', ' ')[:80] + "..."
            print(f"  #{rank} | Score: {score:.4f} | DocID: {doc_id} | Preview: {preview}")
            
        # Phản hồi của Agent (sẽ in ra DUMMY LLM theo prompt)
        answer = agent.answer(q, top_k=3)
        print(f"  [Agent] -> {answer}")

if __name__ == "__main__":
    main()
