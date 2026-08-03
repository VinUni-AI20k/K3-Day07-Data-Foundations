# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Đào Ngọc Bích]
**Nhóm:** [Tên nhóm]
**Ngày:** [3/8/2026]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Cosine similarity đo góc giữa hai vector embedding chứ không đo độ dài của chúng. Điểm cao (gần 1) nghĩa là hai vector gần như cùng hướng trong không gian embedding — tức hai đoạn văn bản mang ý nghĩa/ngữ cảnh gần giống nhau theo cách mô hình biểu diễn, dù cách diễn đạt (từ ngữ, độ dài câu) có thể khác nhau hoàn toàn.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên phải đăng ký học phần đúng thời hạn quy định."
- Câu B: "Việc đăng ký môn học cần hoàn tất trong thời gian được thông báo."
- Tại sao tương đồng: hai câu diễn đạt khác từ (đăng ký học phần / đăng ký môn học, thời hạn quy định / thời gian được thông báo) nhưng cùng một ý: sinh viên phải đăng ký đúng hạn.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Ký túc xá UEH có hai tòa nhà dành cho sinh viên nội trú."
- Câu B: "Cosine similarity đo góc giữa hai vector embedding."
- Tại sao khác: một câu nói về cơ sở vật chất ký túc xá, câu còn lại nói về khái niệm toán học trong NLP — hai chủ đề không liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Euclidean distance bị ảnh hưởng bởi độ lớn (norm) của vector, mà độ lớn embedding có thể lệch theo độ dài câu hoặc cách mô hình mã hoá, không phản ánh ngữ nghĩa. Cosine similarity chỉ quan tâm hướng của vector nên bất biến với độ lớn — hai câu diễn đạt cùng ý nhưng độ dài khác nhau vẫn được nhận diện là giống nhau, phù hợp hơn cho so sánh ngữ nghĩa text.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`.
> Đáp án: **23 chunk**. Đã verify bằng code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a" * 10000)` → `len(...) == 23`.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Overlap tăng lên 100 → `ceil((10000-100)/(500-100)) = ceil(9900/400) = 25` chunk (verify bằng code: 25, tăng thêm 2 chunk so với overlap=50). Tăng overlap làm số chunk tăng (mỗi bước trượt ngắn hơn nên cần nhiều bước hơn để phủ hết văn bản), đổi lại mỗi ranh giới chunk chia sẻ nhiều ngữ cảnh chung hơn — giảm rủi ro một câu/ý bị cắt đứt đúng ngay điểm nối giữa hai chunk, giúp retrieval ở gần biên chunk chính xác hơn, đánh đổi là tốn thêm chi phí embedding (nhiều chunk hơn) và dữ liệu trùng lặp giữa các chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split(r'(?<=[.!?])\s+', text.strip())` — lookbehind giữ dấu câu (`.`, `!`, `?`) ở cuối phần đứng trước, tách tại khoảng trắng theo sau (bao gồm cả `\n` vì `\s` đã bao trùm trường hợp `.\n`). Sau khi tách, `strip()` từng câu và loại bỏ chuỗi rỗng, rồi gom theo từng nhóm `max_sentences_per_chunk` câu bằng `" ".join(...)`. Edge case xử lý: text rỗng trả `[]` ngay từ đầu; `max_sentences_per_chunk` được `max(1, ...)` ở `__init__` để tránh group size 0.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk()` chỉ lo edge case text rỗng rồi gọi `_split(text, self.separators)`. `_split` là đệ quy với 2 base case: (1) `len(current_text) <= chunk_size` → trả `[current_text]` — đây là điều kiện dừng chính; (2) hết separator hoặc separator hiện tại là `""` → cắt cứng theo `chunk_size` bằng slicing. Nếu còn separator, `split()` theo separator đó rồi gộp các phần liền nhau bằng `current + separator + part` miễn còn `<= chunk_size`; phần nào một mình đã dài hơn `chunk_size` thì đệ quy tiếp với `_split(part, next_separators)` (danh sách separator ngắn dần đảm bảo tiến tới base case, không lặp vô hạn).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuyển thành 1 record `{id, content, embedding, metadata}` qua `_make_record` (metadata tự `setdefault("doc_id", doc.id)` nếu thiếu, để `delete_document` luôn hoạt động được kể cả khi không đi qua `ingest.py`). In-memory thì append vào `self._store`; nếu có ChromaDB thì gọi `collection.add(...)`. `search` nhúng câu hỏi rồi tính **dot product** giữa embedding câu hỏi và embedding từng record (`_dot`, có sẵn trong `chunking.py`) — vì mock/local embedder đều trả vector đã chuẩn hoá (unit norm) nên dot product ở đây tương đương cosine similarity — sắp xếp giảm dần rồi cắt `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc **trước**: lấy toàn bộ record (`_all_records()`), giữ lại những record có `metadata[key] == value` cho mọi cặp trong `metadata_filter`, sau đó mới chạy `_search_records` (cùng logic dot-product) trên tập đã lọc — nên `top_k` áp dụng trên phần đã thu hẹp, không phải toàn bộ store. `delete_document` so khớp `metadata["doc_id"] == doc_id` và loại bỏ toàn bộ record khớp khỏi `self._store` (hoặc gọi `collection.delete(ids=...)` với ChromaDB), trả `True`/`False` tuỳ có xoá được gì không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer()` gọi `store.search(question, top_k=top_k)` để lấy các chunk liên quan nhất, ghép chúng thành khối `Context` có đánh số `[1]`, `[2]`, ... rồi nhét vào một prompt template yêu cầu LLM chỉ trả lời dựa trên context đó (và nói rõ nếu context không đủ thông tin), cuối cùng gọi `self.llm_fn(prompt)` để sinh câu trả lời. Đây đúng pattern RAG 3 bước: retrieve → augment prompt → generate.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v
============================= test session starts ==============================
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

