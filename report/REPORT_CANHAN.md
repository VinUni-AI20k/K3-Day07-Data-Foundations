# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hà Duy Anh
**Nhóm:** C52
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có cùng *hướng* trong không gian nhiều chiều — tức hai đoạn văn bản mà mô hình mã hoá thành các vector đó biểu đạt nội dung/ý nghĩa gần giống nhau, dù độ dài câu chữ hoặc cách diễn đạt cụ thể có khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần qua cổng VinUniDigi Student Portal."
- Câu B: "Sinh viên sử dụng VinUniDigi Student Portal để đăng ký các môn học."
- Tại sao tương đồng: cùng nói về một hành động (đăng ký học phần) qua cùng một hệ thống (VinUniDigi Student Portal), chỉ khác cách diễn đạt — đo thực tế bằng `compute_similarity()` với `LocalEmbedder` ra **0.867**.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên rút môn sau hạn add/drop sẽ nhận điểm W trên bảng điểm."
- Câu B: "Con mèo đang ngủ trên ghế sofa trong phòng khách."
- Tại sao khác: không cùng chủ đề, không chia sẻ từ vựng hay ý nghĩa nào — đo thực tế ra **-0.109** (gần vuông góc/ngược hướng).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ đo góc giữa hai vector (hướng ngữ nghĩa), không bị ảnh hưởng bởi độ lớn (magnitude) của vector — mà độ lớn của embedding thường lệ thuộc vào độ dài câu/tần suất từ chứ không phản ánh ý nghĩa. Euclidean distance sẽ đánh giá sai hai câu cùng ý nghĩa nhưng độ dài khác nhau là "cách xa nhau", trong khi cosine vẫn nhận ra chúng gần nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính: `số lượng chunk = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> Đáp án: **23 chunks.** (Đã kiểm chứng lại bằng cách chạy `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a"*10000)` — độ dài `list` trả về đúng là 23, khớp công thức.)

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks` (tăng thêm 2, cũng đã kiểm chứng bằng code) — vì bước nhảy giữa hai chunk liên tiếp (`chunk_size - overlap`) giảm từ 450 xuống 400 nên cần nhiều chunk hơn mới phủ hết tài liệu. Overlap lớn hơn giúp giảm rủi ro một ý quan trọng bị cắt đúng vào ranh giới hai chunk (thông tin đó vẫn còn xuất hiện trọn vẹn trong ít nhất một chunk), đổi lại bằng việc lưu trữ và embed nhiều chunk hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex lookbehind `(?<=[.!?])\s+` để tách tại khoảng trắng ngay sau `.`, `!`, hoặc `?` — lookbehind giữ nguyên dấu câu ở cuối phần đứng trước (không bị regex "ăn" mất), nên câu tách ra vẫn còn dấu kết thúc. Sau khi tách, mỗi câu được `.strip()` và câu rỗng bị loại; các câu còn lại được nhóm theo cụm kích thước `max_sentences_per_chunk` rồi ghép bằng một dấu cách. Edge case xử lý riêng: text rỗng trả `[]` ngay từ đầu; nếu regex không khớp gì (không có dấu câu), toàn bộ text vẫn được strip và coi là một "câu" duy nhất.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split(current_text, remaining_separators)` thử tách theo separator đầu tiên trong danh sách ưu tiên (`\n\n` → `\n` → `. ` → `" "` → `""`); nếu separator đó không xuất hiện trong text, đệ quy lại với phần separator còn lại. Khi tách được, các phần liền nhau được gộp vào một buffer cho đến ngay trước khi vượt `chunk_size`, rồi buffer được chốt thành một chunk; phần nào đứng riêng vẫn quá dài thì bị đệ quy tiếp bằng separator ưu tiên thấp hơn. Hai base case: (1) text đã đủ ngắn (`<= chunk_size`) → trả `[text]`; (2) hết separator hoặc separator hiện tại là chuỗi rỗng → cắt cố định theo `chunk_size` (không còn cách nào "thông minh" hơn).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được `_make_record()` chuyển thành một dict `{id, content, metadata, embedding}`: `metadata` được copy (không dùng thẳng object của caller) và luôn có `doc_id` (`setdefault`, không đè lên giá trị mà `ingest.py` đã gắn từ file gốc); `id` ghép `doc.id` với bộ đếm `_next_index` để không trùng khi thêm nhiều lần. `search()` embed câu hỏi **một lần**, tính dot product của vector đó với embedding của từng record (`_search_records`), sort giảm dần theo score và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc theo `metadata_filter` (AND trên mọi cặp key/value, so khớp tuyệt đối) **trước**, rồi mới đưa tập đã lọc vào cùng hàm `_search_records` mà `search()` dùng — nếu rank rồi mới lọc, top-k có thể bị các bản ghi không hợp lệ chiếm hết chỗ dù store vẫn còn tài liệu đúng. `delete_document(doc_id)` giữ lại mọi record mà `metadata["doc_id"] != doc_id`, so sánh kích thước store trước/sau để trả `True`/`False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Gọi `store.search(question, top_k=top_k)` (agent không tự embed gì cả), rồi đánh số từng chunk `[1]`, `[2]`... kèm `(nguồn: doc_id)` để có thể truy vết câu trả lời về đúng chunk/file khi debug. Prompt gồm 4 phần: chỉ dẫn "chỉ dùng context, nói rõ khi thiếu dữ liệu" → `Context:` (các chunk đã đánh số) → `Question:` → nhãn `Answer:`. Nếu `search()` trả về rỗng (store rỗng hoặc không có kết quả), agent trả thông báo cố định ngay, không gọi `llm_fn` vô ích.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
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

> Đo bằng `compute_similarity()` với `LocalEmbedder` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) — mock embedder không dùng ở đây vì nó chỉ là hash ngẫu nhiên, không phản ánh ngữ nghĩa thật.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần qua cổng VinUniDigi Student Portal. | Sinh viên sử dụng VinUniDigi Student Portal để đăng ký các môn học. | cao | 0.867 | Đúng |
| 2 | Full nghĩa là lớp học đã hết chỗ. | Conflict nghĩa là lớp học bị trùng lịch với một lớp khác. | thấp | 0.484 | Đúng (nhưng cao hơn dự đoán) |
| 3 | Sinh viên rút môn sau hạn add/drop sẽ nhận điểm W trên bảng điểm. | Con mèo đang ngủ trên ghế sofa trong phòng khách. | thấp | -0.109 | Đúng |
| 4 | Thư viện cho sinh viên mượn tối đa 5 cuốn sách trong 14 ngày. | Sinh viên được phép mượn không quá 5 đầu sách, thời hạn hai tuần. | cao | 0.654 | Đúng |
| 5 | Thời hạn đăng ký học phần Summer 2026 là từ 29/6 đến 4/7/2026. | Sinh viên cần liên hệ phòng Đào tạo nếu gặp vấn đề khi đăng ký. | thấp | 0.305 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 2 bất ngờ nhất: dự đoán "thấp" vì "Full" và "Conflict" là hai trạng thái khác nhau, nhưng điểm thực tế 0.484 cao hơn hẳn so với các cặp "thấp" khác (cặp 3, 5 chỉ 0.305 và -0.109). Điều này cho thấy embedding bắt được sự tương đồng ở mức *chủ đề/miền* (cả hai câu đều dùng chung khung ngữ pháp "X nghĩa là..." và cùng nói về trạng thái đăng ký lớp học) chứ không phân biệt được nội dung *cụ thể* khác nhau giữa hai trạng thái — đây chính là rủi ro nếu chỉ dựa vào embedding để phân loại chính xác giữa các khái niệm gần nhau trong cùng một miền.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> Cấu hình chạy: `RecursiveChunker(chunk_size=400)` + `LocalEmbedder` (không dùng mock vì mock không phản ánh ngữ nghĩa), corpus `data/vinuni_course_registration` (66 chunk). `llm_fn` dùng `demo_llm` — một hàm giả lập chỉ echo lại 300 ký tự đầu của prompt, **không phải LLM thật**, nên cột "Câu trả lời của Agent" dưới đây là tóm tắt nội dung context mà agent đưa vào prompt, không phải suy luận thực sự.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Portal nào dùng để đăng ký Summer 2026 + checklist hoàn tất? | doc `summer-2026-new-student-portal` — đoạn giới thiệu portal mới VinUniDigi | 0.784 | Có — đúng tài liệu, nhưng top-1 chỉ nêu tên portal, chưa có bước CONFIRM/Registered (nằm ở chunk khác cùng tài liệu) | Trích đúng "VinUniDigi Student Portal" nhưng thiếu chi tiết checklist |
| 2 | Thời gian đăng ký Summer 2026 + hạn add/drop cuối? | doc `summer-2026-registration` — chunk chứa cả ngày công bố lịch và (ở cuối chunk) mốc 29/6–4/7 | 0.836 | Có — đúng tài liệu và chứa đủ mốc thời gian cần | Nêu đúng khung thời gian Summer 2026 trong chunk |
| 3 | Withdrawal ghi nhận thế nào, hạn chót, giới hạn tín chỉ? | doc `spring-2026-important-notes` — "withdrawal... W grade... trước 30% thời gian học" | 0.737 | Một phần — đúng về W grade và mốc 30%, nhưng giới hạn "18 credits" nằm ở chunk khác (`undergraduate-academic-regulations`, xuất hiện ở top-2/3) | Nêu đúng W grade + 30%, thiếu giới hạn 18 tín chỉ trong top-1 |
| 4 | Full/Conflict nghĩa là gì, chưa đủ điều kiện tiên quyết thì sao? | doc `summer-2026-new-student-portal` — "Full means no seats... Conflict means... Prerequisite Requirements..." | 0.754 | Có — khớp đủ cả 4 ý cần (Full/no seats/Conflict/prerequisite) trong đúng 1 chunk | Trả lời đầy đủ cả 3 khái niệm trong một chunk duy nhất |
| 5 | Cách xin retake/audit/individual study + xin rút môn sau add/drop? | doc `undergraduate-academic-regulations` — quy trình petition cần academic advisor/Registrar phê duyệt | 0.779 | Một phần — đúng chủ đề (petition/approval) nhưng SAI tài liệu kỳ vọng (`forms-and-petitions`, có quy trình email cụ thể); vẫn khớp 3/4 evidence ("Registrar", "instructor", "approval") | Nêu đúng cần approval từ Registrar/instructor, nhưng thiếu chi tiết "gửi qua email" |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (3 câu top-1 đã đủ trực tiếp; 2 câu — #3 và #5 — top-1 chỉ đúng một phần nhưng thông tin còn thiếu vẫn xuất hiện trong top-2/top-3)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Điền sau khi nhóm demo/so sánh chiến lược (Bài tập 3.4) — chưa diễn ra tại thời điểm viết báo cáo này.*

---

## Tự Đánh Giá (Phần Cá Nhân)

> Điểm dưới đây là đề xuất dựa trên bằng chứng khách quan (test pass, dữ liệu đo thật); hãy điều chỉnh lại theo đánh giá thật của bạn trước khi nộp.

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |

**Ghi chú tự đánh giá mục Kết quả truy xuất (7/10):** theo `docs/SCORING.md` (2 điểm/câu — top-3 có chunk liên quan **và** agent trả lời đúng), chỉ câu #2 và #4 đạt đủ 2 điểm (top-1 đúng và đủ chi tiết); câu #1, #3, #5 chỉ đạt 1 điểm vì top-1 đúng tài liệu nhưng thiếu chi tiết hoặc lệch tài liệu kỳ vọng. Ngoài ra `llm_fn` dùng trong lần chạy này (`demo_llm`) chỉ là hàm giả lập echo lại prompt, không phải LLM thật, nên "câu trả lời của agent" chưa được kiểm chứng độ chính xác một cách đầy đủ — điểm này nên được xem lại khi có LLM thật.
