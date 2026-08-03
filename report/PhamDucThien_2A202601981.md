# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Đức Thiện
**Nhóm:** [Tên nhóm]
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> *Viết 1-2 câu: Độ tương tự cosine cao nghĩa là hai đoạn văn bản có sự tương đồng lớn về mặt ngữ nghĩa và hướng ngữ cảnh, bất kể độ dài ngắn của chúng. Điều này thể hiện rằng các vectơ embedding của hai văn bản hướng về gần cùng một phía trong không gian đa chiều.*

**Ví dụ có độ tương tự CAO:**

- Câu A: "Hôm nay thời tiết rất đẹp và nắng nhẹ."
- Câu B: "Thời tiết hôm nay thật đẹp trời lại có nắng dịu."
- Tại sao tương đồng: Cả hai câu đều truyền tải chung một nội dung ngữ cảnh (thời tiết đẹp, có nắng) và sử dụng nhiều từ đồng nghĩa, giúp vectơ embedding của chúng chỉ về cùng một hướng.

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Hôm nay thời tiết rất đẹp và nắng nhẹ."
- Câu B: "Giải thuật quy hoạch động được ứng dụng rộng rãi trong tối ưu hóa."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn độc lập (thời tiết và khoa học máy tính), không có sự liên quan về mặt ngữ nghĩa nên hai vectơ chỉ về các hướng khác biệt.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> *Viết 1-2 câu: Độ tương tự cosine chỉ đo góc giữa hai vectơ nên tập trung hoàn toàn vào nội dung ngữ nghĩa và không bị ảnh hưởng bởi độ dài văn bản. Ngược lại, khoảng cách Euclid đo độ dài tuyệt đối giữa hai điểm, khiến hai văn bản có cùng nội dung nhưng độ dài chênh lệch lớn dễ bị đánh giá sai là không tương đồng.*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> *Trình bày phép tính: số_lượng_chunk = làm_tròn_lên((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))*
> *Đáp án: 23*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> *Viết 1-2 câu: Khi overlap tăng lên 100, số lượng chunk tăng từ 23 lên **25 chunks** (áp dụng công thức: **$\text{làm\_tròn\_lên}((10000 - 100) / (500 - 100)) = \lceil 24.75 \rceil = 25$**). Việc tăng độ chồng chéo giúp bảo toàn ngữ cảnh liền mạch giữa ranh giới các đoạn cắt, tránh tình trạng câu văn hoặc ý nghĩa quan trọng bị đứt gãy khi đưa vào mô hình truy vấn.*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Tôi dùng `re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)` để tách câu — pattern này dùng lookbehind để giữ lại dấu câu cuối mỗi câu và tách tại khoảng trắng hoặc xuống dòng sau chúng. Sau khi tách, các câu được nhóm thành chunks với số lượng tối đa `max_sentences_per_chunk`. Trường hợp ngoại lệ được xử lý: văn bản rỗng trả về `[]`, và văn bản không có dấu câu nào thì trả về nguyên văn bản như một chunk duy nhất.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán thử tách văn bản theo separator ưu tiên nhất (từ `\n\n` xuống dần), gộp các phần vào chunk hiện tại cho đến khi vượt `chunk_size` thì lưu chunk và bắt đầu chunk mới. Nếu một đoạn đơn lẻ vẫn quá lớn, nó được đệ quy với `next_separators`. Base case gồm hai trường hợp: (1) văn bản đã ngắn hơn `chunk_size` → trả về nguyên văn bản; (2) `remaining_separators` rỗng → chia thô theo `chunk_size` từng ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> Mỗi `Document` được nhúng (embed) bằng `_embedding_fn` rồi lưu vào `self._store` dưới dạng dict chứa `{id, content, embedding, metadata}`. Khi tìm kiếm, query cũng được nhúng rồi tính **dot product** với từng embedding đã lưu (tương đương cosine similarity vì mock embedder đã trả về vector đã chuẩn hóa). Các kết quả được sắp xếp giảm dần theo score và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> `search_with_filter` **lọc trước** — duyệt qua `self._store` để giữ lại các records có `metadata` khớp với tất cả các cặp key-value trong `metadata_filter`, sau đó chạy `_search_records` trên danh sách đã lọc. `delete_document` xóa bằng cách xây dựng lại `self._store` với list comprehension, loại bỏ tất cả records có `id == doc_id`, trả về `True` nếu danh sách co lại.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> `answer` theo pattern RAG 3 bước: (1) gọi `store.search(question, top_k)` để lấy các chunks liên quan; (2) xây dựng prompt bằng cách liệt kê từng chunk dưới dạng `[Chunk i]: <nội dung>` rồi nối với câu hỏi; (3) gọi `llm_fn(prompt)` để sinh câu trả lời. Ngữ cảnh được inject trực tiếp vào phần đầu prompt trước câu hỏi, giúp LLM có đủ thông tin để trả lời chính xác.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\project\vin\lab6\DAY07_2A202601981_PhamDucThien
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED

