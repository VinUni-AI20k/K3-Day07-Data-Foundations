# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Văn Lưu  
**Mã học viên:** 2A202601857  
**Nhóm:** C5-3  
**Ngày nộp:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai vector biểu diễn hai văn bản có hướng gần giống nhau, cosine similarity sẽ cao. Điều này cho thấy hai nội dung có ý nghĩa tương đồng, dù không nhất thiết cùng từ vựng.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần trong cổng học vụ."
- Câu B: "Học phần được đăng ký qua hệ thống học vụ trực tuyến."
- Tại sao tương đồng: Cả hai đều nói về quy trình đăng ký học phần trong môi trường học vụ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên đăng ký học phần."
- Câu B: "Thư viện cho phép mượn sách trong thời gian dài."
- Tại sao khác: Hai câu đề cập đến hai chủ đề khác nhau: đăng ký học phần và dịch vụ thư viện.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, phù hợp hơn cho việc so sánh ý nghĩa ngữ nghĩa giữa các văn bản. Euclidean distance lại nhạy hơn với độ lớn của vector, nên ít phản ánh đúng sự tương đồng về ý nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: $\lceil (10000 - 500) / (500 - 50) \rceil + 1 = \lceil 9500 / 450 \rceil + 1 = 22 + 1 = 23$ chunk.  
> **Đáp án:** 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng, bước trượt giảm, nên số chunk tăng lên. Độ chồng chéo nhiều hơn giúp giữ lại ngữ cảnh ở giữa các chunk, đặc biệt hữu ích cho các đoạn văn dài hoặc khi cần nối kết ý nghĩa giữa các đoạn liên tiếp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex để tách văn bản theo các dấu kết thúc câu như `.`, `!`, `?` kèm theo khoảng trắng hoặc dòng mới. Sau đó, tôi chuẩn hóa khoảng trắng và gom các câu lại theo số câu tối đa cho mỗi chunk để giữ chunk ngắn gọn và dễ đọc.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi triển khai thuật toán đệ quy theo từng mức dấu phân cách ưu tiên: đoạn xuống dòng, dấu câu, khoảng trắng và cuối cùng là cắt theo kích thước. Khi gặp separator phù hợp, hàm sẽ nhóm nội dung lại; nếu một đoạn vượt quá kích thước, hàm tiếp tục chia đệ quy ở mức thấp hơn để bảo toàn ý nghĩa ngữ cảnh.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi tài liệu được chuyển thành một record có nội dung, metadata và vector embedding. Khi tìm kiếm, hệ thống tạo embedding cho câu hỏi rồi tính cosine similarity với toàn bộ vector đã lưu để chọn kết quả phù hợp nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi thực hiện lọc metadata trước khi tính similarity để giảm nhiễu kết quả. Khi xóa tài liệu, hệ thống loại bỏ toàn bộ các record liên quan đến `doc_id` tương ứng để giữ kho dữ liệu nhất quán.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent sẽ lấy các chunk phù hợp nhất từ store, ghép thành ngữ cảnh rồi tạo prompt cho mô hình. Cách này giúp câu trả lời có nền tảng rõ ràng và dễ trace tới đoạn tài liệu gốc.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts ==============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py ..........................................        [100%]

============================= 42 passed in 0.15s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Đăng ký học phần | Đăng ký môn học | cao | 0.95 | Có |
| 2 | Thư viện | Mượn sách | cao | 0.93 | Có |
| 3 | Học phí | Đăng ký học phần | thấp | 0.62 | Không |
| 4 | Thời gian học | Lịch học | cao | 0.94 | Có |
| 5 | Mượn sách | Học bổng | thấp | 0.58 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp “học phí” và “đăng ký học phần” có điểm tương đồng khá cao hơn dự đoán ban đầu. Điều này cho thấy embeddings có thể phản ánh các mối liên hệ ngữ cảnh trong cùng miền dữ liệu, dù không luôn chỉ dựa trên từ đồng nghĩa trực tiếp.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Cách đăng ký học phần trong cổng học vụ | Tài liệu đăng ký học phần | 0.91 | Có | Trả lời về quy trình đăng ký học phần và điều kiện cần kiểm tra trước khi xác nhận. |
| 2 | Quy định mượn và gia hạn tài liệu thư viện | Tài liệu dịch vụ thư viện | 0.88 | Có | Trả lời rằng thư viện cần thẻ định danh và có quy định mượn, gia hạn, quá hạn. |
| 3 | Điều kiện tiên quyết của một học phần | Tài liệu đăng ký học phần | 0.86 | Có | Nêu rõ học phần có thể có học phần tiên quyết và cần kiểm tra trước khi đăng ký. |
| 4 | Khi nào cần gửi yêu cầu ngoại lệ cho đăng ký | Tài liệu đăng ký học phần | 0.84 | Có | Gợi ý gửi qua kênh hỗ trợ học vụ khi gặp lỗi trùng lịch hoặc trường hợp ngoại lệ. |
| 5 | Thẻ định danh có cần thiết khi mượn tài liệu không | Tài liệu dịch vụ thư viện | 0.90 | Có | Xác nhận người dùng cần mang thẻ định danh hợp lệ khi mượn tài liệu. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua demo, tôi hiểu rõ rằng chiến lược chunking và metadata rất ảnh hưởng đến chất lượng truy xuất. Khi chunk giữ được ngữ cảnh và metadata được thiết kế rõ ràng, agent trả lời sẽ chính xác và dễ giải thích hơn.

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
