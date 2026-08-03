# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Công Thái Đức — 2A202601581
**Nhóm:** VinBrothers
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

> **Môi trường số liệu trong báo cáo này:** Python 3.11.4; mọi con số về độ tương tự và truy xuất được đo với `EMBEDDING_PROVIDER=local` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`). Mock embedder chỉ dùng để chạy `pytest`.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector nhúng chỉ về gần cùng một **hướng** trong không gian ngữ nghĩa, tức hai đoạn văn bản nói về cùng một chủ đề / cùng một ý — dù dùng từ ngữ khác nhau, thậm chí khác ngôn ngữ. Điểm gần 1 là cùng hướng, gần 0 là không liên quan, gần −1 là ngược hướng.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần trong cổng học vụ theo lịch từng học kỳ."
- Câu B: "Việc ghi danh môn học được thực hiện trên portal của trường theo kế hoạch mỗi kỳ."
- Tại sao tương đồng: gần như không trùng từ vựng ("đăng ký học phần" vs "ghi danh môn học", "cổng học vụ" vs "portal"), nhưng cùng mô tả một hành vi hành chính. Đo được **0.658** — embedding bắt được ý, không chỉ bắt từ khóa.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Ký túc xá bố trí bốn sinh viên mỗi phòng."
- Câu B: "Độ tương tự cosine đo góc giữa hai vector."
- Tại sao khác: khác hẳn miền chủ đề (dịch vụ sinh viên vs toán/kỹ thuật), không chia sẻ khái niệm nào. Đo được **0.058** — gần như vuông góc.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm **hướng**, bỏ qua **độ dài** vector — nên một đoạn dài 500 ký tự và một câu hỏi 10 từ cùng chủ đề vẫn được coi là giống nhau, còn Euclid sẽ phạt nặng vì hai vector lệch nhau về độ lớn (chịu ảnh hưởng của độ dài văn bản và tần suất từ). Thêm nữa, khi vector đã chuẩn hóa về độ dài 1 thì cosine chính là tích vô hướng — rất rẻ để tính, và đó là lý do `EmbeddingStore.search()` trong bài chỉ cần một phép `_dot()`.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* bước nhảy (step) = `chunk_size − overlap` = 500 − 50 = **450**. Mỗi chunk mới đóng góp thêm 450 ký tự nội dung mới, chunk đầu tiên đã "bao" 50 ký tự chồng lấp:
> `số chunk = ceil((10000 − 50) / 450) = ceil(9950 / 450) = ceil(22.11) = 23`
> *Đáp án:* **23 chunks** (chunk cuối chỉ dài 100 ký tự). Đã kiểm chứng bằng code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("x"*10000)` trả về đúng **23** phần tử, khớp công thức.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Step giảm còn 400 nên số chunk **tăng lên 25** (`ceil(9900/400) = 24.75 → 25`, cũng đã kiểm chứng bằng code) — tức tốn thêm chi phí nhúng và lưu trữ. Đổi lại, overlap lớn giúp một câu/ý nằm vắt qua ranh giới chunk vẫn xuất hiện **trọn vẹn** trong ít nhất một chunk, tránh mất câu trả lời vì bị cắt giữa ý. Chính lỗi này đã xảy ra trong thí nghiệm của tôi ở Phần 5 (Q2: chunk bắt đầu bằng "trước khi xác nhận đăng ký…", mất phần đầu câu).

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `re.compile(r"(?<=[.!?])\s+")` để cắt: **lookbehind** `(?<=[.!?])` đảm bảo dấu kết câu được giữ lại ở cuối câu trước, còn `\s+` bao trọn cả `". "` và `".\n"` như đặc tả (một biểu thức xử lý được cả bốn trường hợp `. `, `! `, `? `, `.\n`). Sau khi cắt, tôi `strip()` từng câu và **bỏ các câu rỗng** — cần thiết vì văn bản mẫu kết thúc bằng dấu cách nên phép split sinh ra một phần tử rỗng ở cuối. Edge case: text rỗng hoặc chỉ có khoảng trắng → trả `[]`; `max_sentences_per_chunk` được `max(1, …)` ngay trong `__init__` để không bao giờ chia cho 0. Hạn chế đã biết: viết tắt kiểu "TS." hay "v.v." sẽ bị coi là hết câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split` đệ quy theo danh sách separator giảm dần độ "ngữ nghĩa" (`\n\n` → `\n` → `". "` → `" "` → `""`). **Base case:** đoạn hiện tại đã `<= chunk_size` thì trả về nguyên vẹn; nếu hết separator (hoặc gặp `""`) thì `_hard_split()` cắt cứng theo ký tự để hàm luôn kết thúc. Với separator hiện hành, tôi cắt rồi **gộp tham lam** các mảnh liền nhau (nối lại đúng separator đã cắt) cho tới sát `chunk_size`; mảnh nào một mình đã quá dài thì đệ quy xuống separator kế tiếp. Có thêm một tối ưu nhỏ: nếu separator không xuất hiện trong đoạn thì bỏ qua ngay, thử separator tiếp theo. Nhờ vậy `separators=[]` không lỗi mà rơi thẳng vào nhánh cắt cứng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi tách một hàm `_make_record()` chuẩn hóa mỗi `Document` thành record `{id, content, metadata, embedding}` dùng chung cho cả hai backend. Hai quyết định quan trọng ở đây: (1) **luôn bơm `doc_id` vào metadata** nếu chưa có (`metadata.setdefault("doc_id", doc.id)`) để việc lọc và xóa theo tài liệu vẫn chạy khi caller không truyền metadata; (2) **id lưu trữ có hậu tố số đếm tăng dần** (`f"{doc.id}#{self._next_index}"`) để hai chunk trùng id gốc vẫn là hai record riêng — ChromaDB yêu cầu id duy nhất, nếu không nó sẽ âm thầm ghi đè và làm sai `get_collection_size()`. `search()` nhúng câu hỏi rồi tính `_dot()` với từng vector đã lưu, sắp giảm dần, lấy `top_k`; vì cả ba embedder trong lab đều trả vector đã chuẩn hóa nên tích vô hướng chính là cosine.
> Nếu môi trường có `chromadb`, `__init__` tạo collection với `metadata={"hnsw:space": "cosine"}` và `_query_chroma()` quy đổi `score = 1 − distance`, nhờ đó điểm số của hai backend nằm trên **cùng một thang** và kết quả báo cáo so sánh được với nhau.
>
> **Kiểm chứng nhánh ChromaDB (và 2 lỗi tìm ra nhờ đó):** `pytest` trên máy tôi chỉ chạy nhánh in-memory (không có `chromadb`), nên tôi cài `chromadb` vào một venv riêng và chạy lại toàn bộ 42 test trên nhánh Chroma. Lần đầu **2 test đỏ**, và đều là lỗi thật: (1) `chromadb.EphemeralClient()` **chia sẻ DB trong RAM giữa các lần khởi tạo trong cùng process**, nên `EmbeddingStore` mới vẫn thấy dữ liệu của store cũ cùng tên collection (`get_collection_size()` trả 6 thay vì 0) → khắc phục bằng `delete_collection()` khi dùng client ephemeral; (2) `ingest.parse_front_matter()` dùng pyyaml nên `retrieved_at: 2026-08-02` thành `datetime.date`, khiến Chroma **từ chối cả lô** (`Expected metadata value to be a str, int, float, bool…`) → tôi thêm `_normalize_metadata()` ép mọi giá trị lạ về `str()`. Lỗi (2) còn âm thầm ảnh hưởng cả nhánh in-memory: trước khi sửa, `metadata_filter={"retrieved_at": "2026-08-02"}` **luôn trả 0 kết quả** vì đang so chuỗi với `date` — một cái bẫy trực tiếp cho Giai đoạn 2 vì K3 bắt buộc có trường `retrieved_at`. Sau khi sửa: **42/42 test pass trên cả hai backend**, và bộ lọc `retrieved_at` trả đúng 3/3 chunk.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc trước, xếp hạng sau** (pre-filter): tôi thu hẹp tập record theo `metadata_filter` rồi mới đưa vào `_search_records()`. Nếu làm ngược lại (lấy top-k rồi lọc) thì các chunk điểm cao ngoài phạm vi sẽ chiếm hết chỗ và `top_k=1` có thể trả về rỗng dù dữ liệu hợp lệ vẫn còn. Khi `metadata_filter` rỗng/None thì uỷ quyền thẳng cho `search()` để hai đường cho **cùng số kết quả**. `delete_document()` lọc bỏ mọi record có `metadata["doc_id"]` khớp và so sánh độ dài trước/sau để biết trả `True` hay `False` — xóa theo `doc_id` (không phải id chunk) nên một lệnh gọi dọn sạch toàn bộ chunk của tài liệu, đúng như cách `ingest.py` gắn `doc_id` lên từng chunk.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Đúng 3 bước RAG: `store.search(question, top_k)` → dựng ngữ cảnh → `llm_fn(prompt)`. Ngữ cảnh được ghép từ các chunk dưới dạng khối **có đánh số và kèm `source` + `score`** (`[1] source=… score=…`), và prompt yêu cầu rõ "chỉ dùng thông tin trong NGỮ CẢNH", "nếu không đủ thì nói *Không tìm thấy thông tin trong tài liệu*", "ghi rõ đã dựa vào nguồn nào" — ba câu này nhắm trực tiếp vào tiêu chí *Grounding Quality* của `docs/EVALUATION.md` để hạn chế bịa. Tôi lưu thêm `self.last_results` sau mỗi lần trả lời để truy vết được chunk nào đã sinh ra câu trả lời; khi không truy xuất được gì, ngữ cảnh là chuỗi `(không truy xuất được tài liệu nào liên quan)` thay vì rỗng, để LLM không tự do suy diễn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts ==============================
platform darwin -- Python 3.11.4, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/duc/VIN_AI/K3-Day07-TranHieu-2A202602030
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.03s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

Ngoài bộ test, tôi kiểm tra thêm hai đường chạy thật:
- `python3 ingest.py` → self-check parser front matter OK (4 khóa metadata, 18 chunk giữ đủ `doc_id`).
- `python3 main.py "…"` → chạy trọn pipeline nạp dữ liệu → `search()` → `KnowledgeBaseAgent.answer()` không lỗi.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Dự đoán được ghi **trước** khi chạy; điểm thực tế đo bằng `compute_similarity()` với embedder local (cột mock để đối chứng).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (local) | Đúng? | (đối chứng mock) |
|------|-----------|-----------|---------|--------------|-------|-------|
| 1 | "Sinh viên đăng ký học phần trong cổng học vụ theo lịch từng học kỳ." | "Việc ghi danh môn học được thực hiện trên portal của trường theo kế hoạch mỗi kỳ." | cao | **0.658** | ✅ | 0.045 |
| 2 | "Thư viện cho phép gia hạn sách trực tuyến." | "Thư viện tạm dừng dịch vụ cho mượn sách." | thấp (trái nghĩa) | **0.450** | ❌ | 0.037 |
| 3 | "Hạn cuối đóng học phí là ngày 15 tháng 9." | "The tuition payment deadline is September 15." | cao (song ngữ) | **0.866** | ✅ | −0.034 |
| 4 | "Ký túc xá bố trí bốn sinh viên mỗi phòng." | "Độ tương tự cosine đo góc giữa hai vector." | thấp | **0.058** | ✅ | 0.259 |
| 5 | "Làm sao để xin học bổng khuyến khích học tập?" | "Sinh viên có điểm trung bình từ 3.2 nộp đơn xét học bổng khuyến khích học tập tại phòng công tác sinh viên." | cao (hỏi ↔ đáp) | **0.650** | ✅ | 0.049 |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là **cặp 2: 0.450** — hai câu nói điều **ngược nhau** ("cho phép gia hạn" vs "tạm dừng cho mượn") nhưng vẫn được coi là khá giống, cao hơn cả ngưỡng tôi tưởng là "liên quan". Embedding mã hóa **chủ đề**, không mã hóa **phủ định/trạng thái**: cùng nói về thư viện và việc mượn sách là đủ để hai vector chỉ về gần một hướng. Hệ quả trực tiếp cho RAG: retrieval có thể lôi lên đúng chủ đề nhưng **sai kết luận** (ví dụ trả về quy định đã bị bãi bỏ), nên phải dựa vào metadata như `document_version` / `retrieved_at` để phân biệt, chứ không tin điểm cosine là "đúng".
> Hai quan sát đi kèm: cặp 3 (**0.866**, cao nhất) xác nhận model đa ngữ đặt tiếng Việt và tiếng Anh cùng ý vào cùng vùng không gian — corpus song ngữ vẫn truy xuất chéo được. Còn cột mock cho thấy đúng cảnh báo của README: cặp **khác chủ đề nhất lại có điểm mock cao nhất (0.259)** trong khi cặp song ngữ bị âm — mock chỉ là hash xác định nên hoàn toàn không phản ánh ngữ nghĩa, tuyệt đối không dùng để kết luận chiến lược nào tốt hơn.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> ⚠️ **Kết quả dưới đây là TẠM THỜI.** Nhóm chưa chốt bộ tài liệu 5–10 văn bản và 5 câu hỏi đánh giá chung (Giai đoạn 2). Tôi chạy trước trên **bộ khởi động `data/k3_university/` (2 tài liệu → 3 chunk)** với 5 câu hỏi tự đặt, để kiểm chứng pipeline cá nhân đã đúng. **Cần chạy lại và cập nhật bảng này bằng đúng 5 câu hỏi nhóm chốt trong `REPORT_NHOM.md`.**
>
> Cấu hình: `EMBEDDING_PROVIDER=local`, chunker `FixedSizeChunker(chunk_size=500, overlap=50)` (mặc định của `ingest.build_knowledge_base`), `top_k=3`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên đăng ký học phần ở website nào và cần lưu ý gì trước khi đăng ký? | `huong-dan-dang-ky-hoc-phan` chunk 2 — "…Sinh viên đăng nhập trang đăng ký học phần bằng tài khoản và mật khẩu truy cập Cổng thông tin Sinh viên" | 0.815 | ⚠️ **Một phần** — đúng tài liệu, nhưng địa chỉ `dkhp.iuh.edu.vn` nằm ở chunk 1 và **không lọt cả top-5** | Nêu được các lưu ý (chương trình khung, mã lớp, điều kiện ràng buộc) nhưng **không trả lời được "website nào"** |
| 2 | Sinh viên nộp học phí trực tuyến bằng những cách nào? | `huong-dan-nop-hoc-phi-truc-tuyen` chunk 1 — "…sinh viên cung cấp MÃ SỐ SINH VIÊN… Gạch nợ trực tiếp qua ứng dụng trên điện thoại" | 0.670 | ✅ Có, top-1 đúng và chunk này **có cả cách 2** ("áp dụng cho tất cả ngân hàng") | Nêu đủ 2 cách nộp; riêng link `sv.iuh.edu.vn` lấy từ hạng 3 — mà hạng 3 lại là **tài liệu khác** (`chinh-sach-mien-giam-hoc-phi`) |
| 3 | Mức học bổng khuyến khích học tập tối đa là bao nhiêu? | `che-do-hoc-bong-sinh-vien` chunk 3 — chứa đúng chuỗi "Mức học bổng sinh viên nhận được lên tới **130% học phí**" | 0.797 | ✅ Có, top-1 chứa trọn đáp án | Trả lời đúng: lên tới 130% học phí, cho SV đại học chính quy trong thời gian học chính khóa |
| 4 | Kho sách ngoại văn của thư viện nằm ở tầng nào? | `huong-dan-su-dung-thu-vien` chunk 2 — "TÀI LIỆU GIẤY… kho sách tại các tầng lầu: Tầng trệt… Lầu 2… **Lầu 3: Kho sách ngoại văn**" | 0.706 | ✅ Có, top-1 chứa trọn đáp án | Trả lời đúng: Lầu 3 |
| 5 | Sinh viên bị ốm phải điều trị dài ngày thì việc học được giải quyết thế nào? (`metadata_filter={"audience": "student"}`) | `quy-dinh-nghi-hoc-tam-thoi` chunk 1 — "…chứng nhận của cơ sở khám bệnh, chữa bệnh có thẩm quyền theo quy định của **Bộ Y tế**" | 0.573 | ✅ Có, top-1 đúng — bộ lọc đã loại nhiễu `tu-van-tam-ly` (`audience=all`) | Trả lời đúng: nộp đơn nghỉ học tạm thời + bảo lưu, gửi Phòng Đào tạo, kèm chứng nhận y tế |

> **Cách chấm:** tôi chấm theo đúng chữ trong `docs/SCORING.md` — 2 điểm cần *top-3 có chunk liên quan **và** câu trả lời của agent chính xác*. Nếu chỉ chấm ở mức "đúng tài liệu" thì cả 5 câu đều top-1 và ra 10/10, nhưng như vậy là **tự chấm dễ cho mình**: Q1 tuy top-1 đúng tài liệu nhưng agent không thể trả lời được phần "website nào" vì thông tin đó không có trong ngữ cảnh.
>
> Q1 = 1 điểm, Q2–Q5 = 2 điểm mỗi câu.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5** (cả 5 câu đều có gold doc ở **top-1**). Nhưng theo tiêu chí "agent trả lời chính xác" thì Q1 chỉ đạt một phần → tự đánh giá **9/10**.

**Quan sát về `search_with_filter` (Q5, đối chứng có/không lọc):**

| | Rank 1 | Rank 2 | Rank 3 |
|---|---|---|---|
| Không lọc | 0.573 `quy-dinh-nghi-hoc-tam-thoi` (student) | **0.531 `tu-van-tam-ly-cham-soc-suc-khoe` (all)** ← nhiễu | 0.523 `quy-che-dao-tao-tin-chi` (student) |
| Lọc `audience=student` | 0.573 (student) | 0.523 `quy-che-dao-tao-tin-chi` | 0.518 `quy-che-dao-tao-tin-chi` |

> Bộ lọc làm đúng việc ở câu này: `tu-van-tam-ly-cham-soc-suc-khoe` trùng rất nhiều từ khóa ("ốm", "sức khỏe", "điều trị") nên chen lên hạng 2, nhưng nội dung là trạm y tế và bảo hiểm y tế — **không trả lời được câu hỏi về việc học**. Lọc `audience=student` đẩy nó ra và thay bằng văn bản học vụ thực sự liên quan.
>
> **Nhưng lọc không phải lúc nào cũng tốt.** Tôi thử câu "Sinh viên cần mang theo giấy tờ gì khi vào trường?": đáp án đúng nằm ở `noi-quy-hoc-duong` (`audience=all`, 0.675 — "không đeo thẻ sinh viên…"), và lọc `audience=student` **xóa mất chính đáp án đó**. Kết luận: lọc chỉ tăng precision khi tài liệu `all` là nhiễu; khi tài liệu `all` chính là nguồn trả lời thì lọc phá recall.

**Điểm yếu đã thấy ở chiến lược baseline (đầu vào cho Giai đoạn 2):**
> `FixedSizeChunker(500, 50)` cắt theo **số ký tự, không theo cấu trúc**, nên một quy trình bị xé làm đôi: ở Q1, câu "Sinh viên đăng ký các học phần qua Website của Trường https://dkhp.iuh.edu.vn/" rơi vào **chunk 1**, còn phần "Lưu ý" hướng dẫn thao tác nằm ở **chunk 2**. Câu hỏi khớp ngữ nghĩa với phần thao tác nên chunk 2 lên hạng 1 (0.815), còn chunk chứa URL không lọt nổi top-5 — agent có ngữ cảnh nhưng **thiếu đúng dữ kiện được hỏi**.
>
> Q2 lộ một vấn đề khác về grounding: chuỗi `sv.iuh.edu.vn` xuất hiện ở hạng 3 nhưng thuộc **tài liệu khác** (`chinh-sach-mien-giam-hoc-phi`). Agent vẫn "trả lời đúng", nhưng dẫn nguồn sai tài liệu — đúng loại lỗi mà tiêu chí *Source Traceability* trong `docs/EVALUATION.md` muốn phát hiện.
>
> Hướng cải thiện cho Giai đoạn 2: chunk **theo heading/mục** (gợi ý K3 trong `K3_VARIANT.md`) để mỗi chunk là một quy trình trọn vẹn kèm URL của nó, hoặc tăng `overlap` để URL và phần thao tác cùng nằm trong một chunk.

**So sánh với thành viên khác (cùng 5 câu, cùng corpus, khác chunker):**

| Câu | Tôi — `FixedSizeChunker(500, 50)` | Trần Trung Hiếu — `RecursiveChunker(500)` |
|---|---|---|
| Q1 đăng ký học phần | 0.815, top-1 | 0.791, top-1 |
| Q2 học phí trực tuyến | 0.670, top-1 | 0.706, top-1 |
| Q3 học bổng | 0.797, top-1 — chunk top-1 **chứa** "130%" | 0.773, top-1 — "130%" ở **top-2** |
| Q4 thư viện | 0.706, top-1 | 0.706, top-1 |
| Q5 ốm dài ngày (có lọc) | **0.573, top-1** | 0.528, gold doc ở **top-3** |

> Khác biệt rõ nhất ở Q5: `RecursiveChunker` cắt theo `\n\n` trước, nên `quy-che-dao-tao-tin-chi` (39.962 ký tự — chiếm phần lớn corpus) sinh nhiều chunk "chung chung" dễ chen lên hạng cao, đẩy tài liệu ngắn `quy-dinh-nghi-hoc-tam-thoi` xuống. Fixed-size cắt đều nên tài liệu ngắn không bị lép vế. Ngược lại ở Q2 thì Recursive nhỉnh hơn vì giữ được ranh giới đoạn của phần liệt kê ngân hàng.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *[Điền sau buổi demo — cần nghe chiến lược của các thành viên khác trước khi viết.]*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 (42/42 test pass) |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 *(5/5 gold doc ở top-1; trừ 1 điểm ở Q1 vì agent thiếu dữ kiện được hỏi)* |
| **Tổng phần cá nhân** | **59 / 60** |
