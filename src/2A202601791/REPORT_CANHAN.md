# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Nguyễn Thế Anh]
**Nhóm:** [NguyenTheAnh]
**Ngày:** [03/08/2026]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

Hai đoạn văn bản có độ tương tự cosine cao có nghĩa là chúng **nói về cùng một chủ đề, cùng ý tưởng, và dùng từ ngữ tương đồng**. Trong không gian embedding, hai vector có hướng gần nhau (góc nhỏ giữa chúng), dù độ dài (magnitude) có thể khác nhau. Điều này giúp hệ thống nhận diện được hai câu "nói cùng một thứ" dù cách diễn đạt hơi khác.

**Ví dụ có độ tương tự CAO:**
- **Câu A:** "Hôm nay trời đẹp và nắng ấm"
- **Câu B:** "Trời hôm nay rất đẹp, có nắng ấm"
- **Tại sao tương đồng:** Hai câu đều mô tả thời tiết đẹp, có nắng ấm. Từ vựng gần giống, cấu trúc câu tương tự, nên embedding vectors sẽ có hướng rất gần nhau → cosine similarity cao.

**Ví dụ có độ tương tự THẤP:**
- **Câu A:** "Hôm nay trời đẹp và nắng ấm"
- **Câu B:** "Tôi thích ăn pizza phô mai"
- **Tại sao khác:** Hai câu thuộc chủ đề hoàn toàn khác nhau (thời tiết vs. ẩm thực), không có từ vựng chung, không có ý nghĩa liên quan. Vector embeddings sẽ hướng về hai phía khác nhau trong không gian → cosine similarity thấp.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

Cosine similarity **đo lường góc giữa hai vector** (hướng), không phụ thuộc vào độ dài (magnitude) của chúng. Trong khi đó, Euclidean distance bị ảnh hưởng bởi cả hướng và độ dài — hai câu có cùng ý nghĩa nhưng một câu dài hơn có thể bị đánh giá là "xa" hơn chỉ vì magnitude lớn hơn. Vì text embeddings thường có độ dài khác nhau tùy câu, cosine similarity là thước đo phù hợp hơn để đánh giá sự tương đồng ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

Công thức: `số_lượng_chunk = ceil((độ_dài_tài_liệu - overlap) / (chunk_size - overlap))`

Phép tính:
- `(10,000 - 50) / (500 - 50) = 9,950 / 450 ≈ 22.11`
- `ceil(22.11) = 23`

**Đáp án: 23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

Phép tính với overlap=100:
- `(10,000 - 100) / (500 - 100) = 9,900 / 400 = 24.75`
- `ceil(24.75) = 25`

→ Số lượng chunk **tăng từ 23 lên 25**.

