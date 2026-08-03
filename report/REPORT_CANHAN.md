# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Thế Dũng
**Nhóm:** C05_03
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Độ tương tự cosine cao nghĩa là hai vector embedding hướng gần giống nhau, vì vậy hai đoạn văn thường có nội dung hoặc ý nghĩa ngữ nghĩa gần nhau. Điểm càng gần 1 thì mức độ tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**

- Câu A: Sinh viên đăng ký học phần trên cổng học vụ.
- Câu B: Người học chọn môn học thông qua hệ thống đăng ký trực tuyến.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng cùng nói về việc sinh viên đăng ký môn học trên một hệ thống trực tuyến.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Thư viện cho phép sinh viên gia hạn tài liệu đang mượn.
- Câu B: Thời tiết hôm nay có mưa lớn vào buổi chiều.
- Tại sao khác: Hai câu thuộc hai chủ đề không liên quan, một câu nói về dịch vụ thư viện và câu còn lại nói về thời tiết.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Cosine similarity tập trung vào hướng của vector, tức mẫu phân bố đặc trưng ngữ nghĩa, thay vì bị ảnh hưởng nhiều bởi độ lớn của vector. Vì vậy nó phù hợp hơn khi so sánh ý nghĩa của các văn bản có độ dài hoặc cường độ embedding khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> Phép tính: `ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.11) = 23`.
> **Đáp án: 23 chunks.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Khi overlap tăng lên 100, số chunk là `ceil((10,000 - 100) / (500 - 100)) = ceil(9,900 / 400) = 25`, tức tăng từ 23 lên 25 chunks. Overlap lớn hơn giúp giữ ngữ cảnh nằm gần ranh giới giữa hai chunk, nhưng đổi lại làm tăng dữ liệu trùng lặp, dung lượng lưu trữ và chi phí embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Tôi dùng regex `(?<=[.!?])(?:[ \t]+|\n+)` để tách tại khoảng trắng hoặc xuống dòng ngay sau dấu kết thúc câu, nhờ đó vẫn giữ lại dấu câu. Các câu được loại khoảng trắng thừa rồi gom theo `max_sentences_per_chunk`; văn bản rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán thử lần lượt các dấu phân cách từ cấu trúc lớn đến nhỏ: đoạn văn, dòng, câu, từ rồi ký tự. Nếu đoạn đã ngắn hơn `chunk_size` thì trả về ngay; nếu không còn dấu phân cách phù hợp thì chia cố định theo ký tự, bảo đảm đệ quy luôn tiến triển và không tạo vòng lặp vô hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> `add_documents` tạo embedding cho nội dung, gắn ID bản ghi duy nhất và lưu nội dung, vector cùng metadata vào bộ nhớ; nếu ChromaDB khả dụng thì bản ghi cũng được đồng bộ sang collection. `search` embedding câu hỏi, tính tích vô hướng giữa query vector và từng vector đã lưu, sau đó sắp xếp điểm giảm dần và trả về tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> `search_with_filter` lọc trước các bản ghi có metadata khớp tất cả điều kiện, sau đó mới tính độ tương tự trên tập ứng viên nhỏ hơn. `delete_document` tìm và xóa toàn bộ chunk có `metadata['doc_id']` trùng với ID tài liệu; hàm trả về `True` khi có bản ghi bị xóa và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> `answer` truy xuất các chunk liên quan nhất, đánh số từng nguồn rồi ghép chúng vào phần `NGỮ CẢNH` của prompt cùng câu hỏi. Prompt yêu cầu mô hình chỉ trả lời từ ngữ cảnh và phải nói rõ khi thông tin chưa đủ, sau đó chuyển prompt hoàn chỉnh cho `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
Lệnh: .venv\python.exe -m pytest tests -v
Môi trường: Windows, Python 3.11.9, pytest 9.1.1
Kết quả: collected 42 items
============================= 42 passed in 0.11s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán    | Điểm thực tế | Đúng? |
| --- | ----- | ----- | ---------- | ------------ | ----- |
| 1   |       |       | cao / thấp |              |       |
| 2   |       |       | cao / thấp |              |       |
| 3   |       |       | cao / thấp |              |       |
| 4   |       |       | cao / thấp |              |       |
| 5   |       |       | cao / thấp |              |       |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> _Viết 2-3 câu:_

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| #   | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| --- | --------------- | ------------------------------------ | ---------- | ------------------------------ | ------------------------------- |
| 1   |                 |                                      |            |                                |                                 |
| 2   |                 |                                      |            |                                |                                 |
| 3   |                 |                                      |            |                                |                                 |
| 4   |                 |                                      |            |                                |                                 |
| 5   |                 |                                      |            |                                |                                 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** \_\_ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> _Viết 2-3 câu:_

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | / 5              |
| Hướng tiếp cận của tôi (My Approach)            | / 10             |
| Hoàn thiện code (Core Implementation — tests)   | / 30             |
| Dự đoán độ tương tự (Similarity Predictions)    | / 5              |
| Kết quả truy xuất của tôi (Competition Results) | / 10             |
| **Tổng phần cá nhân**                           | **/ 60**         |
