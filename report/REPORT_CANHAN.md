# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Việt Trường
**Mã học viên:** 2A202601467
**Nhóm:** TruongTieuThu
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector có hướng gần nhau trong không gian embedding, nên hai đoạn văn thường có nội dung hoặc ngữ cảnh gần nhau. Điểm gần 1 cho thấy mức tương đồng cao; điểm gần 0 cho thấy ít liên hệ.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên đăng ký học phần trực tuyến trên cổng đào tạo.
- Câu B: Người học chọn môn học qua hệ thống đăng ký online.
- Tại sao tương đồng: Cả hai đều nói về cùng một hành động và ngữ cảnh đăng ký môn học.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Thư viện mở cửa đến 21 giờ.
- Câu B: Hôm nay nhiệt độ ngoài trời là 30 độ C.
- Tại sao khác: Hai câu đề cập đến hai chủ đề độc lập: dịch vụ thư viện và thời tiết.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine so sánh hướng của vector nên ít bị ảnh hưởng bởi độ lớn của embedding hoặc độ dài văn bản. Với text embeddings, hướng thường biểu đạt quan hệ ngữ nghĩa tốt hơn khoảng cách thẳng giữa hai điểm.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11)`.
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng thành `ceil((10.000 - 100) / (500 - 100)) = ceil(24,75) = 25 chunks`. Overlap lớn hơn giữ lại ngữ cảnh ở ranh giới giữa hai chunk, nên giảm nguy cơ tách rời một ý hoặc câu trả lời quan trọng; đánh đổi là nhiều dữ liệu và embedding hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])(?:\s+|$)` để cắt sau dấu kết thúc câu, giữ lại dấu câu trong nội dung. Các câu trống hoặc chỉ có khoảng trắng được loại bỏ; nếu văn bản không có dấu kết thúc câu, toàn bộ văn bản vẫn được trả về như một chunk hợp lệ.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán ưu tiên lần lượt ngắt đoạn, xuống dòng, kết thúc câu, khoảng trắng rồi mới hard-split. Base case là đoạn có độ dài không lớn hơn `chunk_size`; nếu hết separator mà vẫn dài, đoạn được cắt an toàn theo kích thước cố định để không mất nội dung.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hoá thành record gồm id duy nhất, content, metadata, và vector embedding. Store lưu record trong bộ nhớ (và đồng bộ ChromaDB khi khả dụng); truy vấn được embed rồi xếp hạng giảm dần bằng dot product, phù hợp với embedding đã được chuẩn hoá.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc chính xác metadata trước, sau đó mới tính điểm trên tập ứng viên còn lại để tránh kết quả sai phạm vi. `delete_document` dùng `metadata['doc_id']` để xoá toàn bộ chunks của một tài liệu và trả về trạng thái có bản ghi nào bị xoá hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunks, đánh số từng chunk rồi chèn chúng vào phần `Ngữ cảnh` của prompt. Prompt yêu cầu LLM chỉ dựa vào ngữ cảnh và nói rõ khi thiếu thông tin, giúp hạn chế câu trả lời không có căn cứ.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
42 passed in 0.05s
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần trực tuyến. | Người học chọn môn trên cổng đăng ký. | cao | 0,2628 | Có (cao nhất) |
| 2 | Thư viện mở cửa đến 21 giờ. | Ký túc xá có quy định giờ giấc riêng. | thấp | 0,1012 | Có (thấp) |
| 3 | Học bổng hỗ trợ sinh viên có thành tích tốt. | Sinh viên xuất sắc có thể nhận hỗ trợ học tập. | cao | -0,1613 | Không |
| 4 | Tôi nộp học phí qua cổng thanh toán. | Phí ký túc xá được thanh toán theo học kỳ. | trung bình | 0,1532 | Có |
| 5 | Cách mượn sách tại thư viện là gì? | Thời tiết hôm nay có mưa không? | thấp | 0,2074 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 3 có ý nghĩa gần nhau nhưng nhận điểm âm, trong khi cặp 5 không liên quan lại nhận điểm dương. Tôi chạy bảng này với `MockEmbedder` mặc định để kiểm thử mã nguồn; nó sinh vector xác định nhưng không mang ngữ nghĩa. Vì vậy, các điểm này xác nhận hàm cosine hoạt động, nhưng không thể dùng để đánh giá chất lượng retrieval; khi so sánh thật cần dùng local multilingual embedder.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> **Trạng thái chờ nhóm:** `REPORT_NHOM.md` hiện chưa có 5 benchmark queries/gold answers được nhóm thống nhất. Tôi không tự tạo dữ liệu nhóm để tránh làm sai phần nộp chung. Khi nhóm chốt 5 câu hỏi, chạy cùng `EMBEDDING_PROVIDER=local` và điền kết quả vào bảng bên dưới trước khi mở PR.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Chờ benchmark chung của nhóm | — | — | — | — |
| 2 | Chờ benchmark chung của nhóm | — | — | — | — |
| 3 | Chờ benchmark chung của nhóm | — | — | — | — |
| 4 | Chờ benchmark chung của nhóm | — | — | — | — |
| 5 | Chờ benchmark chung của nhóm | — | — | — | — |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** Chờ benchmark chung / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chờ phần demo và so sánh retrieval của nhóm. Sau buổi demo, tôi sẽ ghi lại một quan sát cụ thể về ảnh hưởng của chunking và metadata đối với top-3 kết quả.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | Chờ benchmark chung / 10 |
| **Tổng phần cá nhân** | **50 / 50 đã hoàn thành; chờ 10 điểm phần nhóm phụ thuộc** |