Tại sao muốn tăng overlap: Khi overlap lớn hơn, các chunk liền kề **chồng chéo nhiều hơn**, giúp đảm bảo thông tin ở ranh giới giữa hai chunk không bị mất. Điều này quan trọng vì một câu hoặc một ý quan trọng có thể bị cắt đúng ở giữa hai chunk — overlap lớn giúp ngữ cảnh được giữ lại ở cả hai bên, tăng khả năng truy xuất đúng thông tin.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Tôi dùng regex `r'(?<=[.!?])\s+'` để phát hiện ranh giới câu (dấu chấm, chấm than, chấm hỏi theo sau bởi khoảng trắng). Sau khi tách thành list các câu, tôi nhóm lại thành chunks mỗi chunk chứa tối đa `max_sentences_per_chunk` câu. Với edge case: nếu text rỗng trả về `[]`; nếu không tìm thấy ranh giới câu (ví dụ text chỉ có 1 câu không có dấu câu), trả về nguyên văn text đó.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán thử các dấu phân cách theo thứ tự ưu tiên (`"\n\n"` → `"\n"` → `". "` → `" "` → `""`). Với mỗi separator, nếu text vẫn dài hơn `chunk_size`, tách text bằng separator đó rồi đệ quy xử lý từng phần. Base case là khi text đã đủ ngắn (≤ `chunk_size`) hoặc đã thử hết các separator (lúc này trả về nguyên văn text).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Tôi lưu trữ trong bộ nhớ (in-memory) dưới dạng list các dict, mỗi dict chứa `id`, `content`, `embedding`, và `metadata`. Khi `add_documents`, tôi gọi `embedding_fn` để nhúng từng document rồi append vào list. Khi `search`, tôi nhúng query, tính dot product giữa query embedding và từng stored embedding (vì với embeddings đã được normalize, dot product tương đương cosine similarity), sau đó sắp xếp giảm dần và trả về top_k kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Với `search_with_filter`, tôi **lọc trước** bằng metadata_filter: duyệt qua tất cả records, chỉ giữ lại những record thỏa mãn tất cả điều kiện trong `metadata_filter`, sau đó chạy similarity search trên tập con đã lọc. Với `delete_document`, tôi dùng list comprehension để giữ lại các record có `r.get("id") != doc_id`, trả về `True` nếu có record bị xóa, `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Tôi cấu trúc prompt theo mẫu RAG: đưa ngữ cảnh (context) vào đầu prompt, bao gồm các chunks được truy xuất kèm metadata, sau đó là câu hỏi của người dùng. Cụ thể: tôi retrieve top-k chunks từ store, nối chúng thành một đoạn context, rồi gọi `llm_fn` với prompt dạng `"Dựa trên ngữ cảnh sau đây, hãy trả lời câu hỏi. Ngữ cảnh:\n{context}\n\nCâu hỏi: {question}\n\nTrả lời:"`. Điều này giúp LLM có thông tin nền (grounding) để trả lời chính xác hơn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: d:\AI IN ACTION\GIAI ĐOAN 1\Day 7-8\K3_07_DataFoundations_E403_NguyenTheAnh
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
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED [ 45%]
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

============================= 42 passed in 0.27s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

### Dự đoán trước khi chạy

| Cặp | Câu A | Câu B | Dự đoán | Lý do dự đoán |
|------|-----------|-----------|---------|---------------|
| 1 | "Hom nay troi dep" | "Troi hom nay rat dep" | **CAO** | Cùng chủ đề thời tiết, từ vựng gần giống, chỉ khác một từ "rat" |
| 2 | "Python la ngon ngu lap trinh" | "Toi thich an pizza" | **THẤP** | Hoàn toàn khác chủ đề (lập trình vs. ẩm thực) |
| 3 | "Machine learning hoc du lieu" | "Deep learning su dung mang neural" | **CAO** | Cùng lĩnh vực AI, nhiều thuật ngữ liên quan |
| 4 | "Dang ky mon hoc tu ngay 15" | "Hoc phi dong truoc ngay 30" | **THẤP** | Cùng chủ đề đại học nhưng khác hoạt động (đăng ký vs. học phí) |
| 5 | "Thu vien mo cua luc 8h sang" | "Thu vien co 500 cho ngoi" | **CAO** | Cùng chủ đề thư viện, nhiều từ chung "thu vien" |

### Kết quả thực tế (dùng mock embedder)

| Cặp | Câu A | Câu B | Điểm thực tế | Dự đoán đúng? |
|------|-----------|-----------|---------|--------------|
| 1 | "Hom nay troi dep" | "Troi hom nay rat dep" | 0.0177 | THẤP (dự đoán CAO → **SAI**) |
| 2 | "Python la ngon ngu lap trinh" | "Toi thich an pizza" | -0.0562 | THẤP (dự đoán THẤP → **ĐÚNG**) |
| 3 | "Machine learning hoc du lieu" | "Deep learning su dung mang neural" | -0.1198 | THẤP (dự đoán CAO → **SAI**) |
| 4 | "Dang ky mon hoc tu ngay 15" | "Hoc phi dong truoc ngay 30" | 0.1002 | THẤP (dự đoán THẤP → **ĐÚNG**) |
| 5 | "Thu vien mo cua luc 8h sang" | "Thu vien co 500 cho ngoi" | 0.0490 | THẤP (dự đoán CAO → **SAI**) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Kết quả bất ngờ nhất là **Cặp 1** ("Hom nay troi dep" vs "Troi hom nay rat dep"): tôi dự đoán CAO nhưng thực tế chỉ đạt 0.0177 (rất thấp). Tương tự, Cặp 3 và Cặp 5 cũng cho điểm thấp bất chấp rõ ràng là cùng chủ đề.

Điều này cho thấy **mock embedder (`_mock_embed`) không phản ánh chất lượng ngữ nghĩa** — nó sinh vector gần như ngẫu nhiên dựa trên hash MD5 của chuỗi đầu vào, nên hai câu có nghĩa gần nhau vẫn có thể có vector gần như không liên quan. Đây là lý do README nhấn mạnh: mock embedder chỉ dùng cho unit test, **không dùng để đánh giá chiến lược chunking hay kết luận embedding tiếng Việt nào tốt hơn**. Để có kết quả có ý nghĩa, cần dùng embedder thật (local hoặc OpenAI).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

> **Lưu ý:** Phần này cần 5 câu hỏi đánh giá của nhóm (xem `REPORT_NHOM.md` — Phần 3). Nội dung dưới đây là placeholder; cần cập nhật sau khi nhóm thống nhất câu hỏi và chạy đánh giá.

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | *(chờ câu hỏi từ nhóm)* | | | | |
| 2 | *(chờ câu hỏi từ nhóm)* | | | | |
| 3 | *(chờ câu hỏi từ nhóm)* | | | | |
| 4 | *(chờ câu hỏi từ nhóm)* | | | | |
| 5 | *(chờ câu hỏi từ nhóm)* | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *(Cập nhật sau khi thuyết trình nhóm)*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
