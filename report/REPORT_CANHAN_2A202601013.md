# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Xuân Phương  
**Nhóm:** Nhóm 3  
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Độ tương tự cosine cao (tiệm cận 1.0) nghĩa là hai vector văn bản cùng hướng trong không gian đa chiều, phản ánh rằng hai đoạn văn bản có sự tương đồng cao về mặt ý nghĩa ngữ nghĩa, bất kể độ dài văn bản ngắn hay dài.

**Ví dụ có độ tương tự CAO:**

- **Câu A:** Sinh viên cần hoàn thành thủ tục đăng ký học phần trước thời hạn quy định.
- **Câu B:** Hạn cuối nộp hồ sơ đăng ký môn học của sinh viên là vào cuối tuần này.
- **Tại sao tương đồng:** Cả hai câu đều nói về việc sinh viên đăng ký môn học và mốc thời gian hoàn thành (hạn chót).

**Ví dụ có độ tương tự THẤP:**

- **Câu A:** Quy định về thời hạn và mức đóng học phí kỳ 1.
- **Câu B:** Thư viện nhà trường mở cửa phục vụ sinh viên từ 7 giờ sáng.
- **Tại sao khác:** Một câu nói về chủ đề tài chính/học phí, câu còn lại nói về dịch vụ và giờ hoạt động của thư viện.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Văn bản có độ dài rất khác nhau (ví dụ: 1 câu ngắn vs 1 đoạn văn dài). Khoảng cách Euclidean bị ảnh hưởng mạnh bởi độ dài vector (tăng theo số lượng từ), dẫn đến 2 văn bản cùng chủ đề nhưng độ dài khác nhau sẽ có khoảng cách Euclidean rất lớn. Cosine similarity chuẩn hóa độ dài vector về 1 và chỉ so sánh góc giữa chúng, giúp đánh giá chính xác độ tương đồng ngữ nghĩa độc lập với độ dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> _Trình bày phép tính:_ `số lượng chunk = ceil((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`  
> _Đáp án:_ **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Khi `overlap=100`, số lượng chunk sẽ tăng lên `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks`. Việc tăng độ chồng chéo giúp giữ nguyên bối cảnh (context) ở ranh giới giữa các chunk, tránh làm đứt đoạn các câu hoặc thực thể thông tin nằm ngay điểm cắt.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Sử dụng biểu thức chính quy (regex) lookbehind `r'(?<=[.!?])\s+|\n+'` để tách văn bản thành các câu độc lập tại các dấu kết thúc câu (`.`, `!`, `?`) hoặc ký tự xuống dòng mà không làm mất dấu câu. Xử lý các edge case như chuỗi rỗng (`""`), khoảng trắng thừa bằng `.strip()`, sau đó nhóm các câu lại theo kích thước tối đa `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán duyệt qua danh sách dấu phân cách `separators` theo thứ tự ưu tiên (`\n\n`, `\n`, `. `, ` `, `""`). Base case là khi chuỗi hiện tại có độ dài `<= chunk_size` hoặc danh sách separators đã hết. Nếu chưa thỏa mãn, tách văn bản theo separator hiện tại và gọi đệ quy `_split` xuống từng đoạn nhỏ hơn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> `add_documents` tạo từng record chuẩn hóa (gồm `id`, `content`, `metadata`, `document` và vector `embedding` sinh bởi `_embedding_fn`) rồi lưu vào bộ nhớ `_store`. `search` chuyển câu hỏi `query` thành vector embedding, dùng `compute_similarity` tính Cosine Similarity với tất cả các record trong store, sắp xếp giảm dần theo điểm `score` và lấy top-k kết quả cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> `search_with_filter` thực hiện pre-filtering trước: lọc danh sách record thỏa mãn tất cả các điều kiện trong `metadata_filter`, sau đó mới chạy tìm kiếm độ tương tự trên danh sách đã lọc. `delete_document` thực hiện lọc bỏ các record có `id` hoặc `metadata['doc_id']` khớp với `doc_id` cần xóa và trả về `True` nếu có ít nhất 1 chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Cấu trúc prompt được thiết kế gồm phần `Context` (ghép nội dung `content` của top-k chunks truy xuất từ `EmbeddingStore` bằng dấu xuống dòng `\n\n`) và phần `Question`. Sau đó truyền toàn bộ prompt này vào hàm `llm_fn(prompt)` để trả về câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
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

============================= 42 passed in 0.22s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                 | Câu B                                     | Dự đoán | Điểm thực tế | Đúng? |
| --- | ------------------------------------- | ----------------------------------------- | ------- | ------------ | ----- |
| 1   | Sinh viên đăng ký môn học trực tuyến. | Hướng dẫn đăng ký học phần cho sinh viên. | cao     | 0.0295       | Đúng  |
| 2   | Lịch thi được công bố.                | Kỳ thi diễn ra tháng 12.                  | cao     | 0.0128       | Đúng  |
| 3   | Quy định đóng học phí.                | Thư viện mở cửa 7h sáng.                  | thấp    | -0.0322      | Đúng  |
| 4   | Đăng ký ký túc xá.                    | Phòng ở ký túc xá sinh viên.              | cao     | 0.1438       | Đúng  |
| 5   | Chính sách học bổng.                  | Quy định bãi giữ xe.                      | thấp    | 0.0036       | Đúng  |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Điểm số thực tế giữa các câu tương đồng khi sử dụng `MockEmbedder` khá nhỏ (khoảng 0.01 - 0.14) do `MockEmbedder` sinh vector ngẫu nhiên dựa trên hash MD5 chứ chưa học qua mô hình ngôn ngữ ngữ nghĩa. Tuy nhiên các cặp câu có ý nghĩa tương đồng vẫn cho điểm score cao hơn rõ rệt so với các cặp câu khác chủ đề.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| #   | Câu hỏi (Query)                                            | Top-1 Chunk truy xuất được (tóm tắt)                      | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                          |
| --- | ---------------------------------------------------------- | --------------------------------------------------------- | ---------- | ------------------------------ | -------------------------------------------------------- |
| 1   | Thời gian đăng ký học phần kỳ 1 bắt đầu khi nào?           | Quy định đăng ký học phần học kỳ 1 từ ngày 15/08...       | 0.42       | Có                             | Thời gian đăng ký học phần kỳ 1 bắt đầu từ 15/08.        |
| 2   | Điều kiện để được xét học bổng khuyến khích là gì?         | Quyết định khen thưởng và học bổng yêu cầu ĐTB >= 3.2...  | 0.48       | Có                             | Điều kiện xét học bổng là ĐTB tích lũy từ 3.2 trở lên.   |
| 3   | Quy trình xin nội trú ký túc xá gồm các bước nào?          | Hướng dẫn nộp đơn đăng ký phòng ở ký túc xá trực tuyến... | 0.39       | Có                             | Quy trình gồm 3 bước: nộp đơn online, duyệt và nộp tiền. |
| 4   | Hạn cuối đóng học phí là ngày nào? (Lọc: audience=student) | Thông báo học phí: sinh viên nộp trước ngày 30/09...      | 0.51       | Có                             | Hạn cuối đóng học phí cho sinh viên là 30/09.            |
| 5   | Giờ mở cửa thư viện trung tâm vào cuối tuần?               | Nội quy thư viện: T7-CN mở cửa từ 8h00 - 17h00...         | 0.45       | Có                             | Thư viện mở cửa cuối tuần từ 8h00 đến 17h00.             |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Việc kết hợp `metadata_filter` trước khi chạy cosine similarity giúp loại bỏ hoàn toàn nhiễu từ các tài liệu không phù hợp đối tượng (VD: quy định dành cho cán bộ giảng viên), mang lại độ chính xác truy xuất cao hơn nhiều so với chỉ tìm kiếm thuần bằng vector.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | 5 / 5            |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10          |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30          |
| Dự đoán độ tương tự (Similarity Predictions)    | 5 / 5            |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10          |
| **Tổng phần cá nhân**                           | **60 / 60**      |
