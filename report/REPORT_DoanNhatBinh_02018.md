# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đoàn Nhật Bình
**Nhóm:** C11
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Nghĩa là hai vector có hướng gần giống nhau. Giá trị cosine similarity càng gần 1 thì mức độ tương đồng càng cao.*

**Ví dụ có độ tương tự CAO:**
- Câu A: Hôm nay trời rất nóng
- Câu B: Hôm nay trời oi quá
- Tại sao tương đồng: Cả hai câu đều diễn đạt thời tiết hôm nay nóng

**Ví dụ có độ tương tự THẤP:**
- Câu A: Tôi đang học AI thực chiến
- Câu B: Cái laptop đang ở trên bàn
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Cosine similarity chỉ so sánh hướng của các vector nên phản ánh tốt sự tương đồng về ngữ nghĩa. Euclidean distance bị ảnh hưởng bởi độ lớn của vector nên kém phù hợp hơn với text embeddings.*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính: Bước nhảy (stride) = chunk_size - overlap = 500 -50 = 450
Số chunk = ⌈(10000 - 500) / 450⌉ + 1 = [21.11] + 1 = 22 + 1 = 23*
> *Đáp án:23 chunks*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Overlap tăng lên 100 thì stride giảm còn 400, nên số lượng chunk tăng lên thành 25 chunks. Overlap lớn hơn giúp giữ ngữ cảnh giữa các chunk, giảm nguy cơ mất thông tin ở ranh giới giữa hai chunk.*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Mình dùng regex `(?<=[.!?])[ \t]+|\n+` để tách câu tại các dấu `.`, `!`, `?` khi phía sau có khoảng trắng hoặc xuống dòng, đồng thời giữ lại dấu câu trong câu. Trước khi chia, hàm xử lý chuỗi rỗng hoặc chỉ có khoảng trắng bằng cách trả về `[]`, sau đó chuẩn hóa nhiều khoảng trắng và gom tối đa `max_sentences_per_chunk` câu vào mỗi chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán thử các separator theo thứ tự ưu tiên `\n\n`, `\n`, `. `, khoảng trắng và cuối cùng là chuỗi rỗng; nếu một separator không xuất hiện thì chuyển sang separator tiếp theo. `_split` gom các phần liên tiếp nếu tổng độ dài không vượt `chunk_size`, còn phần quá dài sẽ được đệ quy tách bằng separator có độ ưu tiên thấp hơn. Base case là khi văn bản đã ngắn hơn hoặc bằng `chunk_size`; nếu không còn separator thì cắt trực tiếp theo số ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Mỗi `Document` được chuẩn hóa thành record gồm id nội bộ, nội dung, metadata và embedding tạo bởi `embedding_fn`; hệ thống ưu tiên lưu vào ChromaDB, nếu ChromaDB không khả dụng hoặc gặp lỗi thì dùng danh sách in-memory. Khi tìm kiếm, query cũng được chuyển thành embedding rồi so sánh với các vector đã lưu bằng dot product, sắp xếp điểm giảm dần và trả về tối đa `top_k` kết quả kèm content, metadata và score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Metadata được lọc trước khi tính độ tương đồng: với ChromaDB, filter được truyền vào `where`, còn bộ nhớ in-memory chỉ giữ các record thỏa tất cả cặp key-value rồi mới search. `delete_document` xóa toàn bộ chunk có `metadata["doc_id"]` trùng với id tài liệu; hàm trả về `True` nếu có record bị xóa và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Hàm `answer` kiểm tra câu hỏi và `top_k`, gọi `store.search` để lấy các chunk liên quan rồi đánh số từng chunk dưới dạng `[Context 1]`, `[Context 2]` trước khi ghép vào prompt. Prompt yêu cầu agent chỉ sử dụng phần context, nói rõ khi thiếu thông tin và không tự bịa dữ kiện; sau đó chèn câu hỏi của người dùng vào mục `Question` và chuyển toàn bộ prompt cho `llm_fn` để sinh câu trả lời. Nếu không lấy được context, hàm trả về thông báo không tìm thấy thông tin phù hợp.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED         [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                  [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED           [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED            [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                 [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED       [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED        [ 19%] 
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED      [ 21%] 
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                        [ 23%] 
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED        [ 26%] 
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                   [ 28%] 
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED               [ 30%] 
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                         [ 33%] 
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED    [ 38%] 
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED    [ 42%] 
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                        [ 45%] 
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED          [ 47%] 
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED            [ 50%] 
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                  [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED       [ 54%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED         [ 57%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED          [ 61%] 
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                   [ 64%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                  [ 66%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED             [ 69%] 
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED         [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED    [ 73%] 
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED        [ 76%] 
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED              [ 78%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED        [ 80%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED   [ 85%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED  [ 88%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|--------|--------|---------|--------------|-------|
| 1 | Tôi thích uống cà phê vào buổi sáng. | Buổi sáng tôi thường uống một ly cà phê. | Cao | **0.9208** | Đúng |
| 2 | Hôm nay trời mưa rất to. | Tôi đang học môn Trí tuệ nhân tạo. | Thấp | **0.11** | Đúng |
| 3 | Sinh viên cần nộp bài trước thứ Sáu. | Hạn nộp bài của sinh viên là trước thứ Sáu. | Cao | **0.9506** | Đúng |
| 4 | Python là một ngôn ngữ lập trình phổ biến. | Tôi vừa đi sở thú để xem trăn và rắn. | Thấp | **0.2897** | Đúng |
| 5 | Cô ấy mua một chiếc xe mới hôm qua. | Hôm qua cô ấy đã mua một chiếc ô tô mới. | Cao | **0.9258** | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Cặp 4 là kết quả đáng chú ý nhất vì từ "Python" có thể gợi liên tưởng đến loài rắn, nhưng embedding vẫn đánh giá độ tương tự thấp do hai câu thuộc hai ngữ cảnh hoàn toàn khác nhau. Điều này cho thấy embeddings biểu diễn ý nghĩa của cả câu dựa trên ngữ cảnh và quan hệ ngữ nghĩa, thay vì chỉ so khớp các từ khóa giống nhau.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-----------------|--------------------------------------|------------|--------------------------------|---------------------------------|
| 1 | Mỗi học kỳ, sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ? | Quy định khối lượng học tập: mỗi học kỳ sinh viên đăng ký tối thiểu 08 tín chỉ và tối đa 16 tín chỉ. | **0.6723** | Có | Mỗi học kỳ, sinh viên được đăng ký tối thiểu 08 tín chỉ và tối đa 16 tín chỉ. |
| 2 | Nếu sinh viên còn nợ học phí của học kỳ trước thì điều gì xảy ra khi đăng ký học kỳ tiếp theo? | Quy định sinh viên còn nợ học phí sẽ không được đăng ký học phần của học kỳ tiếp theo. | **0.6436** | Có | Sinh viên còn nợ học phí sẽ không được đăng ký học phần của học kỳ tiếp theo. |
| 3 | Sinh viên đạt học bổng khuyến khích học tập Loại A được nhận mức học bổng bằng bao nhiêu phần trăm số học phí đã nộp? | Quy định mức học bổng Loại A bằng 50% số học phí sinh viên đã nộp. | **0.6029** | Có | Sinh viên đạt học bổng Loại A được nhận 50% số học phí đã nộp. |
| 4 | Chi phí ở ký túc xá phòng 8 sinh viên là bao nhiêu mỗi tháng? | Bảng mức phí ký túc xá quy định phòng 8 sinh viên có giá 350.000 VNĐ/sinh viên/tháng. | **0.6979** | Có | Chi phí ở ký túc xá phòng 8 sinh viên là 350.000 VNĐ/sinh viên/tháng. |
| 5 | Khu tự học ở tầng 6 của thư viện mở cửa vào những khung giờ nào? | Quy định giờ mở cửa khu tự học tầng 6 từ thứ 2 đến Chủ nhật, 6h30–22h. | **0.6539** | Có | Khu tự học ở tầng 6 mở cửa từ thứ 2 đến Chủ nhật, từ 6h30 đến 22h. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Tôi học được rằng chiến lược chunking ảnh hưởng trực tiếp đến chất lượng truy xuất, không chỉ phụ thuộc vào mô hình embedding. Việc chia chunk theo cấu trúc tài liệu hoặc điều chỉnh kích thước và overlap hợp lý có thể giúp nội dung quan trọng không bị cắt rời, từ đó cải thiện thứ hạng của chunk liên quan.*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **57/ 60** |
