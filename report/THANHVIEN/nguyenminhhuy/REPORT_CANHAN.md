# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Minh Huy
**Nhóm:** B05
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> *Viết 1-2 câu:*
>
> ```
> Độ tương tự cosine cao nghĩa là vector embedding của hai văn bản có
> hướng gần giống nhau. Hai văn bản thường nói về cùng chủ đề hoặc mang
> ý nghĩa tương tự
> ```

**Ví dụ có độ tương tự CAO:**

- Câu A: `Sinh viên phải đóng học phí trước ngày 15 tháng 9.`
- Câu B: `Hạn cuối để sinh viên thanh toán học phí là ngày 15 tháng 9.`
- Tại sao tương đồng: `Hai câu cùng nói về thời hạn đóng học phí.`

**Ví dụ có độ tương tự THẤP:**

- Câu A: `Sinh viên phải đóng học phí trước ngày 15 tháng 9.`
- Câu B: `Cây phượng trong sân trường nở hoa vào mùa hè.`
- Tại sao khác: `Hai câu nói về những chủ đề không liên quan.`

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> *Viết 1-2 câu:*
>
> ```
> Cosine similarity tập trung vào hướng của vector, tức sự tương đồng về
> ngữ nghĩa, và ít bị ảnh hưởng bởi độ lớn vector. Khoảng cách Euclidean
> có thể thay đổi theo độ lớn vector hoặc độ dài văn bản.
> ```

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính: `Số chunk = ceil((10.000 - 50) / (500 - 50))`*
> *Đáp án: `23 chunks`*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> *Viết 1-2 câu:*
>
> ```
> Khi overlap tăng lên 100:
>
> Số chunk = ceil((10.000 - 100) / (500 - 100)) = 25 chunks.
>
> Overlap lớn hơn giúp giữ lại ngữ cảnh ở ranh giới giữa các chunk và
> giảm nguy cơ một ý quan trọng bị cắt đôi. Đổi lại, nó làm tăng số chunk,
> nội dung trùng lặp và chi phí xử lý.
> ```

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào? Tôi dùng regex với positive lookbehind để tách tại khoảng trắng đứng sau dấu chấm, dấu chấm than hoặc dấu hỏi, nhờ đó dấu câu vẫn được giữ lại. Sau đó tôi loại bỏ câu rỗng và gom các câu thành từng nhóm không vượt quá `max_sentences_per_chunk`; văn bản rỗng trả về danh sách rỗng.*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì? Tôi thử các separator theo thứ tự ưu tiên từ cấu trúc lớn đến nhỏ: đoạn văn, dòng, câu, từ và ký tự. Nếu một phần vẫn dài hơn `chunk_size`, hàm `_split` tiếp tục gọi đệ quy với separator kế tiếp; khi hết separator, thuật toán cắt cứng theo số ký tự. Các trường hợp cơ sở gồm văn bản rỗng, văn bản đã đủ ngắn và danh sách separator đã hết.*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao? Khi thêm tài liệu, tôi sao chép metadata, bổ sung `doc_id` nếu còn thiếu, tạo embedding từ nội dung và lưu record với một ID duy nhất. Khi tìm kiếm, truy vấn cũng được chuyển thành embedding; store tính tích vô hướng với từng embedding đã lưu, sắp xếp điểm giảm dần và trả về tối đa `top_k` kết quả.*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào? Với tìm kiếm có bộ lọc, tôi lọc trước các record thỏa mãn đồng thời tất cả điều kiện metadata, sau đó mới tính điểm tương tự và lấy top-k. Khi xóa tài liệu, tôi loại bỏ tất cả record có cùng `metadata["doc_id"]`; hàm trả về `True` nếu kích thước store giảm hoặc có ID được xóa, ngược lại trả về `False`.*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào? Phương thức `answer` dùng câu hỏi để truy xuất top-k chunk từ `EmbeddingStore`, sau đó ghép nội dung và nguồn của các chunk thành phần context trong prompt. Prompt yêu cầu LLM chỉ trả lời dựa trên context, không tự tạo dữ kiện và thông báo khi tài liệu không cung cấp đủ thông tin; cuối cùng prompt được truyền vào `llm_fn`.*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
(.venv) PS C:\Users\hweem\Documents\aia\Day07-2A202601303-NguyenMinhHuy> python -m pytest tests/ -v
============================================= test session starts ==============================================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\hweem\Documents\aia\Day07-2A202601303-NguyenMinhHuy\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\hweem\Documents\aia\Day07-2A202601303-NguyenMinhHuy
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                     [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                              [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                       [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                        [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                             [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED             [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                   [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                    [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                  [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                    [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                    [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                               [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                           [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                     [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED            [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED          [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                    [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                      [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                        [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                              [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                   [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                     [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED         [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                      [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                               [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                              [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                         [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                     [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                    [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                          [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                    [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED               [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED              [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED  [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED             [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED      [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================================== 42 passed in 0.09s ==============================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán  | Điểm thực tế | Đúng? |
| ---- | ------ | ------ | ----------- | ---------------- | ------- |
| 1 | Thư viện mở cửa lúc 8 giờ sáng. | Thư viện bắt đầu phục vụ lúc 08h00. | Cao | 0.8993 | Có |
| 2 | Bạn đọc cần mang Căn cước công dân. | Khi check-in phải xuất trình CCCD. | Cao | 0.2502 | Không |
| 3 | Phòng đọc nằm ở tầng 4. | Lệ phí làm thẻ là 100.000 đồng. | Thấp | 0.0860 | Có |
| 4 | Thư viện sử dụng hệ thống phân loại LC. | Sách được sắp xếp dựa theo bảng LC. | Cao | 0.7324 | Có |
| 5 | Không được mang sách ra khỏi phòng đọc. | QA800 là tài liệu Cơ lý thuyết. | Thấp | 0.0488 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> *Viết 2-3 câu:*
>
> Bất ngờ nhất là cặp 2 chỉ đạt `0.2502` dù “Căn cước công dân” và “CCCD” cùng chỉ một loại giấy tờ. Kết quả cho thấy embedding có thể nhận diện tốt các câu diễn đạt tương đương khi từ ngữ đầy đủ, nhưng vẫn gặp khó với chữ viết tắt hoặc cách biểu đạt quá ngắn; vì vậy similarity ngữ nghĩa không phải lúc nào cũng phản ánh đúng quan hệ mà con người nhận thấy.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Thiết lập đánh giá: bộ 7 tài liệu HUST trong `data/b05-hust-library` của repo cá nhân (cùng nội dung với `data/k3_university` trong repo nhóm), `LocalEmbedder` với model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, `SentenceChunker(max_sentences_per_chunk=4)`, 22 chunks và `top_k=3`. Điểm top-1 trung bình của 5 câu là `(0.7338 + 0.7027 + 0.5297 + 0.6400 + 0.4268) / 5 = 0.6066`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| - | ----------------- | ------------------------------------------ | ------------ | --------------------------------- | ------------------------------------- |
| 1 | Thư viện mở cửa lúc mấy giờ vào cuối tuần? | `hust-gio-phuc-vu`: phòng tự học 301, 303, 401, 418 mở từ 8h00–19h00 cả thứ 7 và Chủ nhật. | 0.7338 | Có | Cuối tuần, các phòng tự học 301, 303, 401 và 418 mở 8h00–19h00; lịch phòng đọc chuyên ngành trong cao điểm thi là 8h00–16h00 theo thông báo. |
| 2 | Để làm thẻ thư viện cần mang theo giấy tờ gì? | `hust-noi-quy-thu-vien`: yêu cầu xuất trình thẻ hợp lệ và liệt kê các loại thẻ bạn đọc. | 0.7027 | Có một phần | Top-3 nêu các loại thẻ hợp lệ nhưng chưa chứa đoạn yêu cầu ảnh thẻ và Căn cước công dân, nên ngữ cảnh truy xuất chưa đủ để trả lời trọn vẹn thủ tục làm thẻ. |
| 3 | Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng mấy? | `hust-noi-quy-thu-vien`: quy định xuất trình thẻ khi vào phòng đọc, không chứa vị trí phòng 402. | 0.5297 | Không | Không đủ căn cứ từ top-3 để xác định tầng; chunk liên quan `hust-tai-lieu-phong-doc` chỉ đứng hạng 6 và ghi `PHÒNG 402`, từ đó mới có thể suy ra tầng 4. |
| 4 | Hệ thống phân loại sách nào được sử dụng trong thư viện? | `hust-sap-xep-kho-mo`: tài liệu được sắp xếp dựa theo bảng LC, tiếp theo là chỉ số Cutter. | 0.6400 | Có | Thư viện Tạ Quang Bửu sử dụng phân loại LC; thứ tự xếp giá còn xét Cutter, số tập, năm xuất bản và số bản copy. |
| 5 | Có được phép mượn giáo trình Cơ lý thuyết về nhà không? | `hust-quy-trinh-muon-tra`: chính sách Phòng 111 cho mượn tối đa 8 cuốn trong 90 ngày và được gia hạn. | 0.4268 | Có một phần | Top-3 có chính sách mượn và danh mục chứa dải `QA800–QA899`, nhưng bằng chứng về đúng đầu sách “Cơ lý thuyết” bị tách rời; chỉ có thể kết luận có điều kiện nếu tài liệu đó thuộc kho mượn Phòng 111. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5. Câu 3 không có chunk vị trí Phòng 402 trong top-3; câu 5 có hai mảnh thông tin liên quan nhưng chưa được nối thành một bằng chứng hoàn chỉnh.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> *Viết 2-3 câu:*
>
> Qua so sánh trong nhóm, tôi học được rằng `RecursiveChunker` phù hợp hơn với tài liệu Markdown và dữ liệu OCR dạng danh sách vì nó ưu tiên ranh giới đoạn, dòng rồi mới đến câu. `SentenceChunker` giữ tốt các quy định viết thành câu hoàn chỉnh, nhưng có thể gom cả bảng thành chunk rất lớn hoặc tách mất quan hệ giữa tên phòng, số phòng và nhóm tài liệu khi nguồn thiếu dấu câu chuẩn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                    |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                   |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                   |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5                    |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10                   |
| **Tổng phần cá nhân**                      | **60 / 60**         |
