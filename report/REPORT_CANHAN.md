# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hoàng Mạnh Dũng
**Nhóm:** Dịch vụ và quy định đăng ký học phần dành cho sinh viên HUST
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai đoạn văn bản có vector biểu diễn nhắm về cùng một hướng trong không gian ngữ nghĩa đa chiều, thể hiện nội dung/chủ đề của chúng rất tương đồng với nhau bất kể độ dài ngắn của đoạn văn.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên thực hiện đăng ký học phần trên hệ thống CTT HUST."
- Câu B: "Người học tiến hành đăng ký lớp môn học qua cổng thông tin đào tạo Đại học Bách Khoa."
- Tại sao tương đồng: Cả hai câu cùng diễn tả hành vi đăng ký môn học của sinh viên HUST trên cổng trực tuyến.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Quy định về thời hạn nộp học phí học phần tín chỉ HUST."
- Câu B: "Hướng dẫn nấu ăn món phở bò truyền thống Hà Nội."
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn riêng biệt (quy định học vụ Bách Khoa vs ẩm thực).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự cosine chỉ đo góc giữa các vector (hướng ý nghĩa) mà không phụ thuộc vào độ lớn (magnitude) của vector. Khoảng cách Euclid dễ bị ảnh hưởng bởi độ dài văn bản (văn bản dài có độ lớn vector lớn hơn), dẫn tới đánh giá sai lệch dù hai đoạn có cùng nội dung.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11) = 23`
> *Đáp án:* 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100: `làm_tròn_lên((10000 - 100) / (500 - 100)) = làm_tròn_lên(9900 / 400) = làm_tròn_lên(24.75) = 25` chunks. Số lượng chunk tăng từ 23 lên 25. Ta muốn tăng độ chồng chéo để bảo tồn ngữ cảnh liên tục ở ranh giới giữa các chunk, tránh việc câu hoặc ý quan trọng bị cắt đôi gây mất thông tin khi truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng `re.split(r'(?<=[.!?])\s+|\n+', text)` để tách các câu dựa trên dấu chấm, cảm, hỏi hoặc xuống dòng. Sau đó gom nhóm tối đa `max_sentences_per_chunk` câu vào một chunk string. Xử lý văn bản rỗng và loại bỏ khoảng trắng thừa ở mỗi ranh giới câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng chiến lược chia nhỏ đệ quy theo danh sách phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Base case là khi đoạn văn bản có độ dài `<= chunk_size` hoặc danh sách phân cách đã hết (fallback về cắt theo ký tự). Thuật toán gộp các đoạn nhỏ theo dấu phân cách hiện tại cho đến khi chạm hạn mức `chunk_size`, nếu gặp đoạn quá dài sẽ đệ quy chia tiếp bằng dấu phân cách cấp thấp hơn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ dữ liệu dưới dạng danh sách `list[dict]` gồm `id`, `content`, `metadata` và `embedding` (được tính bằng `self._embedding_fn`). Khi tìm kiếm, tính dot product giữa vector câu hỏi và vector của tất cả các chunk trong kho, sắp xếp giảm dần theo điểm số score và trả về top-k kết quả cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tiến hành pre-filtering trước: lọc các chunk thỏa mãn tất cả cặp điều kiện trong `metadata_filter`, sau đó mới thực hiện tìm kiếm tương đồng trên tập đã lọc. Với `delete_document`, duyệt loại bỏ tất cả chunk có `metadata['doc_id'] == doc_id` hoặc ID bắt đầu với `doc_id::` và trả về `True` nếu có ít nhất 1 chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Nhận câu hỏi, gọi `store.search(question, top_k)` để lấy danh sách chunk liên quan nhất. Nối nội dung các chunk phân cách bằng `\n---\n` tạo thành đoạn `Context`, xây dựng prompt chuẩn gồm `Context` + `Question` và truyền cho `llm_fn` tạo câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
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

============================= 42 passed in 0.42s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
| --- | ----------------------------------------------------------------- | ------------------------------------------------------------------------ | ------- | ----------------------------- | ------------------ |
| 1   | Sinh viên đăng ký học phần trên portal ctt.hust.edu.vn.           | Sinh viên truy cập hệ thống đăng ký môn học trực tuyến Bách Khoa.        | cao     | -0.1160 (Mock) / 0.88 (Local) | Đúng ngữ nghĩa     |
| 2   | Quy định về thời hạn nộp học phí tín chỉ HUST.                    | Lịch thi kết thúc học phần và lịch nghỉ lễ của trường.                   | thấp    | 0.1867                        | Đúng (khác chủ đề) |
| 3   | Sinh viên bị cảnh báo học tập chỉ được đăng ký tối đa 14 tín chỉ. | Sinh viên học lực bình thường đăng ký tối đa 24 tín chỉ mỗi học kỳ.      | cao     | -0.0300                       | Tương đối          |
| 4   | Học phần tiên quyết T yêu cầu đạt điểm D trở lên ở môn trước.     | Hướng dẫn nấu ăn món phở bò truyền thống Hà Nội.                         | thấp    | 0.1520                        | Đúng               |
| 5   | Cố vấn học tập duyệt đơn đăng ký vượt tải cho sinh viên.          | Giảng viên hướng dẫn duyệt kế hoạch học tập của sinh viên trên hệ thống. | cao     | 0.2214                        | Đúng               |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Điểm bất ngờ nhất là khi sử dụng MockEmbedder (dựa trên hash md5), hai câu đồng nghĩa (Cặp 1) lại cho điểm số âm (-0.1160) do vector được tạo ngẫu nhiên giả lập. Khi chuyển sang mô hình nhúng ngữ nghĩa thật (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`), Cặp 1 đạt điểm rất cao (>0.85). Điều này khẳng định embeddings học máy thực sự mã hóa được quan hệ ngữ nghĩa sâu sắc của câu tiếng Việt chứ không chỉ so sánh trùng khớp từ vựng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên bình thường và bị cảnh báo tại HUST được đăng ký tối đa bao nhiêu tín chỉ? | hust-credit-training-regulation::chunk_0 (SV bình thường 12-24 TC, cảnh báo 10-14 TC) | 0.2126 | Có | SV bình thường đăng ký 12-24 TC, bị cảnh báo đăng ký 10-14 TC. |
| 2 | Các bước thao tác đăng ký lớp môn học trên cổng CTT HUST? | hust-course-registration-system-guide::chunk_0 (Đăng nhập CTT, chọn lớp kíp học, lưu phiếu) | 0.2013 | Có | Đăng nhập CTT, chọn Đăng ký lớp, chọn kíp học và xác nhận đăng ký. |
| 3 | Hạn nộp học phí tín chỉ HUST và chế tài xử lý khi chậm nộp? | hust-tuition-by-credits::chunk_0 (Hạn nộp học phí theo kỳ, chậm nộp bị hủy danh sách) | 0.2017 | Có | Nộp học phí theo hạn thông báo; chậm nộp bị hủy đăng ký lớp và khóa kỳ sau. |
| 4 | Thời gian đăng ký kế hoạch học tập kỳ 1 năm học 2026-2027? | hust-study-plan-2026::chunk_0 (Đăng ký kế hoạch kỳ 20261 thực hiện từ tháng 3/2026) | 0.2829 | Có | Đăng ký kế hoạch học tập kỳ 20261 thực hiện từ đợt tháng 3/2026 CTT 27235. |
| 5 | Sinh viên chương trình hợp tác quốc tế (SIE) có quy định gì khi đăng ký môn thay thế? (filter: audience=sie-student) | hust-sie-course-substitution::chunk_0 (Hướng dẫn SIE đăng ký môn thay thế) | 0.2375 | Có | Sinh viên SIE đăng ký môn thay thế theo hướng dẫn riêng của SoICT HUST. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc áp dụng chiến lược `RecursiveChunker` kết hợp phân tách theo tiêu đề Markdown (`#`, `##`) giúp giữ nguyên cấu trúc các mục quy chế Bách Khoa. Ngoài ra, việc dùng `metadata_filter` theo đối tượng `audience` giúp loại bỏ hoàn toàn nhiễu từ tài liệu hướng dẫn dành cho nhóm đối tượng khác.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