============================== 42 passed in 0.03s ===============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy bằng `_mock_embed` (chưa cài `sentence-transformers` nên chưa thử `EMBEDDING_PROVIDER=local`; xem ghi chú bên dưới bảng).

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Sinh viên phải đăng ký học phần đúng thời hạn quy định." | "Việc đăng ký môn học cần hoàn tất trong thời gian được thông báo." | cao (paraphrase) | -0.064 | Sai |
| 2 | "Học bổng khuyến khích học tập dựa trên điểm trung bình tích lũy và kết quả rèn luyện." | "Mức học bổng được xét theo điểm số tích lũy và đánh giá rèn luyện của sinh viên." | cao (paraphrase) | -0.074 | Sai |
| 3 | "Ký túc xá UEH có hai tòa nhà dành cho sinh viên nội trú." | "Cosine similarity đo góc giữa hai vector embedding." | thấp (khác chủ đề) | 0.232 (cao nhất trong 5 cặp) | Sai |
| 4 | "Học phí học kỳ cuối năm 2026 được thông báo theo quyết định số 803." | "Sinh viên có thể vay vốn tín dụng học tập để đóng học phí." | trung bình (cùng chủ đề học phí, khác nội dung cụ thể) | 0.141 | Đúng (tương đối) |
| 5 | "Sinh viên hoàn thành đầy đủ nghĩa vụ học phí sẽ được giữ nguyên trong danh sách lớp." | "Sinh viên không đóng học phí đúng hạn sẽ bị xóa tên khỏi lớp đã đăng ký." | thấp (gần như trái nghĩa hành động) | -0.105 (thấp nhất) | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 3: hai câu hoàn toàn không liên quan (ký túc xá vs. định nghĩa cosine similarity) lại có điểm **cao nhất** trong cả 5 cặp, cao hơn cả hai cặp paraphrase thật sự (cặp 1, 2) — vốn phải là cặp có điểm cao nhất nếu embedding phản ánh đúng ngữ nghĩa. Điều này cho thấy `MockEmbedder` chỉ sinh vector giả lập từ hash MD5 của chuỗi ký tự (xem `src/embeddings.py`), hoàn toàn không mã hoá ý nghĩa — nên điểm số của nó gần như ngẫu nhiên và không thể dùng để kết luận gì về chất lượng ngữ nghĩa. Đây đúng là điều README đã cảnh báo trước; muốn có kết quả phản ánh thật cần chạy lại bằng `EMBEDDING_PROVIDER=local` (dự kiến làm ở Giai đoạn 2 khi so sánh chiến lược retrieval).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** (bộ query chính thức trong `scripts/bench.py`) trên mã nguồn cá nhân, chiến lược `FixedSizeChunker(chunk_size=500, overlap=50)`, corpus `data/ueh_university/` (10 tài liệu, 118 chunk). Lệnh chạy thật:

```
EMBEDDING_PROVIDER=local python scripts/bench.py --chunker fixed_size --top-k 3
```