============================== 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                                                        | Câu B                                                                              | Dự đoán | Điểm thực tế          | Đánh giá | Đúng?      |
| ---- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ---------- | ------------------------- | ----------- | ------------ |
| 1    | "Học phí học kỳ này cần nộp trước ngày 15 tháng 9."                | "Sinh viên phải đóng tiền học trước ngày 15/9 trong học kỳ."             | cao        | **0.8237 → cao**   | cao         | **✓** |
| 2    | "Sinh viên đăng ký môn học trực tuyến qua cổng thông tin."          | "Hệ thống cho phép chọn môn học trên website của trường."                 | cao        | **0.5734 → cao**   | cao         | **✓** |
| 3    | "Thư viện mở cửa từ 7 giờ sáng đến 10 giờ tối."                    | "Thuật toán gradient descent dùng để tối ưu mô hình machine learning."     | thấp      | **0.1710 → thấp** | thấp       | **✓** |
| 4    | "Học bổng khuyến khích học tập dành cho sinh viên có GPA trên 3.5." | "Sinh viên xuất sắc với điểm trung bình trên 3.5 được nhận học bổng." | cao        | **0.6812 → cao**   | cao         | **✓** |
| 5    | "Ký túc xá nhà trường cho phép sinh viên đăng ký ở nội trú."    | "Sinh viên cần mang chứng minh nhân dân để đăng ký thẻ thư viện."      | thấp      | **0.5487 → cao**   | cao         | **✗** |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> **So sánh & Phân tích:** Khi sử dụng mô hình thực **OpenAI Embedding 3 Small (`text-embedding-3-small`)**, điểm cosine đạt đến **0.8237 (Cặp 1)** và **0.6812 (Cặp 4)** cho các câu có nội dung đồng nghĩa. Điều này khẳng định OpenAI Embeddings phản ánh chính xác mối quan hệ ngữ nghĩa trong không gian vector đa chiều (1536 chiều).
> Điểm bất ngờ thú vị ở **Cặp 5** với OpenAI: hai câu cùng về dịch vụ sinh viên trường học (KTX và Thẻ thư viện) có điểm tương đồng là **0.5487** (mức khá), thể hiện khả năng nhận diện các thực thể mang cùng ngữ cảnh trường học của mô hình AI thế hệ 3.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi** trên bộ dữ liệu thực `uet_handbook` (học phí, học bổng, KTX, BHYT, thủ tục một cửa) sử dụng `EmbeddingStore` + `KnowledgeBaseAgent` kết hợp mô hình **`OpenAI text-embedding-3-small`** (OpenAI 3 Mini).

| # | Câu hỏi (Query)                                                                            | Top-1 Chunk truy xuất được (tóm tắt)                                                         | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                                                  |
| - | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------ | --------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1 | Điều kiện để sinh viên được xét cấp học bổng khuyến khích học tập là gì?  | Chunk 1 (`hoc_bong_diem_ren_luyen`) — Quy định tiêu chuẩn & định mức học bổng KKHT     | 0.6758       | **✓ Có liên quan**       | Trích xuất đúng điều kiện đào tạo chuẩn, GPA khá trở lên và tích lũy >= 15 tín chỉ  |
| 2 | Quy định về mức đóng học phí và hạn nộp học phí của sinh viên như thế nào? | Chunk 3 (`hoc_phi_che_do_chinh_sach`) — Mức thu học phí hệ chuẩn và hệ CLC               | 0.6059       | **✓ Có liên quan**       | Trả về đúng quy định đóng học phí theo tín chỉ/niên chế và thời hạn quy định        |
| 3 | Hướng dẫn khám chữa bệnh ban đầu và BHYT cho sinh viên ở đâu?                   | Chunk 7 (`kham_chua_benh`) — Quy định khám sức khỏe nhập học & thanh toán BHYT          | 0.6340       | **✓ Có liên quan**       | Hướng dẫn thủ tục BHYT và khám chữa bệnh ban đầu tại cơ sở y tế theo quy định         |
| 4 | Thông tin đăng ký ở nội trú Ký túc xá cho sinh viên như thế nào?               | Chunk 5 (`ky_tuc_xa`) — Hướng dẫn đăng ký chỗ ở KTX và đường link dịch vụ         | 0.5623       | **✓ Có liên quan**       | Trả về chính xác thông tin đăng ký KTX và đường dẫn hỗ trợ sinh viên`css.vnu.edu.vn` |
| 5 | Cách nộp hồ sơ xin xác nhận sinh viên qua Cổng thông tin một cửa trực tuyến?    | Chunk 13 (`thu_tuc_hanh_chinh_mot_cua`) — Cổng thông tin 1 cửa giải quyết thủ tục online | 0.6772       | **✓ Có liên quan**       | Trả về đúng hướng dẫn nộp hồ sơ và xin giấy xác nhận trực tuyến với Phòng CTSV       |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5 (100%)** (Khi dùng `OpenAI text-embedding-3-small`)

> **Phân tích:** Khi sử dụng mô hình **OpenAI Embedding 3 Small (`text-embedding-3-small`)**, tỉ lệ truy xuất chính xác đạt tuyệt đối **5/5 (100%)** ngay tại vị trí Top-1 với điểm số tương đồng vượt trội (từ **0.5623** đến **0.6772**). Ngược lại, nếu dùng.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Qua bài lab này, tôi nhận ra sự khác biệt cốt lõi giữa MockEmbedder (hash ngẫu nhiên) và các embedding model thực (học từ ngữ nghĩa): cùng một pipeline RAG nhưng chất lượng truy xuất khác nhau hoàn toàn. Một insight quan trọng khác là việc kết hợp lọc metadata (`search_with_filter`) trước khi tìm kiếm vector giúp thu hẹp không gian tìm kiếm, đặc biệt hữu ích khi corpus lớn và câu hỏi có ngữ cảnh cụ thể (ví dụ: chỉ tìm tài liệu tiếng Việt, hoặc tài liệu về học phí). Chiến lược chunking cũng ảnh hưởng lớn: `RecursiveChunker` giữ ngữ cảnh tốt hơn `FixedSizeChunker` vì tách theo ranh giới tự nhiên của văn bản.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                  |
| Hướng tiếp cận của tôi (My Approach)           | 9 / 10                 |
| Hoàn thiện code (Core Implementation — tests)     | 30 / 30                |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5                  |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10                 |
| **Tổng phần cá nhân**                      | **56 / 60**      |
