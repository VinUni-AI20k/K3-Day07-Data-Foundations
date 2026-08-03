# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phan Bá Khánh Linh - 2A202601989
**Nhóm:** C11
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding gần như "chỉ cùng một hướng" trong không gian nhiều chiều — tức nội dung ngữ nghĩa của hai đoạn văn bản gần giống nhau, bất kể chúng dài ngắn khác nhau hay dùng từ ngữ khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên cần đăng ký học phần trước ngày 15/8."
- Câu B: "Hạn chót đăng ký môn học là ngày 15 tháng 8."
- Tại sao tương đồng: cùng diễn đạt một ý — mốc thời hạn đăng ký học phần — chỉ khác cách dùng từ ("học phần" ↔ "môn học", "trước ngày" ↔ "hạn chót"), nên vector embedding của hai câu có hướng gần như trùng nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên cần đăng ký học phần trước ngày 15/8."
- Câu B: "Thư viện mở cửa từ 7h đến 21h các ngày trong tuần."
- Tại sao khác: hai câu nói về hai chủ đề hoàn toàn khác nhau (đăng ký học phần vs. giờ mở cửa thư viện), không chia sẻ khái niệm ngữ nghĩa nào đáng kể, nên vector của chúng gần như vuông góc nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ đo **góc/hướng** giữa hai vector, bỏ qua độ lớn (magnitude) — trong khi magnitude của embedding thường bị ảnh hưởng bởi độ dài văn bản chứ không phản ánh ý nghĩa. Hai đoạn văn bản cùng ý nhưng độ dài khác nhau có thể có magnitude khác nhau; Euclidean distance sẽ "phạt" sự khác biệt đó dù ngữ nghĩa giống nhau, còn cosine vẫn cho điểm cao vì hướng vector không đổi.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Trình bày phép tính:
> `số chunk = ceil((độ_dài_tài_liệu - overlap) / (chunk_size - overlap))`
> `= ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
>
> **Đáp án: 23 chunks.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks` — tăng từ 23 lên 25 (mỗi bước trượt (`chunk_size - overlap`) nhỏ hơn nên cần nhiều bước hơn để phủ hết văn bản). Overlap lớn hơn giúp bảo toàn ngữ cảnh ở ranh giới chunk — nếu một câu/ý bị cắt ngang giữa hai chunk, phần overlap đảm bảo ý đó vẫn xuất hiện trọn vẹn ở chunk liền kề, giảm rủi ro mất thông tin khi retrieval chỉ lấy đúng một chunk; đánh đổi là nhiều chunk hơn đồng nghĩa tốn thêm chi phí embedding/lưu trữ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** __ / 42

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
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

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
