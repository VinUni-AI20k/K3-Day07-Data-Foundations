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
        "gold_answer": "Sinh viên bình thường được đăng ký 12-24 tín chỉ. Sinh viên bị cảnh báo học tập mức 1 hoặc 2 chỉ được đăng ký tối đa 14 tín chỉ (tối thiểu 10).",
        "expected_doc": "hust-quy-dinh-dang-ky-hoc-phan",
        "filter": {"audience": "student"}
    },
    {
        "id": 2,
        "query": "Các bước thao tác đăng ký môn học trên cổng CTT HUST (ctt.hust.edu.vn) như thế nào?",
        "gold_answer": "Đăng nhập email HUST -> Chọn Đăng ký học phần & kì học -> Nhập mã lớp học phần -> Kiểm tra kíp học trùng lịch -> Bấm Đăng ký và lưu phiếu.",
        "expected_doc": "hust-huong-dan-thao-tac-ctt",
        "filter": {"audience": "student"}
    },
    {
        "id": 3,
        "query": "Học phần tiên quyết ký hiệu T tại HUST là gì và điều kiện để đăng ký học cải thiện điểm?",
        "gold_answer": "Học phần tiên quyết T yêu cầu phải đạt điểm D trở lên ở môn trước. Đăng ký học cải thiện dành cho các môn đạt điểm D, D+, C, C+.",
        "expected_doc": "hust-dieu-kien-tien-quyet-hoc-lai",
        "filter": {"audience": "student"}
    },
    {
        "id": 4,
        "query": "Thời hạn nộp học phí tín chỉ HUST và chính sách rút học phần trong tuần 1 của học kỳ ra sao?",
        "gold_answer": "Hạn nộp học phí từ tuần 5 đến tuần 7. Rút học phần trong tuần 1 của học kỳ được hoàn 100% học phí.",
        "expected_doc": "hust-quy-dinh-hoc-phi-dang-ky",
        "filter": {"audience": "student"}
    },
    {
        "id": 5,
        "query": "Cố vấn học tập Bách Khoa có trách nhiệm gì trong việc phê duyệt đơn đăng ký vượt tải cho sinh viên?",
        "gold_answer": "Cố vấn học tập (dành cho giảng viên) duyệt đơn đăng ký vượt tải (trên 24 tín chỉ) cho sinh viên CPA >= 3.2 hoặc duyệt học dưới tải.",
        "expected_doc": "hust-quy-trinh-co-van-hoc-tap-duyet",
        "filter": {"audience": "faculty"}
    }
]


def run_benchmark():
    embedder = MockEmbedder()
    chunker = RecursiveChunker(chunk_size=400)
    store = build_knowledge_base("data/k3_university", embedding_fn=embedder, chunker=chunker)
    
    print("=" * 80)
    print("BENCHMARK RETRIEVAL RESULTS (HUST Course Registration Corpus)")
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
