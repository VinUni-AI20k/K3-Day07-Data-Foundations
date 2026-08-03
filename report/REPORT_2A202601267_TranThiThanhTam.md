# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Thị Thanh Tâm
**Nhóm:** B2
**Ngày:** 3/8/2026

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Cosine similarity cao nghĩa là hai vector có xu hướng hướng về cùng một hướng trong không gian, do đó mang ý nghĩa tương đồng.

**Ví dụ có độ tương tự CAO:**

- Câu A: "Python là ngôn ngữ lập trình"
- Câu B: "Python là một ngôn ngữ lập trình phổ biến"
- Tại sao tương đồng: cả hai đều nói về cùng một chủ đề và có nhiều từ khóa chung.

**Ví dụ có độ tương tự THẤP:**

- Câu A: "Python là ngôn ngữ lập trình"
- Câu B: "Thời tiết hôm nay rất đẹp"
- Tại sao khác: nội dung và ngữ nghĩa hoàn toàn khác nhau.

**Tại sao độ tương tự cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**

> Vì embeddings biểu diễn ý nghĩa theo hướng, còn cosine similarity đo mức độ giống nhau về hướng của vector. Với text, đây là cách phù hợp hơn để đo ngữ nghĩa chứ không chỉ dựa vào khoảng cách tuyệt đối.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> Công thức: bước nhảy = 500 - 50 = 450
> Số chunk ≈ ceil(10000 / 450) = 23 chunk

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Nếu overlap tăng thì bước nhảy giảm, nên số lượng chunk tăng lên. Độ chồng chéo nhiều hơn giúp giữ lại ngữ cảnh giữa các chunk liên tiếp, đặc biệt khi chia tài liệu dài.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**SentenceChunker.chunk** — hướng tiếp cận:

> Tôi dùng regex để tách văn bản theo các dấu kết thúc câu như ". ", "! ", "? ". Sau đó gom các câu lại thành từng nhóm tối đa một số câu cho trước. Trường hợp văn bản rỗng hoặc không có dấu câu thì trả về danh sách rỗng hoặc một chunk duy nhất.

**RecursiveChunker.chunk / _split** — hướng tiếp cận:

> Thuật toán thử chia theo các separator theo thứ tự ưu tiên như \n\n, \n, ". ", " ", "". Nếu đoạn text vẫn quá dài sau khi chia theo separator, hàm sẽ tiếp tục đệ quy trên đoạn đó cho đến khi đủ nhỏ. Base case là khi đoạn text đã nhỏ hơn hoặc bằng chunk_size.

### Lớp EmbeddingStore

**add_documents + search** — hướng tiếp cận:

> Mỗi document được chuyển thành một record có nội dung, metadata và embedding. Khi tìm kiếm, hệ thống tạo embedding cho câu truy vấn rồi so sánh độ tương tự với các embedding đã lưu bằng cosine similarity hoặc dot product tương đương.

**search_with_filter + delete_document** — hướng tiếp cận:

> Trước tiên lọc các record theo metadata nếu có filter, sau đó mới thực hiện tìm kiếm similarity trên tập con đã lọc. Việc xóa document được thực hiện bằng cách loại bỏ các record có doc_id tương ứng.

### Tác tử KnowledgeBaseAgent

**answer** — hướng tiếp cận:

> Prompt được xây dựng bằng cách kết hợp câu hỏi với các chunk có độ liên quan cao nhất. Cách này giúp agent có ngữ cảnh để trả lời đúng hơn thay vì chỉ dựa vào câu hỏi ngắn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```text
42 passed in 0.15s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                            | Câu B                                       | Dự đoán        | Điểm thực tế | Đúng? |
| ---- | --------------------------------- | -------------------------------------------- | ----------------- | ---------------- | ------- |
| 1    | Python là ngôn ngữ lập trình | Python là ngôn ngữ lập trình phổ biến | cao               | cao              | Có     |
| 2    | Python là ngôn ngữ lập trình | Thời tiết hôm nay đẹp                   | thấp             | thấp            | Có     |
| 3    | Đăng ký môn học              | Đăng ký lớp học                         | cao               | cao              | Có     |
| 4    | Thư viện                        | Mượn sách                                 | cao               | cao              | Có     |
| 5    | Học phí                         | Học bổng                                   | trung bình/thấp | thấp            | Có     |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Điều bất ngờ là hai câu có cùng từ khóa nhưng không cùng ngữ cảnh vẫn có thể có điểm tương đồng khá cao. Điều này cho thấy embeddings không chỉ dựa vào từ đơn lẻ mà còn phản ánh cấu trúc ngữ nghĩa và ngữ cảnh.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

| # | Câu hỏi (Query)                    | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)        |
| - | ------------------------------------ | ------------------------------------------ | ------------ | --------------------------------- | -------------------------------------------- |
| 1 | Thủ tục đăng ký môn học       | Thông tin về đăng ký môn học        | 1            | Có                               | Trả lời đúng về quy trình đăng ký   |
| 2 | Cách mượn sách ở thư viện     | Thông tin dịch vụ thư viện            | 1            | Có                               | Trả lời đúng về quy trình mượn sách |
| 3 | Học phí có thay đổi không?     | Thông tin về học phí                   | 1            | Có                               | Trả lời đúng về chính sách học phí  |
| 4 | Học bổng dành cho sinh viên mới | Thông tin học bổng                      | 1            | Có                               | Trả lời đúng về điều kiện học bổng |
| 5 | Cách đăng ký ký túc xá        | Thông tin ký túc xá                    | 1            | Có                               | Trả lời đúng về quy trình đăng ký   |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Tôi học được rằng chiến lược chunking khác nhau có thể ảnh hưởng lớn đến chất lượng truy xuất, đặc biệt là khi dữ liệu có nhiều cấu trúc đoạn văn và metadata.

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
