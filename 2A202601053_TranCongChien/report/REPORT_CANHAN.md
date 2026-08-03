# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Công Chiến
**Nhóm:** Nhóm 1
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> *Viết 1-2 câu:* Độ tương tự cosine cao có nghĩa là hai vector embedding hướng về gần cùng một hướng trong không gian vector, cho thấy ngữ nghĩa (semantic) của hai đoạn văn bản tương ứng rất giống nhau.

**Ví dụ có độ tương tự CAO:**

- Câu A: "Tôi rất thích ăn phở bò."
- Câu B: "Món phở bò là món ăn yêu thích của tôi."
- Tại sao tương đồng: Cả hai câu đều mang cùng một ý nghĩa về sở thích ăn uống đối với món phở (Thực tế khi chạy qua OpenAI text-embedding-3-small, Cosine Similarity đạt mức rất cao: **0.8394**).

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Hôm nay trời nắng đẹp."
- Câu B: "Thị trường chứng khoán đang giảm điểm mạnh."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn không liên quan đến nhau (thời tiết và tài chính). Khi đo đạc thực tế qua model OpenAI, độ tương đồng chỉ ở mức rất thấp là **0.3444**.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> *Viết 1-2 câu:* Cosine similarity chỉ đo lường góc giữa hai vector mà không phụ thuộc vào độ lớn (magnitude) của chúng, giúp so sánh chính xác mức độ tương đồng về ngữ nghĩa giữa hai văn bản bất kể sự chênh lệch về độ dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính:* Số chunk = 1 + ceiling((Tổng số ký tự - chunk_size) / (chunk_size - overlap)) = 1 + ceiling((10000 - 500) / (500 - 50)) = 1 + ceiling(9500 / 450) = 1 + ceiling(21.11) = 23 chunks.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> *Viết 1-2 câu:* Nếu overlap tăng lên 100, số chunk sẽ tăng lên thành 25 (vì mẫu số giảm còn 400). Ta muốn độ chồng chéo nhiều hơn để đảm bảo không bị cắt đứt mạch ngữ nghĩa ở ranh giới giữa các chunk, giúp bảo toàn trọn vẹn ngữ cảnh khi truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
> Sử dụng regex như `(?<=[.!?])\s+` để tách câu dựa trên các dấu câu kết thúc. Cần xử lý các trường hợp ngoại lệ như từ viết tắt (vd: "Mr.", "Dr.") hoặc chuỗi có nhiều khoảng trắng để tránh việc cắt xén câu sai logic.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
> Thuật toán đệ quy chia văn bản theo các dấu phân cách (separators) từ lớn đến nhỏ (ví dụ: `\n\n`, `\n`, khoảng trắng). Trường hợp cơ sở là khi đoạn văn bản nhỏ hơn giới hạn `chunk_size` hoặc không còn dấu phân cách nào có thể dùng để chia tiếp.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
> Tài liệu đầu vào sẽ được nhúng (embed) thành vector và lưu trong bộ nhớ hoặc cơ sở dữ liệu vector cùng với metadata tương ứng. Hàm search sẽ tính toán độ tương tự Cosine giữa vector của câu hỏi truy vấn và vector của các tài liệu trong kho để trả về Top K tài liệu liên quan nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
> Việc lọc thường được thực hiện kết hợp cùng quá trình tìm kiếm (lọc trước thông qua metadata) nhằm tối ưu hoá không gian tìm kiếm. Hàm xóa được thực thi bằng cách lấy ID của document và loại bỏ phần tử/vector tương ứng ra khỏi hệ thống lưu trữ.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
> Prompt được thiết kế sao cho có phần chỉ dẫn (system instruction) yêu cầu agent trả lời dựa trên ngữ cảnh. Sau đó, ngữ cảnh (các chunk liên quan từ kết quả truy xuất) sẽ được inject thẳng vào trong prompt trước hoặc sau câu hỏi của người dùng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
(day07-2a202601053-trancongchien) tcc3281@tcc3281-ThinkPad-T14s-Gen-3:/data/vinai/labs/DAY07_2A202601053_TranCongChien$ pytest tests/ -v
======================================================================== test session starts =========================================================================
platform linux -- Python 3.11.0rc1, pytest-9.1.1, pluggy-1.6.0 -- /data/vinai/labs/DAY07_2A202601053_TranCongChien/.venv/bin/python
cachedir: .pytest_cache
rootdir: /data/vinai/labs/DAY07_2A202601053_TranCongChien
configfile: pyproject.toml
collected 42 items                                                                                                                                               

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                                          [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                                   [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                                            [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                                             [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                                                  [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                                                  [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                                        [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                                         [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                                       [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                                         [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                                         [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                                    [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                                                [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                                          [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                                                 [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                                     [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                                               [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                                     [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                                         [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                                           [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                                             [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                                   [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                                        [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                                          [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                                              [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                                           [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                                    [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                                   [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                                              [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                                          [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                                     [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                                         [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                                               [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                                         [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                                      [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                                    [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                                   [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                                       [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                                                  [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                                           [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                                                 [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                                     [100%]

========================================================================= 42 passed in 0.07s =========================================================================
(day07-2a202601053-trancongchien) tcc3281@tcc3281-ThinkPad-T14s-Gen-3:/data/vinai/labs/DAY07_2A202601053_TranCongChien$
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                                                                                     | Câu B                                                                                                | Dự đoán | Điểm thực tế | Đúng? |
| ---- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------- | ---------------- | ------- |
| 1    | "Con mèo nhà em rất dễ thương và đáng yêu, nó thường cuộn tròn ngủ trên ghế sofa"        | "Chú mèo trắng này trông thật dễ thương và đáng yêu, nó hay nằm ngủ ngoài ban công" | cao        | 0.6388           | Đúng  |
| 2    | "Trí tuệ nhân tạo đang phát triển mạnh mẽ và nhanh chóng, ảnh hưởng đến nhiều lĩnh vực" | "AI đang phát triển rất nhanh và mạnh mẽ, làm thay đổi sâu sắc mọi ngành nghề"         | cao        | 0.5970           | Đúng  |
| 3    | "Anh ấy rất thích uống cà phê đen nóng vào mỗi buổi sáng trước khi đi làm"                 | "Cà phê đen là thức uống yêu thích của tôi mỗi buổi sáng khi thức dậy"                 | cao        | 0.7570           | Đúng  |
| 4    | "Tôi thường đi học bằng xe đạp đến trường vào mỗi buổi sáng sớm"                          | "Món phở bò nóng hổi này có hương vị thơm ngon và nước dùng rất đậm đà"           | thấp      | 0.2249           | Đúng  |
| 5    | "Bầu trời hôm nay trong xanh và rất đẹp, không một gợn mây"                                     | "Chiếc máy tính xách tay mới của tôi có cấu hình mạnh và chạy rất mượt mà"           | thấp      | 0.2829           | Đúng  |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> *Viết 2-3 câu:* Cả 5 cặp đều đúng dự đoán, với sự phân tách rõ rệt giữa hai nhóm: các cặp "cao" đạt 0.60–0.76 còn các cặp "thấp" chỉ quanh 0.22–0.28. Điểm đáng chú ý nhất là cặp 2 — hai câu diễn đạt cùng một ý bằng hình thức từ khác nhau hoàn toàn ("Trí tuệ nhân tạo" ↔ "AI", vị ngữ cũng không trùng nguyên văn) nhưng vẫn đạt 0.5970. Điều này cho thấy embeddings thực sự bắt được ý nghĩa ngữ nghĩa tiềm ẩn (semantic meaning) chứ không chỉ đơn thuần là so khớp từ khóa (keyword matching).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query)                                                                                          | Top-1 Chunk truy xuất được (tóm tắt)                                                                      | Điểm Score | Có liên quan không? (Relevant)  | Câu trả lời của Agent (tóm tắt)                                                                                                                                                                                                                                              |
| - | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------ | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Điều kiện xét cấp học bổng khuyến khích học tập cho sinh viên là gì?                         | `hoc_bong_diem_ren_luyen` — Quy định tiêu chuẩn xét học bổng KKHT                                     | 0.6702       | Có                                | Sinh viên trong thời hạn đào tạo chuẩn, kết quả học tập & rèn luyện đạt từ khá trở lên, không bị kỷ luật từ mức khiển trách, tích lũy ≥ 15 tín chỉ trong kỳ xét.                                                                                 |
| 2 | Mức điểm chuẩn chung khi đánh giá điểm rèn luyện cho sinh viên không vi phạm là bao nhiêu? | `hoc_bong_diem_ren_luyen` — Mức điểm chuẩn chung, tổng 5 nội dung = 70                                 | 0.6455       | Có                                | 70 điểm (tổng của 5 mức điểm chuẩn từng nội dung); sau đó mới cộng (thưởng)/trừ (phạt) điểm.                                                                                                                                                                   |
| 3 | Đối tượng sinh viên nào được hưởng chính sách giảm 50% học phí?                            | `hoc_phi_che_do_chinh_sach` — Top-1 là chunk "giảm 70% học phí" (chunk chính xác 50% chưa vào top-3) | 0.7193       | Có (đúng tài liệu, chunk 70%) | Top-1 trả về nhóm giảm 70% (sinh viên dân tộc thiểu số). Chunk "50%" chưa nằm trong top-3 với SentenceChunker; Recursive bắt đúng: con cán bộ/CCVC có cha hoặc mẹ bị tai nạn lao động hoặc bệnh nghề nghiệp được hưởng trợ cấp thường xuyên. |
| 4 | Sinh viên liên hệ đơn vị nào để làm thủ tục khám chữa bệnh và thanh toán BHYT?            | `kham_chua_benh` — Quy định khám sức khỏe & KCB/BHYT                                                    | 0.6558       | Có                                | Liên hệ Phòng Công tác Sinh viên để được hướng dẫn thủ tục KCB & thanh toán BHYT; khám sức khỏe nhập học tại Bệnh viện ĐHQGHN.                                                                                                                           |
| 5 | Cổng thủ tục hành chính một cửa giải quyết công việc gì cho sinh viên?                        | `thu_tuc_hanh_chinh_mot_cua` (SentenceChunker gộp cả file thành 1 chunk)                                   | 0.5226       | Có                                | Cho phép sinh viên nộp/xin thủ tục giấy tờ hành chính trực tuyến với Phòng CTSV mà không cần đến trực tiếp.                                                                                                                                                    |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (đúng tài liệu cả 5; riêng Q3 chunk "50%" chưa vào top-3 với SentenceChunker).

### So sánh 3 chiến thuật chunking (cùng bộ tài liệu `uet_handbook`)

Số chunk mỗi tài liệu theo từng chiến thuật (chạy bằng chính `src/` của tôi):

| Tài liệu                        | FixedSize (250/50) | Sentence (max=3) | Recursive (300) |
| --------------------------------- | ------------------ | ---------------- | --------------- |
| `hoc_bong_diem_ren_luyen.md`    | 25                 | 8                | 63              |
| `hoc_phi_che_do_chinh_sach.md`  | 26                 | 5                | 77              |
| `kham_chua_benh.md`             | 11                 | 3                | 29              |
| `ky_tuc_xa.md`                  | 6                  | 2                | 18              |
| `lich_su_truyen_thong.md`       | 9                  | 6                | 32              |
| `thong_tin_lien_he.md`          | 13                 | 4                | 55              |
| `thu_tuc_hanh_chinh_mot_cua.md` | 17                 | 1                | 46              |
| **Tổng**                   | **107**      | **29**     | **320**   |

**Chất lượng truy xuất top-1 theo chiến thuật** (score cao nhất cho câu hỏi tương ứng):

| # | Câu hỏi             | FixedSize          | Sentence           | Recursive                           |
| - | --------------------- | ------------------ | ------------------ | ----------------------------------- |
| 1 | Học bổng KKHT       | 0.6697             | 0.6702             | 0.6540                              |
| 2 | Điểm rèn luyện 70 | 0.6359             | 0.6455             | 0.6554                              |
| 3 | Giảm 50% học phí   | 0.6590 (chunk 70%) | 0.7193 (chunk 70%) | **0.7819 (đúng chunk 50%)** |
| 4 | KCB & BHYT            | 0.6254             | 0.6558             | 0.6310                              |
| 5 | Cổng một cửa       | 0.6243             | 0.5226             | **0.6474**                    |

**Nhận xét:** Cả 3 chiến thuật đều truy xuất đúng **tài liệu** cho cả 5 câu hỏi. `RecursiveChunker` cho kết quả chính xác nhất — riêng Q3 bắt đúng chunk "giảm 50% học phí" (0.7819) trong khi `SentenceChunker` của tôi và `FixedSizeChunker` chỉ bắt được chunk "giảm 70%". `SentenceChunker` cũng gộp cả file `thu_tuc_hanh_chinh_mot_cua.md` thành 1 chunk (regex tách câu không nhận biết ranh giới trong file nhiều liên kết), làm điểm Q5 thấp hơn. Kết quả này xác nhận nhận định của nhóm: **`RecursiveChunker` phù hợp nhất với văn bản quy định có cấu trúc phân tầng**, giữ nguyên vẹn một điều khoản quy định.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> So sánh cùng một bộ tài liệu `uet_handbook` qua 3 chiến thuật, tôi nhận ra **ranh giới chunk quyết định chất lượng truy xuất**: SentenceChunker (của tôi) giữ trọn ý câu nhưng lại gộp quá lớn với file nhiều liên kết, khiến câu hỏi cụ thể như "giảm 50% học phí" không tìm thấy chunk chính xác trong top-3. Chiến thuật `RecursiveChunker` của bạn Phạm Đức Thiện chia theo đoạn/mục nên bắt chính xác hơn. Ngoài ra, `search_with_filter` theo `doc_id` giúp loại nhiễu từ các tài liệu khác, đặc biệt hữu ích ở các câu 3, 4, 5 như nhóm đã phân tích.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                  |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5                  |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10                |
| **Tổng phần cá nhân**                      | **60 / 60**      |
