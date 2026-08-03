import sys
sys.stdout.reconfigure(encoding='utf-8')

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.embeddings import MockEmbedder
from src.chunking import RecursiveChunker

BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Sinh viên bình thường và sinh viên bị cảnh báo học tập tại HUST được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ?",
        "gold_answer": "Sinh viên bình thường được đăng ký 12-24 tín chỉ. Sinh viên bị cảnh báo học tập chỉ được đăng ký tối đa 14 tín chỉ (tối thiểu 10).",
        "expected_doc": "hust-credit-training-regulation",
        "filter": {"audience": "student"}
    },
    {
        "id": 2,
        "query": "Các bước thao tác đăng ký lớp môn học trên hệ thống CTT HUST như thế nào?",
        "gold_answer": "Đăng nhập CTT -> Chọn mục Đăng ký lớp -> Nhập mã lớp kíp học -> Kiểm tra trùng thời khóa biểu -> Bấm Đăng ký và lưu phiếu.",
        "expected_doc": "hust-course-registration-system-guide",
        "filter": {"audience": "student"}
    },
    {
        "id": 3,
        "query": "Hạn nộp học phí tín chỉ HUST và quy định xử lý khi chậm nộp học phí ra sao?",
        "gold_answer": "Hạn nộp học phí thông báo theo từng kỳ. Chậm nộp học phí sẽ bị hủy danh sách đăng ký lớp và khóa quyền đăng ký kỳ tiếp theo.",
        "expected_doc": "hust-tuition-by-credits",
        "filter": {"audience": "student"}
    },
    {
        "id": 4,
        "query": "Thời gian đăng ký kế hoạch học tập kỳ 1 năm học 2026-2027 và kỳ hè 2025-2026 thực hiện vào lúc nào?",
        "gold_answer": "Đăng ký kế hoạch học tập kỳ hè 2025-2026 và kỳ 1 2026-2027 thực hiện theo đợt từ tháng 3/2026 theo thông báo CTT 27235.",
        "expected_doc": "hust-study-plan-2026",
        "filter": {"audience": "student"}
    },
    {
        "id": 5,
        "query": "Sinh viên chương trình hợp tác quốc tế (SIE) có quy định gì riêng khi đăng ký học phần thay thế?",
        "gold_answer": "Sinh viên SIE đăng ký học phần thay thế theo hướng dẫn riêng của Viện CNTT&TT (SoICT HUST) áp dụng cho các học phần không mở.",
        "expected_doc": "hust-sie-course-substitution",
        "filter": {"audience": "sie-student"}
    }
]


def run_benchmark():
    embedder = MockEmbedder()
    chunker = RecursiveChunker(chunk_size=400)
    store = build_knowledge_base("data/k3_university", embedding_fn=embedder, chunker=chunker)
    
    print("=" * 80)
    print("BENCHMARK RETRIEVAL RESULTS (HUST Academic Services Corpus)")
    print("=" * 80)

    for item in BENCHMARK_QUERIES:
        q_id = item["id"]
        q_text = item["query"]
        meta_filter = item.get("filter")

        results = store.search_with_filter(q_text, top_k=3, metadata_filter=meta_filter)
        
        print(f"\nQuery {q_id}: {q_text}")
        print(f"Filter applied: {meta_filter}")
        print(f"Gold Answer: {item['gold_answer']}")
        print("Top-3 Retrieved Chunks:")
        for idx, r in enumerate(results, 1):
            doc_id = r['metadata'].get('doc_id')
            score = r['score']
            snippet = r['content'][:100].replace('\n', ' ')
            print(f"  [{idx}] doc_id={doc_id} | score={score:.4f} | snippet={snippet}...")

    print("\n" + "=" * 80)
    print(f"Total chunks in store: {store.get_collection_size()}")


if __name__ == "__main__":
    run_benchmark()
