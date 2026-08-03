# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
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
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=200)` trên 3 tài liệu của `data/vinuni_course_registration/` (đã bỏ front matter bằng `ingest.parse_front_matter()` trước khi so sánh, nếu không sẽ đo luôn cả khối YAML):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| summer-2026-new-student-portal (2183 ký tự) | FixedSizeChunker (`fixed_size`) | 13 | 186.4 | Kém — cắt thuần theo số ký tự nên thường xẻ giữa câu hoặc giữa dòng heading (`## Class Status`), overlap 20 ký tự không đủ để bù ngữ cảnh mất đi. |
| summer-2026-new-student-portal (2183 ký tự) | SentenceChunker (`by_sentences`) | 9 | 240.0 | Trung bình — không cắt giữa câu, nhưng gộp câu theo số lượng cố định (3 câu/chunk) chứ không theo ranh giới heading, nên một chunk có thể lẫn câu cuối mục này với câu đầu mục sau. |
| summer-2026-new-student-portal (2183 ký tự) | RecursiveChunker (`recursive`) | 16 | 134.7 | Tốt nhất trong 3 — ưu tiên tách theo đoạn (`\n\n`) rồi mới xuống dòng/câu/từ, nên phần lớn chunk trùng khớp ranh giới đoạn văn tự nhiên của tài liệu. |
| undergraduate-academic-regulations (4767 ký tự) | FixedSizeChunker (`fixed_size`) | 27 | 195.8 | Kém — tài liệu quy định có nhiều mục đánh số, cắt cố định theo ký tự phá vỡ cấu trúc mục thường xuyên hơn ở tài liệu dài. |
| undergraduate-academic-regulations (4767 ký tự) | SentenceChunker (`by_sentences`) | 14 | 338.1 | Trung bình — câu trong văn bản quy định khá dài (338 ký tự/chunk trung bình dù chỉ 3 câu), chunk to nhưng vẫn có thể lẫn nội dung của hai điều khoản khác nhau. |
| undergraduate-academic-regulations (4767 ký tự) | RecursiveChunker (`recursive`) | 38 | 123.6 | Tốt hơn nhưng chunk nhỏ (123.6 ký tự) — đoạn văn dài vẫn bị hạ xuống tách theo câu/từ, không giữ được cả một điều khoản trong một chunk. Đây chính là ca `HeadingChunker` (tách theo `##`, giữ nguyên heading) được kỳ vọng làm tốt hơn. |
| registration-hub (2293 ký tự) | FixedSizeChunker (`fixed_size`) | 13 | 194.8 | Kém — tương tự các tài liệu khác, không nhận biết ranh giới ngữ nghĩa. |
| registration-hub (2293 ký tự) | SentenceChunker (`by_sentences`) | 14 | 162.2 | Trung bình — tài liệu này nhiều câu ngắn (danh sách bước đăng ký) nên chunk theo câu khá đều, nhưng vẫn không tôn trọng ranh giới mục. |
| registration-hub (2293 ký tự) | RecursiveChunker (`recursive`) | 18 | 125.8 | Tốt nhất trong 3 — bám theo đoạn/dòng, phù hợp với cấu trúc danh sách theo bước của tài liệu. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
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
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy (định nghĩa gốc: `benchmarks/vinuni_course_registration.json`, chạy qua `bench.py`).

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Starting in Summer 2026, which portal must students use for course registration, and what checks confirm that registration is complete? *(chỉ trả lời đúng khi lọc `metadata_filter={"audience": "student"}`)* | Starting with Summer 2026, course registration is conducted through the VinUniDigi Student Portal at one.vinuni.edu.vn/student. Students should select the correct term, verify prerequisites, class availability and timetable conflicts, click CONFIRM, ensure every course shows the status Registered, and preview the timetable. | doc_id: `summer-2026-new-student-portal` — mục "Access the Student Portal" + "Final Registration Checklist" |
| 2 | What was the Summer 2026 course registration period, and what was the final add/drop deadline? | The Summer 2026 course registration period ran from June 29 to July 4, 2026. The final add/drop deadline was July 11, 2026. | doc_id: `summer-2026-registration` |
| 3 | After the add/drop period, how is a course withdrawal recorded, by what point must it occur, and what is the program-wide withdrawal credit limit? | After add/drop, dropping a course is treated as a withdrawal and a W grade is recorded on the transcript. Withdrawal must occur before the student completes more than 30 percent of the course study time, and students may withdraw from at most 18 credits over the entire program. | doc_id: `undergraduate-academic-regulations`, `spring-2026-important-notes` |
| 4 | What do Full and Conflict mean during course registration, and what happens when prerequisite requirements have not been satisfied? | Full means that no seats are available. Conflict means that the class overlaps with another registered class. The system prevents registration when prerequisite or pre-study requirements have not been satisfied. | doc_id: `summer-2026-new-student-portal` (mục "Class Status" + "Prerequisite Requirements"), `registration-hub` |
| 5 | How should students request a course retake, audit or individual study, and how should they request withdrawal after the add/drop period? | Course retake, audit and individual study requests are submitted by email to the Registrar's Office. Withdrawal after the add/drop period is also requested by email and requires the course instructor's approval. | doc_id: `forms-and-petitions` |

**Ghi chú về câu hỏi #1 (yêu cầu lọc metadata):** đây là ca "không nêu rõ người hỏi là ai" — nếu không lọc `audience: student`, retrieval có thể trộn lẫn thông tin dành cho `faculty`/`staff` (nếu corpus có tài liệu cùng chủ đề nhưng khác đối tượng) và agent dễ trả lời sai nhóm người dùng.
> Không đổi 5 câu hỏi này sau khi một strategy đã chạy tốt hoặc xấu — mọi thành viên dùng chung bộ câu hỏi ở trên.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

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

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