> Lưu ý: `demo_llm` trong `bench.py` chỉ là stub echo lại preview của prompt (không phải LLM thật sinh câu trả lời tự do) — cột "Agent" dưới đây phản ánh **nội dung có sẵn trong context được truyền cho LLM**, không phải văn phong một câu trả lời hoàn chỉnh.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên có được đăng ký mã học phần đang chờ lịch thi...? | "...Sinh viên không được phép đăng ký mã học phần đang chờ lịch thi hoặc chờ kết quả điểm thi..." (`ueh-course-registration-plan-hk-cuoi-2025`) | 0.7587 | Có — đúng doc & đúng câu ở top-1 | Context chứa đúng câu trả lời chuẩn nguyên văn |
| 2 | Sinh viên không nộp học phí đúng hạn HK cuối 2025 sẽ bị xử lý thế nào? | Top-1 lại là `ueh-tuition-fee-2026-2027` (SAI doc, score 0.7691) — doc đúng `ueh-course-registration-plan-hk-cuoi-2025` chỉ xếp Top-2 (0.7432) và Top-3 (0.7234) | 0.7691 (top-1, sai doc) | Có, nhưng không ở top-1 — đã lọt top-3 ở rank 2 | Context top-3 vẫn có đúng đoạn (rank 2), nhưng đoạn xóa tên khỏi lớp cụ thể nằm ở phần khác của cùng doc chưa chắc lọt |
| 3 | Các bước đăng ký cấp thẻ sinh viên nhựa tại UEH là gì? | Đúng doc `ueh-student-card-services` ở cả Top-1/2/3, nhưng nội dung "Bước 3: 100,000đ...Bước 5: A203" nằm cuối tài liệu — không thấy rõ trong 3 chunk đầu (`chunk_size=500` cắt tài liệu 1.558 ký tự thành ~4 chunk, top_k=3 có thể bỏ sót chunk cuối) | 0.7825 | Có, nhưng thiếu chi tiết — đúng doc, nghi ngờ thiếu chunk chứa bước cuối | Context có thể thiếu "Bước 5" nếu chunk 4 bị top_k=3 loại |
| 4 | UEH Smart Library cung cấp quyền truy cập CSDL học thuật quốc tế nào? | "...UEH Smart Library còn cung cấp quyền truy cập ScienceDirect, SpringerLink..." (`ueh-library-reading-culture`) | 0.8743 | Có — đúng doc & đúng câu ở top-1 | Context chứa đúng danh sách CSDL |
| 5 | Thời gian thanh toán nội trú phí KTX Quý III (7,8,9) là khi nào? (filter `document_version=2026-q3`) | "...Thông báo về việc thu nội trú phí Ký túc xá Quý III/2026..." (`ueh-dorm-fee-2026-q3`, đúng năm nhờ filter) | 0.7307 | Có — đúng doc, đúng năm nhờ metadata filter | Context chứa đúng mốc thời gian 01/7/2026–13/7/2026 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (đúng `expected_doc_id` trong top-3: 5/5; đúng ở top-1: 4/5 — câu #2 là failure case, xem phân tích bên dưới).

**Nhận xét (failure case thật, không phải giả định):** Câu #2 là ví dụ rõ nhất về giới hạn của `FixedSizeChunker` + dot-product ranking thuần: `ueh-tuition-fee-2026-2027` (một tài liệu nói về học phí nói chung) xếp hạng cao hơn tài liệu đúng vì cả hai đều chứa nhiều từ khóa "học phí". Cắt cứng theo 500 ký tự không giữ được liên kết ngữ nghĩa giữa điều kiện ("không nộp học phí đúng hạn") và hậu quả ("xóa tên khỏi danh sách lớp") nếu chúng nằm cách xa nhau trong văn bản gốc — đây là đúng loại lỗi mà `RecursiveChunker`/`HeadingChunker` (tách theo đoạn/heading tự nhiên) khắc phục tốt hơn, đã verify: `recursive` xếp đúng doc ở Top-1 (0.8030) cho chính câu hỏi này.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết sau buổi so sánh trong nhóm — phần thuyết trình/demo giữa các nhóm chưa diễn ra tại thời điểm nộp báo cáo này.*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 (5/5 top-3, 4/5 top-1; câu #2 mất điểm vì đúng doc không ở top-1) |
| **Tổng phần cá nhân** | **58 / 60** |
