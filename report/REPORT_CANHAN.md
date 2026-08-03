# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Văn Hiếu
**Nhóm:** VinBrothers
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai đoạn văn bản có vector embedding trỏ gần cùng một hướng trong không gian nhiều chiều — mô hình "nghĩ" chúng nói về cùng một ý, dù dùng từ ngữ khác nhau. Cosine cao không có nghĩa hai câu giống hệt nhau về mặt chữ, mà giống nhau về mặt *nghĩa*.

**Ví dụ có độ tương tự CAO** (đo bằng `LocalEmbedder` thật, không phải mock):
- Câu A: "Sinh viên có thể nộp học phí trực tuyến qua ngân hàng liên kết với trường."
- Câu B: "Người học được phép thanh toán tiền học bằng hình thức online qua các ngân hàng đối tác của IUH."
- Điểm thực đo: **0.850**
- Tại sao tương đồng: hai câu diễn đạt khác từ vựng ("nộp học phí" vs "thanh toán tiền học", "trực tuyến" vs "online") nhưng cùng một sự kiện — sinh viên trả học phí qua ngân hàng đối tác.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên có thể nộp học phí trực tuyến qua ngân hàng liên kết với trường."
- Câu B: "Thư viện trường mở cửa phục vụ bạn đọc từ 7 giờ sáng đến 21 giờ các ngày trong tuần."
- Điểm thực đo: **0.275**
- Tại sao khác: hai chủ đề hoàn toàn khác nhau (tài chính vs giờ giấc thư viện), không chia sẻ khái niệm nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ đo *góc/hướng* của vector, bỏ qua độ dài (magnitude); còn Euclid đo khoảng cách tuyệt đối nên bị ảnh hưởng bởi độ dài vector — mà độ dài embedding có thể thay đổi theo độ dài câu hoặc tần suất từ mà không hề đổi ý nghĩa. Hai câu đồng nghĩa nhưng một câu dài/lặp từ hơn vẫn nên có similarity cao — cosine đảm bảo điều đó, Euclid thì không.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Công thức: `ceil((length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> Đáp án: **23 chunks** — đã xác minh lại bằng code: `len(FixedSizeChunker(500, 50).chunk('a'*10000)) == 23`.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks` — xác minh bằng code cho đúng **25**. Overlap tăng → bước trượt (`chunk_size - overlap`) nhỏ lại → cần nhiều chunk hơn để phủ hết văn bản. Muốn overlap lớn hơn vì nó giữ ngữ cảnh nối giữa hai chunk liền kề — nếu câu trả lời nằm vắt qua ranh giới cắt (ví dụ nửa đầu ở chunk 3, nửa sau ở chunk 4), overlap giúp cả hai chunk vẫn chứa đủ câu trọn vẹn để truy xuất đúng; đánh đổi là tốn thêm chunk → tốn thêm embedding + dung lượng lưu trữ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split(r"(?<=[.!?])\s+", text.strip())` — lookbehind sau `.`/`!`/`?` để tách câu mà vẫn giữ dấu câu ở cuối phần đứng trước, và `\s+` khớp mọi khoảng trắng (kể cả `\n`) nên bao luôn trường hợp `.\n`. Sau khi strip + bỏ chuỗi rỗng, gom câu theo từng nhóm `max_sentences_per_chunk` rồi join bằng `" "`. Edge case xử lý: text rỗng trả `[]` ngay từ đầu; nếu regex tách ra toàn chuỗi rỗng (ví dụ text chỉ có khoảng trắng) thì cũng trả `[]`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Đệ quy theo danh sách separator ưu tiên (`\n\n → \n → ". " → " " → ""`). Base case 1: đoạn hiện tại đã ngắn hơn `chunk_size` thì trả nguyên văn. Base case 2: hết separator hoặc separator rỗng thì cắt cứng theo `chunk_size`. Ở nhánh đệ quy: `split()` theo separator hiện tại, gom các phần vào `buffer` cho tới khi thêm phần tiếp theo sẽ vượt `chunk_size` thì flush buffer, còn phần nào tự nó đã dài hơn `chunk_size` thì gọi đệ quy `_split(part, rest)` với danh sách separator còn lại (rest ngắn dần) để đảm bảo luôn tiến về base case.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được `_make_record()` chuẩn hoá thành 1 dict `{id, content, metadata, embedding}`, id ghép `doc.id::self._next_index` để không bao giờ trùng dù `add_documents` được gọi nhiều lần với cùng `Document.id`. `metadata["doc_id"]` luôn được đảm bảo có (mặc định = `doc.id` nếu chưa gắn sẵn) — đây là khoá dùng cho filter/xoá về sau. `search()` embed query đúng **một lần**, rồi tính dot product giữa query embedding và embedding từng record (`_dot` trong `chunking.py`) — dùng dot product thay vì tính lại cosine vì cả `MockEmbedder` lẫn `LocalEmbedder` đều trả vector đã chuẩn hoá đơn vị nên dot product ≈ cosine. Kết quả sort giảm dần theo score rồi cắt `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc **trước**, rank **sau**: duyệt `self._store`, chỉ giữ record mà `all(metadata.get(k) == v for k, v in metadata_filter.items())`, rồi mới đưa tập đã lọc vào `_search_records` (dùng chung hàm với `search()` nên `metadata_filter=None` cho kết quả giống hệt `search()`). Làm ngược lại — lấy top-k rồi mới lọc — có thể trả về ít hơn `top_k` kết quả dù store còn nhiều tài liệu hợp lệ chưa lọt top-k ban đầu. `delete_document(doc_id)` so sánh độ dài `self._store` trước/sau khi lọc bỏ mọi record có `metadata["doc_id"] == doc_id`, trả `True`/`False` tương ứng.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer()` gọi `store.search(question, top_k)`, có 2 guard sớm: store rỗng hoặc không có kết quả nào thì trả thông báo cố định, **không gọi `llm_fn`** vô ích. Ngược lại, ghép các chunk lấy được thành context đánh số `[1] (source: doc_id) ...`, `[2] ...` — kèm `metadata["doc_id"]` để câu trả lời truy vết được về đúng file gốc (tiêu chí grounding trong `docs/EVALUATION.md`). Prompt gồm 1 dòng hướng dẫn "chỉ dùng context, nói rõ khi thiếu", khối `Context:`, `Question:` và nhãn `Answer:` để LLM biết điểm bắt đầu sinh câu trả lời. Cuối cùng `return self.llm_fn(prompt)` — agent không tự gọi API, chỉ lắp ráp prompt và giao cho hàm LLM được inject vào.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/Apple/Project/Lab/K3-Day07-TranHieu-2A202602030
plugins: anyio-4.14.2
collecting ... collected 42 items

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

============================== 42 passed in 0.02s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Dùng `LocalEmbedder` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) thay vì mock, vì mock gần như ngẫu nhiên theo README nên dự đoán trước sẽ vô nghĩa. Dự đoán được viết **trước khi chạy** `compute_similarity()`, dựa trên trực giác đọc câu.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Sinh viên phải đăng ký học phần trước khi bắt đầu học kỳ mới." | "Người học cần thực hiện đăng ký môn học trước khi học kỳ mới bắt đầu." | cao | 0.975 | Đúng |
| 2 | "Thư viện cho sinh viên mượn tối đa 5 cuốn sách trong 2 tuần." | "Sinh viên vi phạm nội quy học đường có thể bị kỷ luật cảnh cáo." | thấp | 0.201 | Đúng |
| 3 | "Học bổng khuyến khích học tập xét theo điểm trung bình học kỳ." | "Chính sách miễn giảm học phí áp dụng cho sinh viên thuộc diện chính sách." | thấp (hai chính sách khác mục đích) | 0.414 | Gần đúng — thấp hơn cặp 1 nhưng cao hơn dự kiến, vì cùng chung miền "hỗ trợ tài chính cho sinh viên" |
| 4 | "Sinh viên nghỉ học tạm thời cần làm đơn xin bảo lưu kết quả học tập." | "Đội bóng đá của trường vừa giành chức vô địch giải sinh viên toàn quốc." | thấp | 0.152 | Đúng |
| 5 | "Chunking là quá trình chia văn bản dài thành các đoạn nhỏ hơn." | "Splitting a long document into smaller pieces is called chunking." | thấp (nghĩ khác ngôn ngữ thì vector sẽ khác) | 0.665 | **Sai** — điểm thực tế thuộc mức trung bình-cao |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 5: hai câu tiếng Việt và tiếng Anh cùng định nghĩa "chunking" nhưng không chung một từ nào, vậy mà similarity đạt 0.665 — cao hơn cả cặp 3 (hai câu cùng tiếng Việt nhưng khác chủ đề). Điều này cho thấy embedding đa ngữ mã hoá theo **ý nghĩa/khái niệm** chứ không phải theo bề mặt từ vựng hay ngôn ngữ viết — mô hình học được rằng "chunking" và "chia văn bản thành đoạn nhỏ" chiếu vào cùng một vùng không gian ngữ nghĩa dù ký tự hoàn toàn khác nhau. Đây cũng là lý do nhóm chọn `LocalEmbedder` đa ngữ cho corpus tiếng Việt của K3 thay vì một mô hình chỉ hỗ trợ tiếng Anh.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

**Cấu hình chạy** (đúng như `bench.py`): chiến lược cá nhân = `HeadingChunker(chunk_size=800)` (custom, tách theo `CHƯƠNG`/`Điều N.`/heading markdown — khác `FixedSizeChunker(500,50)` baseline của thành viên khác trong nhóm), `EMBEDDING_PROVIDER=local` (`paraphrase-multilingual-MiniLM-L12-v2`, không dùng mock), nạp qua `build_knowledge_base("data/k3_university", embedder, chunker=HeadingChunker())` → **103 chunk**. `llm_fn` dùng bản mô phỏng như `main.py` (không có API key thật) nên "câu trả lời của agent" thực chất là ngữ cảnh được lắp vào prompt; cột dưới tóm tắt xem ngữ cảnh đó có đủ để một LLM thật trả lời đúng hay không.

> **Ghi chú quan trọng:** bản chạy đầu tiên của `HeadingChunker` có 1 bug — khi một `Điều` dài hơn `chunk_size` bị chẻ tiếp theo đoạn, các mảnh con **không được gắn lại dòng heading**, nên mảnh thứ 2 trở đi mất ngữ cảnh "mình thuộc Điều nào". Bug này khiến câu 5 thất bại hoàn toàn (đáp án đúng rơi ngoài top-3). Sau khi sửa (gắn lại `heading` vào đầu mỗi mảnh con, xem `src/heading_chunker.py::_split_section`), kết quả dưới đây đã cải thiện — câu 5 lọt vào top-3. Số liệu bảng dưới là **sau khi sửa**.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên đăng ký học phần ở website nào và cần lưu ý gì? | `huong-dan-dang-ky-hoc-phan`: "Xem kỹ chương trình khung..." (đoạn "lưu ý") | 0.706 | Có, nhưng thiếu chi tiết — URL `dkhp.iuh.edu.vn` nằm ở chunk hạng **#5**, ngoài top-3 mà agent dùng | Agent trả lời được phần "lưu ý trước khi đăng ký" nhưng **không có URL cụ thể** trong ngữ cảnh |
| 2 | Sinh viên nộp học phí trực tuyến bằng cách nào? | `huong-dan-nop-hoc-phi-truc-tuyen`: đoạn về nộp các khoản phí khác (không phải nội dung chính) | 0.794 | Có, nhưng top-1 hơi lệch chủ đề — 2 cách nộp (ngân hàng + online) nằm ở #2 và #3, vẫn trong top-3 dùng bởi agent | Ngữ cảnh top-3 gộp lại có đủ cả 2 cách nộp, dù top-1 riêng lẻ không phải câu trả lời chính |
| 3 | Mức học bổng khuyến khích học tập tối đa là bao nhiêu? | `che-do-hoc-bong-sinh-vien`: điều kiện tích lũy tối thiểu 15 tín chỉ | **0.751** | Có — đúng tài liệu; đoạn chứa con số "130%" xếp hạng #2, vẫn trong top-3 | Ngữ cảnh top-3 có đủ đoạn chứa 130% để trả lời đúng |
| 4 | Kho sách ngoại văn của thư viện nằm ở tầng nào? | `huong-dan-su-dung-thu-vien`: đoạn "THƯ VIỆN SỐ" (tài liệu điện tử) — không phải đoạn nói về tầng lầu | 0.634 | Đúng tài liệu, sai nội dung cụ thể ở top-1; đoạn chứa "Lầu 3" xếp hạng #2, vẫn lọt top-3 | Ngữ cảnh top-3 vẫn có đáp án đúng (#2) lẫn đoạn không liên quan (#1) |
| 5 *(lọc metadata)* | Sinh viên bị ốm điều trị dài ngày thì việc học giải quyết thế nào? `metadata_filter={"audience":"student"}` | `quy-che-dao-tao-tin-chi`: "Điều 24. Xử lý vi phạm đối với sinh viên..." — sai nội dung | 0.493 | **Có** (sau khi sửa bug) — đoạn đúng "Điều 17. Nghỉ học tạm thời" xếp hạng **#3**, vừa lọt top-3; trước khi sửa bug thì nằm ngoài top-3 (fail hoàn toàn) | Ngữ cảnh top-3 giờ có 1/3 đoạn liên quan (#3) lẫn 2 đoạn nhiễu (#1, #2 — cũng về xử lý/cảnh báo sinh viên nên dễ gây nhiễu ngữ nghĩa) |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (1 câu — câu 1 — vẫn thiếu 1 chi tiết cụ thể ngoài top-3)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Bạn cùng nhóm dùng `FixedSizeChunker(500,50)` làm baseline, báo đạt 10/10 (cả 5 gold doc ở top-1) — vẫn cao hơn `HeadingChunker` của mình dù đã sửa bug (5/5 relevant trong top-3, nhưng chỉ 3-4/5 đúng ngay ở top-1). Bài học lớn nhất thực ra đến từ chính quá trình tự benchmark: `HeadingChunker` ban đầu **thất bại hoàn toàn ở câu 5** vì một bug tưởng nhỏ — chẻ một `Điều` dài mà không gắn lại heading vào các mảnh con, khiến mảnh chứa "Điều 17. Nghỉ học tạm thời" (đúng nội dung câu 5) mất tên "Điều 17" nên similarity với câu hỏi thấp hơn hẳn, rơi ngoài top-3. Sau khi gắn lại heading, đúng chunk đó nhảy từ ngoài-top-5 lên hạng #3. Đây là minh chứng cụ thể cho tiêu chí "Chunk Coherence" trong `docs/EVALUATION.md`: mất ngữ cảnh cấu trúc (ở đây là mất tên điều khoản) ảnh hưởng trực tiếp đến retrieval, dù nội dung câu chữ bên trong chunk không đổi.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 *(5/5 câu có chunk liên quan trong top-3; câu 1 thiếu 1 chi tiết cụ thể ngoài top-3)* |
| **Tổng phần cá nhân** | **59 / 60** |
