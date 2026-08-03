import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from main import _select_embedder
from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent

# Force EMBEDDING_PROVIDER to local
os.environ["EMBEDDING_PROVIDER"] = "local"

queries = [
    "Thư viện mở cửa lúc mấy giờ vào cuối tuần?",
    "Để làm thẻ thư viện cần mang theo giấy tờ gì?",
    "Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng mấy?",
    "Hệ thống phân loại sách nào được sử dụng trong thư viện?",
    "Có được phép mượn giáo trình Cơ lý thuyết về nhà không?"
]

def mock_llm_summarize(prompt: str) -> str:
    lower_prompt = prompt.lower()
    if "cuối tuần" in lower_prompt:
        return "Vào cuối tuần (Thứ 7, Chủ nhật), phòng tự học mở cửa từ 8h00 đến 19h00."
    elif "làm thẻ" in lower_prompt:
        return "Để làm thẻ thư viện HUST, bạn đọc cần mang theo thẻ sinh viên hợp lệ hoặc thẻ cán bộ."
    elif "kinh tế - ngoại ngữ" in lower_prompt:
        return "Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng 4 (P.402 hoặc P.411)."
    elif "phân loại" in lower_prompt:
        return "Thư viện sử dụng Khung phân loại DDC (Dewey Decimal Classification) và xếp giá theo Cutter."
    elif "cơ lý thuyết" in lower_prompt:
        return "Không, giáo trình tại các phòng đọc chuyên ngành chỉ được đọc tại chỗ, không được mượn về nhà."
    return "Không tìm thấy thông tin cụ thể trong ngữ cảnh."

embedder = _select_embedder()
store = build_knowledge_base("data/k3_university", embedding_fn=embedder)
agent = KnowledgeBaseAgent(store=store, llm_fn=mock_llm_summarize)

for i, q in enumerate(queries, 1):
    print("=== QUERY {}: {} ===".format(i, q))
    results = store.search(q, top_k=3)
    for idx, r in enumerate(results, 1):
        content_preview = r['content'][:150].strip().replace('\n', ' ')
        print("Match {}: score={:.3f} doc={} file={}".format(idx, r['score'], r['id'], r['metadata'].get('file_path')))
        print("Content: {}".format(content_preview))
    ans = agent.answer(q, top_k=3)
    print("  Answer: {}".format(ans))
