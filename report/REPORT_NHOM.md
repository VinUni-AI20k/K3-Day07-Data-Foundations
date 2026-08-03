# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN_2A202601874.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Đăng ký học phần, quy định học phần tiên quyết/song hành, rút học phần, mức đóng học phí và hướng dẫn nhập điểm dành cho giảng viên (VinUniversity).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định và Quy trình Đăng ký Học phần | https://registrar.vinuni.edu.vn/academics/class-schedule-course-registration/ | 2026-08-03 / 2026.1 | 1,668 | `audience: student`, `category: course-registration` |
| 2 | Quy định về Học phần Tiên quyết và Song hành | https://policy.vinuni.edu.vn/academic-regulations/ | 2026-08-03 / 2026.1 | 1,602 | `audience: student`, `category: academic-rules` |
| 3 | Quy trình Rút bớt Học phần và Hủy Đăng ký Môn | https://registrar.vinuni.edu.vn/academics/course-add-drop-withdrawal/ | 2026-08-03 / 2026.1 | 1,588 | `audience: student`, `category: course-withdrawal` |
| 4 | Quy định về Thời hạn và Mức đóng Học phí | https://policy.vinuni.edu.vn/financial-regulations/ | 2026-08-03 / 2026.1 | 1,516 | `audience: student`, `category: tuition-fee` |
| 5 | Tiêu chuẩn và Quy trình Xét Học bổng | https://vinuni.edu.vn/admission/scholarships-and-financial-aid/ | 2026-08-03 / 2026.1 | 1,464 | `audience: student`, `category: scholarship` |
| 6 | Hướng dẫn Duyệt Lớp và Nhập Điểm cho Giảng viên | https://registrar.vinuni.edu.vn/faculty/grading-guidelines/ | 2026-08-03 / 2026.1 | 1,367 | `audience: faculty`, `category: grading-policy` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `k3-course-registration` | Định danh duy nhất từng tài liệu, dùng để xóa/truy vết nguồn gốc |
| `title` | `str` | `Quy định và Quy trình Đăng ký Học phần` | Lưu tên tiêu đề chính thức của tài liệu |
| `audience` | `str` | `student` / `faculty` | Phân loại đối tượng áp dụng (sinh viên hay giảng viên), giúp lọc metadata hiệu quả |
| `category` | `str` | `tuition-fee` / `course-registration` | Phân loại chủ đề tài liệu để lọc trước khi tìm kiếm vector (pre-filtering) |
| `department` | `str` | `academic-affairs` / `financial-affairs` | Đơn vị chủ quản ban hành văn bản |
| `source_url` | `str` | `https://registrar.vinuni.edu.vn/...` | Đường dẫn truy xuất nguồn gốc công khai |
| `retrieved_at` | `str` | `2026-08-03` | Kiểm soát ngày lấy dữ liệu |
| `document_version` | `str` | `2026.1` | Quản lý phiên bản hiệu lực của văn bản |

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

**Thành viên 1 — Nguyễn Xuân Phương (2A202601874 - Nhóm trưởng)**
- **Loại chiến lược:** `SentenceChunker`
- **Mô tả & lý do chọn:** Tách văn bản dựa theo ranh giới dấu câu (`. `, `! `, `? `) với nhóm `max_sentences_per_chunk=3`. Lý do chọn là vì văn bản quy định có các câu ngắn gọn chứa trọn vẹn thông báo.

**Thành viên 2 — Đào Văn B (Phụ trách Data)**
- **Loại chiến lược:** `RecursiveChunker`
- **Mô tả & lý do chọn:** Chia nhỏ đệ quy theo danh sách phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]` với `chunk_size=400`. Lý do chọn giúp duy trì linh hoạt ranh giới đoạn và dòng mà không làm rách câu.

**Thành viên 3 — Nguyễn Đào Nam Hải (2A202601037 - Phụ trách Retrieval & Benchmark)**
- **Loại chiến lược:** `CustomSectionHeaderChunker` (Custom Chunker)
- **Mô tả & lý do chọn:** Tách văn bản dựa trên các tiêu đề Markdown (`#` và `##`). Văn bản quy định đại học luôn có cấu trúc tiêu đề từng điều khoản rõ ràng, việc tách theo Header giúp giữ trọn vẹn 1 điều khoản trong 1 chunk duy nhất, tránh cắt đứt ngữ cảnh.
- **Code snippet (nếu custom):**
```python
import re

class CustomSectionHeaderChunker:
    def __init__(self, max_chunk_size: int = 600) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []
        pattern = r'(?=\n##?\s+)'
        sections = re.split(pattern, text)
        chunks = []
        for sec in sections:
            sec_str = sec.strip()
            if sec_str:
                chunks.append(sec_str)
        return chunks
```

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
| 1 | Sinh viên được xem là đạt học phần tiên quyết A để đăng ký học phần B khi đáp ứng điều kiện điểm số nào? | Sinh viên bắt buộc phải học và đạt điểm từ C (hoặc Pass) trở lên ở học phần A thì mới đủ điều kiện đăng ký học phần B. | `k3-prerequisites-policy` (Mục 1: Định nghĩa Học phần Tiên quyết) |
| 2 | Nếu xảy ra xung đột lịch học hoặc trùng lịch thi trên hệ thống SIS khi đăng ký học phần thì sinh viên cần xử lý như thế nào? | Hệ thống SIS sẽ tự động chặn đăng ký. Sinh viên cần chủ động chọn nhóm lớp khác hoặc gửi Ticket hỗ trợ cho Registrar Office trước hạn chót. | `k3-course-registration` (Mục 3: Xử lý sự cố trùng lịch) |
| 3 | Hậu quả gì sẽ xảy ra đối với sinh viên nếu chậm nộp học phí quá hạn quy định của nhà trường? | Sinh viên nợ học phí quá hạn sẽ bị tạm khóa tài khoản SIS Portal, không được tham gia thi kết thúc học phần và không được đăng ký học phần học kỳ tiếp theo. | `k3-tuition-policy` (Mục 3: Xử lý nợ học phí) |
| 4 | Theo hướng dẫn dành cho giảng viên, thời hạn tối đa để giảng viên hoàn tất nhập điểm thi kết thúc học phần là bao lâu? | Điểm thi kết thúc học phần phải được nhập hoàn tất trong vòng 7 ngày làm việc kể từ ngày thi. | `k3-faculty-grading-guide` (Mục 2: Quy định nhập điểm thành phần) [Filter: `audience: faculty`] |
| 5 | Sinh viên bình thường được đăng ký tối đa bao nhiêu tín chỉ và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính quy? | Sinh viên bình thường được đăng ký tối đa 24 tín chỉ / học kỳ và tối thiểu 12 tín chỉ / học kỳ (trừ học kỳ cuối). | `k3-course-registration` (Mục 2: Ràng buộc tín chỉ) |

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
