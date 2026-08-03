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
> Các dịch vụ và quy định hỗ trợ sinh viên VinUniversity trong học tập, sức khỏe, nghề nghiệp, tài chính và đời sống ký túc xá.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Dịch vụ mượn tài liệu và thiết bị tại Thư viện VinUniversity | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ | 2026-08-03 / `not-stated` | 1.358 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 2 | Dịch vụ hỗ trợ học tập của Thư viện VinUniversity | https://library.vinuni.edu.vn/services/learning-services/ | 2026-08-03 / `not-stated` | 964 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 3 | Dịch vụ sức khỏe thể chất và tinh thần tại VinUniversity | https://vinuni.edu.vn/vinuni-wellbeing-services/ | 2026-08-03 / `not-stated` | 1.100 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 4 | Dịch vụ phát triển nghề nghiệp tại VinUniversity | https://vinuni.edu.vn/aid/career-services/ | 2026-08-03 / `not-stated` | 1.045 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 5 | Quy trình yêu cầu hỗ trợ tài chính cho sinh viên VinUniversity | https://policy.vinuni.edu.vn/all-policies/guidelines-for-student-financial-support-request/ | 2026-08-03 / `GDL-FAO-001-V2.0` (2025-04-22) | 1.671 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 6 | Tiêu chí duy trì học bổng đầu vào và hỗ trợ tài chính tại VinUniversity | https://policy.vinuni.edu.vn/all-policies/criteria-to-maintain-the-entry-scholarship-and-financial-aid-support/ | 2026-08-03 / `GDL-SAM-004-V2.1` (2025-09-04) | 1.274 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 7 | Phòng ở và tiện ích ký túc xá VinUniversity | https://vinuni.edu.vn/student_life/residential-life/dormitory-room/ | 2026-08-03 / `not-stated` | 1.034 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 8 | Quyền tiếp cận dịch vụ hỗ trợ theo Bộ quy tắc sinh viên VinUniversity | https://policy.vinuni.edu.vn/all-policies/student-affairs-regulations-code-of-conduct/ | 2026-08-03 / `VU_CTSV02.EN V5.0` (2025-12-24) | 1.610 | `audience`, `department`, `category`, `language`, `source_language`, `content_form` |

*Số ký tự được tính trên phần nội dung sau YAML front matter, tức phần thực tế được `ingest.py` đưa vào chunker.*

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `vinuni-financial-aid-request` | Định danh ổn định cho tài liệu và liên kết mọi chunk về đúng nguồn. |
| `title` | string | `Quy trình yêu cầu hỗ trợ tài chính cho sinh viên VinUniversity` | Tăng tín hiệu ngữ nghĩa và giúp hiển thị tên nguồn trong kết quả. |
| `source_url` | URL string | `https://policy.vinuni.edu.vn/...` | Cho phép truy vết và kiểm chứng câu trả lời tại nguồn chính thức. |
| `retrieved_at` | ISO date string (`YYYY-MM-DD`) | `2026-08-03` | Hỗ trợ đánh giá độ mới của dữ liệu đã thu thập và tương thích với metadata store. |
| `document_version` | string | `GDL-FAO-001-V2.0 (2025-04-22)` | Phân biệt phiên bản chính sách; dùng `not-stated` khi trang không công bố phiên bản. |
| `audience` | enum-like string | `undergraduate-student` | Lọc nội dung theo nhóm người học phù hợp. |
| `department` | enum-like string | `financial-aid-office` | Thu hẹp tìm kiếm về đúng đơn vị cung cấp dịch vụ hoặc ban hành quy định. |
| `category` | enum-like string | `financial-aid` | Lọc theo loại nhu cầu như thư viện, sức khỏe, nghề nghiệp, tài chính hoặc ký túc xá. |
| `language` | string | `vi` | Chọn nội dung phù hợp với ngôn ngữ câu hỏi. |
| `source_language` | string | `en` | Cho biết ngôn ngữ của nguồn gốc để kiểm tra bản tóm lược tiếng Việt. |
| `content_form` | string | `translated-summary` | Phân biệt nội dung tóm lược có dịch với bản chép nguyên văn. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

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

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

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
