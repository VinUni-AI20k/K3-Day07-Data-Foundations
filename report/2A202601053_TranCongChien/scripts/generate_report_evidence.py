import sys
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.embeddings import OpenAIEmbedder, MockEmbedder
from src.chunking import compute_similarity
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent
from src.models import Document
from src.chunking import RecursiveChunker

def evaluate_part_4():
    print("="*50)
    print("PHẦN 4: DỰ ĐOÁN ĐỘ TƯƠNG TỰ (SIMILARITY PREDICTIONS)")
    print("="*50)
    pairs = [
        # --- Cặp tương tự cao (gần như paraphrase, dùng chung từ vựng lõi) ---
        ("Con mèo nhà em rất dễ thương và đáng yêu, nó thường cuộn tròn ngủ trên ghế sofa",
         "Chú mèo trắng này trông thật dễ thương và đáng yêu, nó hay nằm ngủ ngoài ban công",
         "cao"),
        ("Trí tuệ nhân tạo đang phát triển mạnh mẽ và nhanh chóng, ảnh hưởng đến nhiều lĩnh vực",
         "AI đang phát triển rất nhanh và mạnh mẽ, làm thay đổi sâu sắc mọi ngành nghề",
         "cao"),
        ("Anh ấy rất thích uống cà phê đen nóng vào mỗi buổi sáng trước khi đi làm",
         "Cà phê đen là thức uống yêu thích của tôi mỗi buổi sáng khi thức dậy",
         "cao"),
        # --- Cặp tương tự thấp (khác chủ đề, không dùng chung từ nội dung) ---
        ("Tôi thường đi học bằng xe đạp đến trường vào mỗi buổi sáng sớm",
         "Món phở bò nóng hổi này có hương vị thơm ngon và nước dùng rất đậm đà",
         "thấp"),
        ("Bầu trời hôm nay trong xanh và rất đẹp, không một gợn mây",
         "Chiếc máy tính xách tay mới của tôi có cấu hình mạnh và chạy rất mượt mà",
         "thấp")
    ]

    try:
        embedder = OpenAIEmbedder()
        print("Sử dụng OpenAIEmbedder.")
    except Exception as e:
        print(f"Không thể load OpenAIEmbedder: {e}")
        print("Sử dụng MockEmbedder (kết quả sẽ mang tính ngẫu nhiên do hash).")
        embedder = MockEmbedder()

    for idx, (a, b, expected) in enumerate(pairs, 1):
        vec_a = embedder(a)
        vec_b = embedder(b)
        sim = compute_similarity(vec_a, vec_b)
        print(f"Cặp {idx}:")
        print(f"  - Câu A: {a}")
        print(f"  - Câu B: {b}")
        print(f"  - Dự đoán: {expected}")
        print(f"  - Điểm thực tế: {sim:.4f}")
        print("-" * 30)

def evaluate_part_5():
    print("\n" + "="*50)
    print("PHẦN 5: KẾT QUẢ TRUY XUẤT (COMPETITION RESULTS)")
    print("="*50)
    print("Mô phỏng 5 câu hỏi truy xuất với một kho tài liệu mẫu.")
    
    # Tạo store với MockEmbedder (hoặc OpenAIEmbedder nếu có)
    try:
        embedder = OpenAIEmbedder()
    except Exception:
        embedder = MockEmbedder()

    store = EmbeddingStore(embedding_fn=embedder)
    
    # Các câu hỏi giả định
    queries = [
        "RAG là gì?",
        "Cosine similarity khác gì?",
        "Vector Database là gì?",
        "Recursive chunking?",
        "Ứng dụng của embedding?"
    ]

    # Sample documents to populate the store
    sample_docs = [
        Document(id="1", content="RAG kết hợp truy xuất và sinh văn bản để AI trả lời chính xác hơn.", metadata={}),
        Document(id="2", content="Phép đo góc giữa hai vector được gọi là Cosine similarity.", metadata={}),
        Document(id="3", content="Vector Database là cơ sở dữ liệu chuyên lưu trữ và tìm kiếm vector nhúng.", metadata={}),
        Document(id="4", content="Kỹ thuật cắt nhỏ tài liệu đệ quy qua dấu câu được gọi là Recursive chunking.", metadata={}),
        Document(id="5", content="Embedding giúp AI hiểu được ngữ nghĩa từ vựng trong văn bản.", metadata={})
    ]

    store.add_documents(sample_docs)

    # Dummy LLM
    def dummy_llm(prompt: str) -> str:
        return "[Câu trả lời sinh ra từ LLM dựa vào context trên]"

    agent = KnowledgeBaseAgent(store=store, llm_fn=dummy_llm)

    for idx, query in enumerate(queries, 1):
        # Trích xuất top 1 chunk để làm report
        results = store.search(query, top_k=1)
        top1_content = results[0]["content"] if results else "Không tìm thấy"
        top1_score = results[0].get("score", 0.0) if results else 0.0
        
        # Agent trả lời
        agent_answer = agent.answer(query, top_k=3)

        print(f"Câu hỏi {idx}: {query}")
        print(f"  - Top-1 Chunk: {top1_content}")
        print(f"  - Score: {top1_score:.4f}")
        print(f"  - Câu trả lời Agent: {agent_answer}")
        print("-" * 30)

if __name__ == "__main__":
    evaluate_part_4()
    evaluate_part_5()
