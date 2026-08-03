# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Lê Công Dũng]
**Nhóm:** [2k355]
**Ngày:** [2/8/2026]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Độ tương tự cosine cao nghĩa là góc giữa hai vector nhúng (embeddings) rất nhỏ, tức hai vector gần như cùng hướng. Điều này cho thấy hai đoạn văn bản đang so sánh có nội dung hoặc ngữ cảnh rất giống nhau, dù chúng có thể dùng từ ngữ khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên năm nhất bắt buộc phải đăng ký ở tại Ký túc xá."
- Câu B: "Tân sinh viên VinUni phải thực hiện quy định nội trú."
- Tại sao tương đồng: Dù sử dụng các từ khác nhau ("năm nhất" vs "tân sinh viên", "Ký túc xá" vs "nội trú"), cả hai câu đều nói về cùng một ý tưởng: quy định nội trú cho sinh viên mới.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Apple vừa ra mắt dòng điện thoại mới với chip AI."
- Câu B: "Quả táo này rất ngọt và chứa nhiều vitamin."
- Tại sao khác: Cùng chứa từ "Apple/Táo" nhưng một câu nói về công nghệ, câu kia nói về trái cây, nên ý nghĩa của hai câu hoàn toàn khác nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine similarity chỉ đo góc giữa hai vector mà không bị ảnh hưởng bởi độ dài (magnitude) của vector. Vì vậy, nó đánh giá đúng hơn sự giống nhau về mặt ngữ nghĩa khi so sánh văn bản dài và ngắn hoặc vector có độ lớn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
Trình bày phép tính: Sử dụng công thức $N = \lceil \frac{\text{Total Length} - \text{Overlap}}{\text{Chunk Size} - \text{Overlap}} \rceil$. Với Total Length = 10000, Overlap = 50 và Chunk Size = 500, ta có $N = \lceil \frac{10000 - 50}{500 - 50} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22{.}11 \rceil = 23$.
Đáp án: 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Nếu overlap = 100, số chunk sẽ tăng lên, vì mỗi chunk mới di chuyển ít hơn so với chunk trước. Cụ thể, $N = \lceil \frac{10000 - 100}{500 - 100} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24{.}75 \rceil = 25$ chunks. Tăng overlap giúp giữ lại nhiều ngữ cảnh chung giữa các chunk, tránh cắt đứt ý nghĩa tại ranh giới và giúp truy xuất thông tin chính xác hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Tôi dùng regex `(?<=[.!?])\s+` để phát hiện các ranh giới câu dựa trên dấu chấm hỏi, dấu chấm than và dấu chấm kết thúc. Sau khi tách, tôi gom các câu thành các chunk theo `max_sentences_per_chunk`, đồng thời kiểm tra các trường hợp ngoại lệ như chữ viết tắt (ví dụ "Ths.", "Mr.") để tránh cắt sai chỗ.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán thử cắt văn bản lần lượt theo các dấu phân cách ưu tiên như `\n\n`, `\n`, ". ", và cuối cùng là khoảng trắng hoặc phân chia cố định. Base case là khi đoạn văn bản hiện tại đã nhỏ hơn hoặc bằng `chunk_size`, khi đó nó được giữ nguyên thành một chunk; nếu vẫn quá dài, `_split` gọi đệ quy với dấu phân cách tiếp theo.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Khi thêm tài liệu, tôi mã hóa nội dung bằng hàm nhúng và lưu từng bản ghi vào bộ nhớ RAM dưới dạng dict chứa `doc_id`, `content`, `metadata` và `embedding`. Khi search, tôi mã hóa truy vấn thành vector, duyệt qua các bản ghi đã lưu, tính score bằng tích vô hướng dot product, rồi sắp xếp và trả về top-k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Tôi lọc trước theo metadata bằng cách chỉ giữ các chunk mà `metadata` thỏa điều kiện, rồi mới thực hiện tìm kiếm tương tự. Hàm xóa đơn giản loại bỏ tất cả các record có `doc_id` trùng với doc_id được yêu cầu và trả về True nếu có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Tôi truy xuất top-k chunk từ vector store trước, sau đó xây dựng prompt gồm phần `[Ngữ cảnh]` nối các chunk và phần `[Câu hỏi]`. Cuối cùng, tôi gọi `llm_fn` với prompt này và yêu cầu LLM chỉ trả lời dựa trên ngữ cảnh đã cung cấp, nếu không tìm thấy thì trả về "Không có thông tin trong tài liệu".

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: D:\DATA\Visual\K3-Day07-E403-2k355
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

