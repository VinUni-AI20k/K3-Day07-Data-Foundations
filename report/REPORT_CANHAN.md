# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có cosine similarity cao khi chúng hướng gần giống nhau trong không gian vector. Điều này thường cho thấy hai đoạn văn có ý nghĩa hoặc ngữ cảnh gần nhau, dù không nhất thiết dùng cùng từ ngữ.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên có thể xin gia hạn thời hạn đóng học phí.
- Câu B: Người học được phép đề nghị lùi hạn thanh toán học phí.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng cùng diễn đạt việc sinh viên yêu cầu kéo dài hạn thanh toán học phí.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên được mượn tài liệu từ thư viện trong 30 ngày.
- Câu B: Dự báo thời tiết cho biết ngày mai có mưa lớn.
- Tại sao khác: Hai câu thuộc hai chủ đề và mục đích hoàn toàn khác nhau: dịch vụ thư viện và thời tiết.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào góc giữa hai vector, nên đánh giá hướng biểu diễn ngữ nghĩa và ít bị ảnh hưởng bởi độ lớn của vector. Khoảng cách Euclid phụ thuộc cả độ lớn, vì vậy hai embedding cùng hướng nhưng khác độ dài vẫn có thể bị xem là xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Phép tính:* `ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.111...)`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng lên 25 vì `ceil((10,000 - 100) / (500 - 100)) = ceil(9,900 / 400) = 25`. Overlap lớn hơn giữ được nhiều ngữ cảnh tại ranh giới chunk và giảm nguy cơ tách rời thông tin liên quan, nhưng làm tăng nội dung trùng lặp, dung lượng lưu trữ và chi phí embedding/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng ngay sau dấu kết thúc câu, nhờ đó dấu câu vẫn nằm ở câu phía trước. Text rỗng trả về `[]`; các phần được `strip`, bỏ phần rỗng rồi ghép theo từng nhóm không vượt quá `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử separator theo thứ tự đoạn, dòng, câu, từ và cuối cùng là ký tự; các phần liền nhau được gộp cho đến trước khi vượt `chunk_size`. Base case là text đã đủ ngắn; nếu hết separator hoặc gặp separator rỗng thì cắt fixed-size. Mỗi lần đệ quy đều bỏ separator hiện tại nên luôn tiến gần điều kiện dừng.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi dùng store in-memory; mỗi `Document` được chuẩn hóa thành record gồm ID chunk duy nhất, content, bản sao metadata, `doc_id` gốc và embedding. `search` chỉ tạo query embedding một lần, tính dot product với embedding của từng record, sắp xếp score giảm dần rồi lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước rồi mới xếp hạng trên tập ứng viên còn lại; như vậy các tài liệu hợp lệ không bị loại chỉ vì không nằm trong top-k toàn cục. `delete_document` loại tất cả record có `metadata['doc_id']` trùng ID tài liệu gốc và trả `True` khi thực sự xóa được ít nhất một record.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi `store.search`, đánh số từng chunk `[1]`, `[2]`, ... và đưa kèm `doc_id` cùng `source_url` hoặc đường dẫn nguồn vào context. Prompt yêu cầu chỉ dùng context, dẫn nguồn bằng số thứ tự và nói rõ khi thiếu thông tin; nếu store không trả kết quả thì agent trả thông báo ngay mà không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ python -m pytest tests -v
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.1.1
rootdir: D:\workSpace\VinAI\K3-Day07-Data-Foundations-NhomC2
collected 42 items

tests/test_solution.py::TestProjectStructure (2 tests) PASSED
tests/test_solution.py::TestClassBasedInterfaces (2 tests) PASSED
tests/test_solution.py::TestFixedSizeChunker (7 tests) PASSED
tests/test_solution.py::TestSentenceChunker (4 tests) PASSED
tests/test_solution.py::TestRecursiveChunker (4 tests) PASSED
tests/test_solution.py::TestEmbeddingStore (8 tests) PASSED
tests/test_solution.py::TestKnowledgeBaseAgent (2 tests) PASSED
tests/test_solution.py::TestComputeSimilarity (4 tests) PASSED
tests/test_solution.py::TestCompareChunkingStrategies (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter (3 tests) PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument (3 tests) PASSED

============================= 42 passed in 0.13s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Hạn mức, thời hạn và gia hạn mượn | `rmit-library-borrowing-returning:13` — menu/liên hệ thư viện (`0.2326`) | 0/2 | Không; thiếu cả hai evidence marker | Agent trích context thư viện nhưng không có hạn mức 25 tài liệu hay gia hạn 15 ngày. |
| 2 | Điều kiện gia hạn thanh toán Standard Course | `rmit-fees-payments:2` — trang tổng quan học phí (`0.2764`) | 0/2 | Không | Agent nhận context cùng chủ đề phí nhưng thiếu mức nợ dưới 5 triệu và giới hạn 45 ngày. |
| 3 | Biểu mẫu và nơi hủy chương trình | `rmit-enrolment:0` — navigation trang enrolment (`0.2641`) | 0/2 | Không | Agent không lấy được chunk 10 chứa Program Cancellation form trong myRMIT. |
| 4 | Công dụng thẻ sinh viên | `rmit-defer-payment:16` — chứng từ thanh toán (`0.4011`) | 0/2 | Không | Top-3 có `rmit-student-cards:4` nhưng đó là ưu đãi, thiếu chunk 3 chứa danh sách công dụng chính. |
| 5 | Phí khi hủy sau Census Date | `rmit-library-borrowing-returning:10` — hư hỏng tài liệu (`0.4253`) | 0/2 | Không | Context không có câu “still liable for tuition and other fees”, nên agent không thể trả lời đúng. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 0 / 5

### Nhận xét benchmark và failure analysis

**Embedder và giới hạn phép đo:** Tôi đã thử cài `requirements-local.txt`, nhưng `sentence-transformers`/PyTorch không hoàn tất trên môi trường Python 3.14 trong thời gian cho phép. Benchmark vì vậy dùng MockEmbedder deterministic. Kết quả 0/10 chỉ phản ánh xếp hạng của vector mock, không đủ để kết luận Recursive-400 tốt hay xấu; số chunk (103), coherence và provenance vẫn kiểm chứng được.

**Precision và chunk coherence:** Các chunk Recursive-400 nhìn chung giữ được danh sách và đoạn văn tự nhiên. Tuy nhiên precision top-3 là 0/5 theo evidence marker; đúng `doc_id` không được tính nếu section không chứa bằng chứng.

**A/B metadata filter:** Ở Q1, có filter trả `[library:13, library:9, library:8]`; không filter trả `[defer-payment:8, library:13, enrolment:0]`. Filter giảm nhiễu giữa tài liệu nhưng không lấy được chunks 3–4, nên tăng precision cấp document mà chưa tăng precision cấp chunk.

**Grounding:** Agent offline chỉ trích nguyên context và giữ citation `[1]`, `[2]`, `[3]`, nên không bịa ngoài retrieval. Dù vậy, context thiếu evidence ở cả năm query nên câu trả lời không đúng/không đủ; score cao nhất `0.4253` ở Q5 vẫn là chunk sai về hư hỏng sách, chứng minh score chỉ là tín hiệu xếp hạng.

**Failure case rõ nhất — Q1:** Sau filter, cả ba slot đều thuộc đúng tài liệu thư viện nhưng chunks 13/9/8 lần lượt nói về menu, hư hỏng và mất tài liệu; chúng không chứa `Loan quota - 25 items` hay `Renewals last 15 days` nằm ở chunks 3–4. Nguyên nhân trực tiếp là MockEmbedder không có ngữ nghĩa; thêm vào đó Recursive-400 không overlap nên mỗi section bằng chứng chỉ có một cơ hội lọt top-k. Đề xuất: chạy lại mọi strategy bằng cùng multilingual semantic embedder, làm sạch navigation/footer, và thử recursive có overlap hoặc gắn lại heading vào từng chunk dài.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
