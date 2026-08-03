# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [DMX]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**

> *1 câu — ví dụ: thư viện + đăng ký môn học.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
| - | --------------- | ------------------- | ------------------------ | ----------- | ------------------ |
| 1 |                 |                     |                          |             |                    |
| 2 |                 |                     |                          |             |                    |
| 3 |                 |                     |                          |             |                    |
| 4 |                 |                     |                          |             |                    |
| 5 |                 |                     |                          |             |                    |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
| ----------------- | ----- | ----------------- | ---------------------------------------------- |
|                   |       |                   |                                                |
|                   |       |                   |                                                |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy)           | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
| ---------- | ---------------------------------- | ----------------- | --------------------- | ------------------------------- |
| Toàn bộ corpus K3 (9 tài liệu) | FixedSizeChunker (`fixed_size`) | 194 | 196.4 | Một phần; kích thước ổn định nhưng có thể cắt giữa câu hoặc giữa câu hỏi và câu trả lời. |
| Toàn bộ corpus K3 (9 tài liệu) | ChunkByHeader (`by_header`) | 53 | 717.2 | Tốt hơn; giữ heading và nội dung theo từng mục, nhưng một số section quá dài. |
|            | SentenceChunker (`by_sentences`) |                   |                       |                                 |
|            | RecursiveChunker (`recursive`)   |                   |                       |                                 |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Vũ Tú Quỳnh**

- **Loại chiến lược:** Fixed Size và Chunk By Header
- **Mô tả & lý do chọn cho chủ đề này:**
  - **Fixed Size:** Chia văn bản thành các chunk có kích thước cố định 200 ký tự, không overlap. Chiến lược này dễ triển khai, tạo các chunk đồng đều và phù hợp để kiểm soát kích thước đầu vào cho embedding. Tuy nhiên, ranh giới cắt có thể nằm giữa câu hỏi, câu trả lời hoặc một ý đang diễn đạt.
  - **Chunk By Header:** Chia tài liệu Markdown tại các heading từ `#` đến `######` và giữ heading ở đầu mỗi chunk. Cách này phù hợp với bộ dữ liệu quy định đại học vì tài liệu có cấu trúc theo các mục như học phí, học bổng, đăng ký môn học và thư viện; nhờ vậy chunk giữ được ngữ cảnh và dễ truy vết chủ đề hơn.
- **Kết quả chạy thử trên corpus:** Với 9 tài liệu trong `data/k3_university`, Fixed Size tạo 194 chunk, độ dài trung bình 196.4 ký tự/chunk. Chunk By Header tạo 53 chunk, độ dài trung bình 717.2 ký tự/chunk; chunk dài nhất vượt 6,000 ký tự ở tài liệu có ít heading.
- **Nhận xét:** Fixed Size có kích thước ổn định và thuận lợi cho embedding nhưng có thể làm mất ngữ cảnh do cắt giữa ý. Chunk By Header bảo toàn cấu trúc tốt hơn nhưng kích thước không đồng đều, một số section quá dài có thể làm loãng kết quả tìm kiếm. Phương án phù hợp nhất là tách theo header trước, sau đó tiếp tục chia các section quá dài bằng Fixed Size hoặc Recursive Chunking.
- **Code snippet (nếu custom):**

```python
from src.chunking import FixedSizeChunker, HeaderChunker

fixed_chunks = FixedSizeChunker(chunk_size=200, overlap=0).chunk(text)
header_chunks = HeaderChunker().chunk(text)
```

**Thành viên 2 — [Tên]**

- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**

- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
| ------------ | ------------------------ | ----------------------- | ------------ | ----------- |
|              |                          |                         |              |             |
|              |                          |                         |              |             |
|              |                          |                         |              |             |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
| - | ----------------- | ----------------------------------- | ---------------------------- |
| 1 |                   |                                     |                              |
| 2 |                   |                                     |                              |
| 3 |                   |                                     |                              |
| 4 |                   |                                     |                              |
| 5 |                   |                                     |                              |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
| - | --------- | -------------------------------------- | --------------------------------- | -------- |
| 1 |           |                                        |                                   |          |
| 2 |           |                                        |                                   |          |
| 3 |           |                                        |                                   |          |
| 4 |           |                                        |                                   |          |
| 5 |           |                                        |                                   |          |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**

> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                   | Điểm tự đánh giá |
| -------------------------------------------- | ---------------------- |
| Lựa chọn tài liệu (Document Set Quality) | / 10                   |
| Thiết kế chiến lược (Strategy Design)   | / 15                   |
| Chất lượng truy xuất (Retrieval Quality) | / 10                   |
| Thuyết trình (Demo)                        | / 5                    |
| **Tổng phần nhóm**                  | **/ 40**         |