============================= 42 passed in 0.11s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Sinh viên năm nhất phải đăng ký ở Ký túc xá." | "Tân sinh viên VinUni cần thực hiện nội trú." | cao | 0.5291 | Có |
| 2 | "Apple vừa ra mắt dòng điện thoại mới với chip AI." | "Quả táo này rất ngọt và chứa nhiều vitamin." | thấp | 0.4073 | Có |
| 3 | "Chính sách học bổng hỗ trợ sinh viên tài năng." | "Quy trình yêu cầu hỗ trợ tài chính cho sinh viên." | cao | 0.6892 | Có |
| 4 | "Thư viện cung cấp dịch vụ mượn sách cho sinh viên." | "Sinh viên có thể mượn máy tính xách tay tại thư viện." | cao | 0.7678 | Có |
| 5 | "Học bổng đầu vào có tiêu chí duy trì năng lực học tập." | "Cảnh quan ký túc xá rất đẹp và tiện nghi." | thấp | 0.0898 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Kết quả bất ngờ nhất là cặp 2 vẫn có điểm tương tự trung bình (0.4073) dù ý nghĩa khác biệt rõ rệt, có lẽ vì embeddings vẫn ghi nhận mối liên hệ ngôn ngữ chung quanh từ "Apple/Táo" và cấu trúc câu tương tự. Điều này cho thấy embeddings không chỉ phân biệt ý nghĩa cụm từ mà còn phản ánh một phần đặc điểm ngôn ngữ và bối cảnh chung, nên vẫn có điểm dương ngay cả khi nội dung không giống nhau.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. Tôi sử dụng `EmbeddingStore` với `LocalEmbedder` và metadata filtering để làm rõ kết quả khi câu hỏi liên quan tới một lĩnh vực cụ thể.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | Sinh viên đại học VinUniversity được mượn tối đa bao nhiêu tài liệu và trong bao lâu? | `vinuni-library-borrowing`: dịch vụ mượn tài liệu và thiết bị tại thư viện. | 0.7778 | Có | Trả lời đúng: sinh viên đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. |
| 2 | Nếu muốn yêu cầu hỗ trợ tài chính cho học kỳ Thu, sinh viên cần nộp hồ sơ trong khoảng thời gian nào và hạn xử lý là ngày nào? | `vinuni-financial-aid-request`: quy trình nộp hồ sơ hỗ trợ tài chính. | 0.7676 | Có | Trả lời đúng: nhận hồ sơ từ 20/6 đến 10/7 và xử lý trước ngày 2/8. |
| 3 | Học bổng Full và 100% cần GPA tối thiểu bao nhiêu để duy trì? | `vinuni-scholarship-maintenance`: tiêu chí duy trì học bổng đầu vào và hỗ trợ tài chính. | 0.7829 | Có | Trả lời đúng: GPA tích lũy tối thiểu 3.2 để duy trì. |
| 4 | Trong ký túc xá VinUni, có những loại căn hộ nào và sinh viên nam/nữ ở tòa nào? | `vinuni-dormitory-services`: thông tin phòng ở và tiện ích ký túc xá. | 0.7814 | Có | Trả lời đúng: có căn 8 người, 4 người, 2 người; sinh viên nữ ở tòa JA, nam ở tòa JB. |
| 5 | Với metadata `category=health-and-wellbeing`, sinh viên cần đến phòng nào để nhận dịch vụ y tế trực tiếp và số hotline là gì? | `vinuni-wellbeing-services`: dịch vụ sức khỏe thể chất và tinh thần. | 0.6313 | Có | Trả lời đúng: phòng I119 và hotline (+84) 866 200 019. |

**Top-3 kết quả với metadata filter (nếu áp dụng):**

- Query 1: không áp dụng filter; top-3 chủ yếu là `library-borrowing` và `library-learning-support`, cả hai đều liên quan đến dịch vụ thư viện.
- Query 2: không áp dụng filter; top-3 đều nằm trong `vinuni-financial-aid-request`, vì câu hỏi này rất cụ thể và đúng với tài liệu quy trình hỗ trợ tài chính.
- Query 3: không áp dụng filter; top-3 đều là `vinuni-scholarship-maintenance`, cho thấy truy xuất đúng tài liệu học bổng.
- Query 4: không áp dụng filter; top-3 vẫn giữ đúng `vinuni-dormitory-services`, với một vài kết quả nhiễu nhẹ về thư viện.
- Query 5: khi áp dụng filter `category=health-and-wellbeing`, top-3 đều là `vinuni-wellbeing-services`, giúp tăng độ chính xác và giảm nhiễu từ các tài liệu về hỗ trợ sinh viên khác.

**Nhận xét:**
Tôi thấy metadata filtering rất hữu ích ở câu hỏi liên quan đến y tế và sức khỏe, vì nó thu hẹp không gian tìm kiếm và giúp hệ thống tập trung đúng tài liệu chuyên ngành. Trong các câu hỏi về thư viện, tài chính, học bổng và ký túc xá, việc dùng embedding + metadata đã cho kết quả tương đối chính xác và phù hợp với ngữ cảnh.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng việc dùng metadata filter kết hợp với embedding retrieval giúp giảm nhiễu đáng kể, đặc biệt ở các câu hỏi có nhiều tài liệu cùng chủ đề nhưng khác mục đích (ví dụ dịch vụ y tế vs hỗ trợ sinh viên tổng quát).

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