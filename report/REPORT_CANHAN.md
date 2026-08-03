# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Xuân Lộc
**Nhóm:** A2
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai đoạn văn bản có độ tương tự cosine cao nghĩa là vector embedding của chúng gần như cùng hướng trong không gian nhiều chiều — tức là chúng mang ý nghĩa ngữ nghĩa tương đồng. Giá trị tiến gần 1.0 cho thấy hai văn bản nói về cùng chủ đề hoặc cùng ý, dù dùng từ ngữ khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần trực tuyến tại cổng giao dịch điện tử UEH."
- Câu B: "Cách thức đăng ký môn học online cho sinh viên UEH."
- Tại sao tương đồng: Cả hai câu đều nói về quy trình đăng ký học phần trực tuyến tại UEH, chỉ khác cách diễn đạt (học phần vs môn học, trực tuyến vs online).

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thư viện UEH mở cửa từ thứ Hai đến thứ Bảy."
- Câu B: "Điều kiện xét học bổng khuyến khích học tập dành cho sinh viên."
- Tại sao khác: Hai câu thuộc chủ đề hoàn toàn khác nhau (thư viện vs học bổng), không chia sẻ ngữ nghĩa nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ đo **hướng** (góc giữa hai vector), không phụ thuộc vào **độ dài** (magnitude) của vector. Điều này quan trọng vì hai văn bản có cùng ý nghĩa nhưng khác độ dài sẽ có embedding khác magnitude — Euclidean distance sẽ cho khoảng cách lớn (sai), trong khi cosine vẫn cho điểm cao (đúng).

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((doc_length - overlap) / (chunk_size - overlap))`
> = `ceil((10000 - 50) / (500 - 50))`
> = `ceil(9950 / 450)`
> = `ceil(22.11)`
> **Đáp án: 23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap=100: `ceil((10000 - 100) / (500 - 100))` = `ceil(9900 / 400)` = `ceil(24.75)` = **25 chunks** — tăng thêm 2 chunk so với overlap=50. Overlap lớn hơn giúp tránh mất thông tin tại ranh giới chunk — nếu một câu quan trọng nằm ở cuối chunk A, nó sẽ được lặp lại ở đầu chunk B, đảm bảo retrieval tìm được chunk có ngữ cảnh đầy đủ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex lookbehind `(?<=[.!?])(?:\s|\n)+` để tách tại vị trí sau dấu kết thúc câu (`.`, `!`, `?`) theo sau bởi khoảng trắng hoặc xuống dòng — giữ dấu câu gắn liền với câu trước. Sau khi tách, gom các câu theo nhóm `max_sentences_per_chunk` bằng slicing `sentences[i:i+n]` rồi join lại bằng khoảng trắng. Edge case: chuỗi rỗng trả về `[]`; `max_sentences_per_chunk` được clamp tối thiểu là 1 bằng `max(1, ...)` để tránh vòng lặp vô hạn.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy thử tách text bằng danh sách separator theo thứ tự ưu tiên (`\n\n` → `\n` → `. ` → ` ` → `""`). **Base case:** text ngắn hơn `chunk_size` → trả về nguyên; hoặc hết separator → trả nguyên (không split vô hạn). Nếu separator hiện tại không tách được (chỉ có 1 phần), thử separator tiếp theo. Sau khi tách, gom (merge) các phần nhỏ liền kề lại nếu tổng vẫn ≤ `chunk_size`, rồi đệ quy xuống separator tiếp cho các phần còn quá lớn. Separator rỗng `""` là fallback cuối cùng — cắt theo ký tự từng `chunk_size` ký tự.

**`compute_similarity`** — hướng tiếp cận:
> Tính cosine similarity = `dot(a,b) / (||a|| * ||b||)`. Dùng hàm `_dot()` nội bộ để tính dot product và magnitude (`sqrt(dot(v,v))`). Xử lý edge case chia cho 0: nếu `mag_a == 0.0` hoặc `mag_b == 0.0` thì trả về `0.0` thay vì raise ZeroDivisionError — vector zero không có hướng nên similarity = 0 là hợp lý.

**`HeadingChunker` (custom chunker cho K3)** — hướng tiếp cận:
> Thiết kế riêng cho tài liệu quy định học vụ UEH. Dùng regex lookahead `^(?=#{1,4}\s|Chương\s+[IVXLCDM\d]|Điều\s+\d+\.)` để phát hiện ranh giới heading mà không tiêu thụ ký tự. Tách text tại các vị trí heading, tạo cặp `(heading_line, body)` cho mỗi section. Gắn parent heading context: duy trì dict `parent_headings[level]` — khi gặp heading level N, xoá tất cả entry level > N. Section quá dài (> `max_chunk_size`) được split tiếp theo paragraph (`\n\n+`). Ưu điểm so với built-in: mỗi chunk là 1 Điều/Chương hoàn chỉnh, kết quả retrieval tự giải thích nhờ heading context.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents`: với mỗi document, gọi `_make_record()` để tạo dict chứa `id`, `content`, `metadata`, và `embedding` (gọi `embedding_fn(content)`), rồi append vào `self._store` (in-memory list). Nếu ChromaDB khả dụng, cũng add song song vào collection. Dùng `self._next_index` auto-increment để tạo unique ID cho Chroma. `search`: embed câu query, rồi tính dot product giữa query embedding và mọi record trong store, sort giảm dần và lấy `top_k` kết quả — trả về list dict có `content`, `score`, `metadata`, `id`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter`: lọc **trước** (pre-filter) — duyệt `self._store`, giữ lại record mà `metadata[k] == v` cho mọi cặp `(k,v)` trong `metadata_filter`, rồi chạy `_search_records` trên tập đã lọc. Lọc trước thay vì lọc sau vì tiết kiệm tính toán similarity trên record không cần thiết. `delete_document`: lọc bỏ record có `id == doc_id` hoặc `metadata["doc_id"] == doc_id` (bắt cả chunk có doc_id gốc từ ingest pipeline), trả về `True` nếu kích thước store giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Gọi `store.search(question, top_k)` lấy top-k chunk liên quan, rồi xây dựng context bằng cách ghép nội dung chunk đánh số `[1] content_1`, `[2] content_2`… Tạo prompt theo mẫu RAG: `"Based on the following context, answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"` rồi gọi `self.llm_fn(prompt)` trả về kết quả. Thiết kế intent: đánh số chunk giúp LLM trích dẫn nguồn; đặt context trước question để LLM đọc bối cảnh trước khi thấy câu hỏi (quen thuộc với instruction-following). Cấu trúc tách biệt retrieve → prompt → generate dễ debug từng bước.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0

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

============================= 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> **Lưu ý:** Sử dụng mock embedder (`_mock_embed`) vì chưa cài `EMBEDDING_PROVIDER=local`. Mock embedder dùng hash-based random projection — điểm **không phản ánh ngữ nghĩa**, chỉ phục vụ unit test. Dự đoán bên dưới dựa trên hiểu biết ngữ nghĩa của tôi; phần "Đúng?" đánh giá dự đoán ngữ nghĩa chứ không so với mock.

| Cặp | Câu A | Câu B | Dự đoán (ngữ nghĩa) | Điểm mock | Dự đoán đúng về ngữ nghĩa? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần ở đâu? | Cách thức đăng ký môn học tại UEH? | cao (~0.85) | 0.0976 (mock, không phản ánh) | ✅ Đúng — cùng chủ đề đăng ký môn, chỉ khác cách diễn đạt |
| 2 | Học bổng khuyến khích học tập là gì? | Ký túc xá UEH có bao nhiêu phòng? | thấp (~0.15) | 0.0429 | ✅ Đúng — hai chủ đề hoàn toàn khác (học bổng vs ký túc xá) |
| 3 | Học phí năm 2026 là bao nhiêu? | Mức học phí các hệ đào tạo năm học 2026-2027 | cao (~0.90) | -0.0349 (mock, không phản ánh) | ✅ Đúng — cùng hỏi về học phí cùng năm, chỉ khác mức độ cụ thể |
| 4 | Thư viện UEH mở cửa mấy giờ? | Điều kiện xét học bổng khuyến khích học tập | thấp (~0.10) | -0.1325 | ✅ Đúng — thư viện vs học bổng, không chia sẻ ngữ nghĩa |
| 5 | Thẻ sinh viên mất phí bao nhiêu? | Phí làm thẻ sinh viên là 100.000 đồng | cao (~0.88) | -0.1125 (mock, không phản ánh) | ✅ Đúng — câu hỏi và câu trả lời cùng chủ đề chi phí thẻ SV |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> **Bất ngờ nhất:** Cặp #3 và #5 — mock cho điểm **âm** dù hai câu rõ ràng cùng chủ đề. Điều này chứng minh mock embedder dùng random projection **hoàn toàn không encode ngữ nghĩa** — nó chỉ tạo vector 64 chiều từ hash, không qua neural network nào.
>
> **Bài học về embedding:** Embeddings thật (sentence-transformers, OpenAI) hoạt động vì chúng được huấn luyện trên hàng triệu cặp câu — model học được rằng "đăng ký học phần" ≈ "đăng ký môn học" dù từ khác nhau. Cosine similarity phản ánh **ý nghĩa**, không phải **trùng từ** (khác BM25/TF-IDF). Hệ quả: khi chọn embedding model cho RAG tiếng Việt, cần model đã fine-tune trên dữ liệu tiếng Việt (ví dụ `bkai-foundation-models/vietnamese-bi-encoder`) — dùng model tiếng Anh thuần sẽ giảm chất lượng retrieval đáng kể.
>
> **So sánh embedder thật vs mock:** Với local embedder, tôi kỳ vọng cặp #1, #3, #5 sẽ có điểm > 0.80 và cặp #2, #4 < 0.20. Mock cho tất cả xấp xỉ 0 (±0.15) — vô nghĩa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** với `HeadingChunker(max_chunk_size=1500, include_parents=True)` — lệnh: `python scripts/bench.py --chunker heading`.

### Kết quả benchmark (mock embedder)

| # | Câu hỏi (Query) | Top-1 Chunk (tóm tắt) | Score | Relevant? | Agent answer |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | SV có được đăng ký mã HP đang chờ lịch thi? | HB Song ngành (scholarship-policy-overview) | 0.1562 | ❌ Sai doc | Không trả lời được |
| 2 | SV không nộp HP đúng hạn HK cuối 2025? | Điều kiện xét HB (scholarship-regulation) | 0.3042 | ❌ Sai doc | Không trả lời được |
| 3 | Các bước đăng ký thẻ SV nhựa? | Bước 5: nhận email…A203 (student-card-services) | 0.3384 | ✅ **Top-1 đúng** | Đúng quy trình 5 bước |
| 4 | UEH Smart Library có CSDL quốc tế nào? | Điều 7 Phòng CTCT (academic-advising) | 0.2328 | ❌ Sai doc | Không trả lời được |
| 5 | Thời gian nộp phí KTX Quý III? (filter `document_version=2026-q3`) | Thông báo KTX Q3/2026 | 0.0230 | ✅ **Top-1 đúng** | Đúng: 01/7–13/7/2026 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 2 / 5

### Phân tích lỗi (Failure Analysis)

**Tại sao chỉ đạt 2/5 với mock embedder?**
> Mock embedder tạo vector từ hash value — **hoàn toàn ngẫu nhiên**, không encode ngữ nghĩa. Kết quả 2/5 gần đúng xác suất ngẫu nhiên (mỗi doc có khoảng 5–6 chunk trong 63 chunk tổng, xác suất top-3 chứa đúng doc ≈ 3×6/63 ≈ 29%). Hai câu đúng (#3, #5) là **may mắn thống kê** và do metadata filter (#5 thu hẹp search space xuống chỉ 1 doc).

**Câu #1 — Failure:** Câu hỏi về "đăng ký mã học phần đang chờ lịch thi" nằm trong chunk về quy trình đăng ký HK cuối 2025. HeadingChunker tách doc này thành nhiều section, nhưng mock embedder không thể match "chờ lịch thi" → section chứa thông tin này. Với local embedder, kỳ vọng câu này sẽ truy xuất đúng vì semantic match "đăng ký học phần" ↔ content chunk.

**Câu #2 — Failure:** Tương tự — "nộp học phí đúng hạn" cần semantic understanding để match với section quy định về hệ quả trễ hạn. Mock chọn sai doc (scholarship-regulation thay vì course-registration-plan).

**Câu #4 — Failure:** "Smart Library" + "cơ sở dữ liệu quốc tế" nằm trong `ueh-library-reading-culture` — tài liệu này không có heading Chương/Điều nên HeadingChunker tạo chunk lớn (toàn bộ body). Mock không distinguish được chunk này với chunk khác. Đây là **điểm yếu thiết kế** của HeadingChunker: tài liệu không có heading bị gom thành 1 chunk lớn, khó match.

**Câu #3 — Success:** Tài liệu thẻ sinh viên ngắn (1,558 chars), HeadingChunker giữ gần như nguyên → nội dung quy trình 5 bước nằm trọn trong chunk. Dù mock, chunk nhỏ + nội dung chuyên biệt giúp score cao hơn tương đối.

**Câu #5 — Success nhờ metadata filter:** Filter `document_version=2026-q3` thu hẹp search space từ 63 chunk xuống còn ~2 chunk (chỉ doc `ueh-dorm-fee-2026-q3`). Khi search space nhỏ, ngay cả mock cũng trả kết quả đúng → chứng minh giá trị của metadata filtering.

### Đề xuất cải thiện

1. **Sử dụng local embedder** (`EMBEDDING_PROVIDER=local` với `bkai-foundation-models/vietnamese-bi-encoder`) — kỳ vọng nâng từ 2/5 lên 4–5/5 vì model hiểu ngữ nghĩa tiếng Việt.
2. **Hybrid chunking**: kết hợp HeadingChunker cho doc có cấu trúc (quy định, sổ tay) với RecursiveChunker cho doc dạng bài viết (thư viện, học bổng tổng quan) — tự động detect dựa trên số lượng heading trong document.
3. **Thêm metadata filter** cho câu #1–2: filter `category=course-registration` sẽ loại bỏ chunk học bổng/thư viện khỏi search space, tương tự hiệu quả của câu #5.

### So sánh HeadingChunker vs các chiến lược khác (trên mock)

| Chiến lược | Số chunk | top-3 hit | top-1 hit | Nhận xét |
|---|---|---|---|---|
| HeadingChunker | 63 | 2/5 | 2/5 | Ít chunk nhất → ít nhiễu; đúng #3 (doc nhỏ) và #5 (filter) |
| RecursiveChunker | 135 | 2/5 | 1/5 | Nhiều chunk hơn gấp đôi; mock random nên kết quả tương đương |
| FixedSizeChunker | 118 | 2/5 | 2/5 | Kết quả tương đương trên mock |

> **Kết luận:** Trên mock embedder, tất cả chunker cho kết quả tương đương (~2/5) vì retrieval là ngẫu nhiên. Sự khác biệt thực sự chỉ thể hiện khi dùng embedding model thật — lúc đó HeadingChunker kỳ vọng vượt trội trên tài liệu quy định nhờ chunk coherence (mỗi chunk = 1 Điều hoàn chỉnh) và heading context (parent headings giúp disambiguate).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> So sánh SentenceChunker (thành viên 1) với HeadingChunker cho thấy: SentenceChunker giữ câu trọn vẹn tốt hơn cho câu hỏi dạng "SV bị xử lý thế nào nếu…" (vì câu điều kiện + hậu quả nằm gọn trong 1 chunk), trong khi HeadingChunker phù hợp hơn cho câu hỏi "Điều X quy định gì?" vì mỗi chunk map 1:1 với 1 Điều. Bài học: **không có chunker tốt nhất cho mọi loại câu hỏi** — chiến lược nên phụ thuộc vào cấu trúc tài liệu và kiểu câu hỏi kỳ vọng.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
