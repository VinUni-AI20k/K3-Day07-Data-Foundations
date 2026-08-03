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
> Hai văn bản hoặc hai vector có độ tương tự cosine cao khi chúng cùng hướng, tức là biểu diễn ngữ nghĩa gần nhau dù độ dài câu có thể khác nhau. Nói đơn giản, hai câu càng nói về cùng một ý thì cosine similarity càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký môn học trên cổng thông tin."
- Câu B: "Việc đăng ký học phần được thực hiện trên hệ thống portal."
- Tại sao tương đồng: Hai câu đều nói về cùng một quy trình đăng ký môn, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thư viện mở cửa vào thứ Hai."
- Câu B: "Mặt trời mọc ở phía Đông."
- Tại sao khác: Hai câu gần như không liên quan về ngữ nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì embeddings thường quan tâm nhiều đến hướng của vector hơn là độ lớn tuyệt đối. Cosine similarity đo mức độ cùng hướng nên phù hợp hơn với text, trong khi Euclidean distance dễ bị ảnh hưởng bởi độ dài vector và biên độ.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> *Đáp án:*
> 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100 thì số chunk tăng lên: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh tốt hơn giữa các chunk, nhưng đổi lại làm tăng số lượng chunk và chi phí lưu trữ/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Mình tách câu bằng regex nhận diện dấu kết thúc câu như `.`, `!`, `?` rồi nhóm lại theo `max_sentences_per_chunk`. Nếu text rỗng thì trả về `[]`; nếu không tách được câu thì vẫn trả về chuỗi đã `strip()` để không làm hỏng dữ liệu đầu vào.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Mình thử tách theo danh sách separator theo thứ tự ưu tiên, từ lớn đến nhỏ. Base case là khi text đã đủ ngắn hơn `chunk_size`, khi không còn separator thì fallback về cắt cố định theo `chunk_size` để luôn trả về kết quả hợp lệ.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được đổi thành một record chuẩn hóa gồm `id`, `content`, `metadata`, `embedding` rồi lưu vào bộ nhớ; nếu có Chroma thì thêm cả vào collection. Khi tìm kiếm, mình embed query rồi tính dot product với tất cả embeddings đã lưu, sau đó sort giảm dần theo `score`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Mình lọc theo metadata trước rồi mới tính similarity để tránh các chunk không đúng điều kiện. Xóa thì duyệt toàn bộ store và loại những record có `metadata["doc_id"]` khớp với `doc_id` cần xóa, đồng thời trả về `True/False` tùy có xóa được hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Mình lấy top-k chunks từ store, nối chúng thành phần `Context` có đánh số và nguồn tương ứng. Prompt yêu cầu LLM chỉ trả lời dựa trên context đã truy xuất, nếu không đủ thông tin thì nói rõ là không chắc chắn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================== 42 passed in 0.13s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a programming language. | Python is a coding language. | thấp | -0.056473 | Đúng |
| 2 | The library opens at 8 a.m. | The library opens at 8 a.m. | cao | 1.000000 | Đúng |
| 3 | I enjoy machine learning. | The moon is bright tonight. | thấp | 0.122294 | Đúng |
| 4 | Students register for courses online. | Course registration is done on the university portal. | cao | 0.235219 | Đúng |
| 5 | Water boils at 100 degrees Celsius. | Bananas are yellow fruits. | thấp | -0.021602 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp câu về đăng ký môn và cổng thông tin có điểm không quá cao dù ý nghĩa khá gần, cho thấy embeddings của mock backend chưa thật sự phản ánh ngữ nghĩa tốt. Điều này nhắc mình rằng để đánh giá retrieval nghiêm túc thì phải dùng embedder thật hoặc ít nhất là embedder cục bộ phù hợp ngôn ngữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** Chờ bộ 5 benchmark queries của nhóm để điền số liệu.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chờ phần benchmark chung của nhóm để tổng hợp sau.

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
