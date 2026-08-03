# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Thị Ngọc Lan
**Nhóm:** DMX
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> *Viết 1-2 câu: Độ tương tự Cosine cao có nghĩa là hai văn bản hoặc 2 vector có nội dung hoặc ngữ nghĩa rất giống nhau, bất kể độ dài của chúng*

**Ví dụ có độ tương tự CAO:**

- Câu A: Hôm nay trời đẹp
- Câu B: Thời tiết hôm nay rất đẹp
- Tại sao tương đồng: Vì hai câu cùng diễn đạt rằng trời đẹp, đều có ý nghĩa giống nhau

**Ví dụ có độ tương tự THẤP:**

- Câu A: Hôm nay trời đẹp
- Câu B: Tôi thích ăn vặt
- Tại sao khác: một câu là khen thời tiết, một câu là nêu sở thích, hai câu có ý nghĩa hoàn toàn khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> *Viết 1-2 câu: Đối với text embeddings thì cosine similarity được ưu tiên hơn khoảng cách Euclid vì mục tiêu là so sánh độ giống nhau về ngữ nghĩa chứ không phải là khoảng cách tuyệt đối giữa các vector*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính: chunks=**⌈(ducument_length-chunk_size)/(chunk_size-overlap)⌉+1
> ⌈(10000-500)/(500-50)⌉+1
> ⌈21,11⌉+1=22+1=23*
> *Đáp án: 23*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> *Viết 1-2 câu: Nếu độ chồng chéo (overlap) tăng từ 50 lên 100 thì số lượng chunk tăng từ 23 lên 25 do mỗi chunk mới dịch ít hơn nên cần nhiều chunk hơn để bao phủ toàn bộ tài liệu. Overlap lớn hơn giúp giữ được ngữ cảnh giữa các chunk, giảm nguy cơ mất thông tin khi nội dung bị cắt ở ranh giới giữa hai chunk.*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?
> Dùng biểu thức regex để tách tại các vị trí mà trước đó là dấu chấm, chấm than, và sau đó là khoảng trắng. Trước khi split nên chuẩn hóa ".\n" thành ". " để tránh lỗi khi câu kết thúc bằng dòng mới.
> Xử lý các trường hợp ngoại lệ (edge case):
>
> + Loại bỏ khoảng trắng thừa
> + Loại bỏ các phần rỗng sau khi split
> + Nếu text không có dấu câu rõ ràng thì giữ nguyên đoạn còn lại như 1 câu duy nhất

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?
> Thuật toán hoạt động bằng cách đệ quy chia text theo thứ tự ưu tiên: đầu tiên thử ngắt bằng \n\n rồi \n rồi . rồi khoảng trắng, cuối cùng là kí tự nếu cần. Hàm split lấy một đoạn text hiện tại và lặp qua các separator; nếu đoạn đó còn vượt quá kích thước chunk_size, nó sẽ gọi đệ quy với separator tiếp theo cho phần con. Base case là khi text rỗng hoặc có độ dài của đoạn nhỏ hơn hoặc bằng chunk_size, lúc đó trả về chính đoạn đó như một chunk cuối cùng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?
> add_documents tạo một record cho mỗi tài liệu bằng cách dùng embedding function để biến nội dung thành vector, rồi lưu kèm metadata và id vào store. search thì tạo embedding cho câu truy vấn, so sánh với các vector đã lưu bằng cosine similarity, sau đó trả về top-k kết quả có độ tương tự cao nhất*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?
> search_with_filter lọc hàm trước bằng cách lấy các bản ghi thỏa mãn metadata_filter trước, rồi mới chạy similarity search trên tập con đó. Delete_document thì xóa bằng id*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?
> answer dùng mẫu prompt theo kiểu RAG: đầu tiên lấy top-k chunk liên quan từ store, rồi gom chúng thành một khối context, sau đó tạo prompt theo cấu trúc “Context -> Question -> Answer”. Cách inject context vào là nối nội dung các chunk lại bằng dấu xuống dòng, đưa vào phần đầu prompt để LLM có thể dùng làm nền tảng trả lời.*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
===================================================================== test session starts =====================================================================
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
metadata: {'Python': '3.14.0', 'Platform': 'Windows-11-10.0.26200-SP0', 'Packages': {'pytest': '9.1.1', 'pluggy': '1.6.0'}, 'Plugins': {'anyio': '4.13.0', 'html': '4.2.0', 'metadata': '3.1.1', 'snapshot': '0.9.0', 'timeout': '2.4.0', 'xdist': '3.8.0'}, 'JAVA_HOME': 'C:\\Program Files\\Java\\jdk-11.0.1'}
rootdir: D:\AI lab\Day07-2A202601385-TranThiNgocLan
plugins: anyio-4.13.0, html-4.2.0, metadata-3.1.1, snapshot-0.9.0, timeout-2.4.0, xdist-3.8.0
collected 42 items                                                                                                                                         

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                                    [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                             [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                                      [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                                       [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                                            [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                                            [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                                  [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                                   [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                                 [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                                   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                                   [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                              [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                                          [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                                    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                                           [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                               [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                                         [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                               [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                                   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                                     [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                                       [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                             [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                                  [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                                    [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                                        [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                                     [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                              [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                             [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                                        [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                                    [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                               [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                                   [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                                         [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                                   [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                                [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                              [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                             [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                                 [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                                            [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                                     [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                                           [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                               [100%]

===================================================================== 42 passed in 0.09s ======================================================================
```

**Số lượng bài test vượt qua (pass):** _42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Điểm thực tế được tính bằng `compute_similarity()` trên embedding thật (backend `LocalEmbedder`, model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`), không dùng `MockEmbedder` vì mock chỉ băm hash nên không phản ánh ngữ nghĩa. Ngưỡng quy đổi cao/thấp: điểm ≥ 0.4 → cao, < 0.4 → thấp.

| Cặp | Câu A                                                                      | Câu B                                                                         | Dự đoán | Điểm thực tế | Đúng? |
| ---- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ---------- | ---------------- | ------- |
| 1    | Sinh viên cần đăng ký học phần trước thời hạn quy định.        | Việc đăng ký môn học phải hoàn thành đúng hạn theo lịch học vụ. | cao        | 0.7396           | Đúng  |
| 2    | Thư viện yêu cầu sinh viên xuất trình thẻ khi mượn sách.         | Để mượn tài liệu, sinh viên phải có thẻ định danh hợp lệ.        | cao        | 0.7771           | Đúng  |
| 3    | Học phần tiên quyết là điều kiện bắt buộc trước khi đăng ký. | Hôm nay thời tiết rất đẹp và trong lành.                               | thấp      | -0.0780          | Đúng  |
| 4    | Thư viện mở cửa từ 7 giờ sáng đến 9 giờ tối.                     | Tôi thích chơi bóng đá vào cuối tuần.                                 | thấp      | -0.0189          | Đúng  |
| 5    | Sinh viên nộp đơn xin học bổng trước ngày 30 tháng 9.             | Học phí kỳ này tăng do điều chỉnh theo quy định mới.                | cao        | 0.1342           | Sai     |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Cặp 5 gây bất ngờ nhất: tôi dự đoán "cao" vì cả hai câu đều thuộc chủ đề tài chính sinh viên (học bổng, học phí) và đều có mốc thời gian/quy định, nhưng điểm thực tế chỉ 0.1342 — gần như không liên quan. Điều này cho thấy embedding đo *ý nghĩa nội dung cụ thể* (hành động nộp đơn xin học bổng vs. việc học phí tăng) chứ không đo *chủ đề chung chung*; hai câu tuy cùng miền chủ đề đại học nhưng khác hẳn về đối tượng, hành động và ý định câu nên bị tách xa nhau trong không gian vector.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| - | ----------------- | ------------------------------------------ | ------------ | --------------------------------- | ------------------------------------- |
| 1 |                   |                                            |              |                                   |                                       |
| 2 |                   |                                            |              |                                   |                                       |
| 3 |                   |                                            |              |                                   |                                       |
| 4 |                   |                                            |              |                                   |                                       |
| 5 |                   |                                            |              |                                   |                                       |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5/ 5                   |
| Hướng tiếp cận của tôi (My Approach)           | 10/ 10                 |
| Hoàn thiện code (Core Implementation — tests)     | 30/ 30                 |
| Dự đoán độ tương tự (Similarity Predictions) | 4/ 5                   |
| Kết quả truy xuất của tôi (Competition Results) | / 10                   |
| **Tổng phần cá nhân**                      | **/ 60**         |
