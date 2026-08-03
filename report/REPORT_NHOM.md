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

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu quy định mẫu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Quy định HP & Học phí | FixedSizeChunker (`fixed_size`) | 22 | 192.6 | Trung bình (cắt rách câu ở biên chunk) |
| Quy định HP & Học phí | SentenceChunker (`by_sentences`) | 11 | 344.8 | Khá (giữ nguyên vẹn từng câu) |
| Quy định HP & Học phí | RecursiveChunker (`recursive`) | 31 | 121.6 | Trung bình (chia nhỏ linh hoạt theo đoạn) |
| Quy định HP & Học phí | CustomSectionHeaderChunker | 8 | 480.2 | Rất tốt (giữ nguyên ngữ cảnh từng điều khoản) |

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
| Thành viên 1 | `SentenceChunker` | 9/10 | Giữ được cấu trúc câu hoàn chỉnh | Không phân biệt được ranh giới phần/mục lớn |
| Thành viên 2 | `RecursiveChunker` | 8/10 | Cắt nhỏ văn bản đều đặn | Chunk nhỏ (121 ký tự) làm xé lẻ ngữ cảnh tiêu đề |
| Thành viên 3 | `CustomSectionHeaderChunker` | 10/10 | Bảo tồn 100% ngữ cảnh điều khoản theo Header `##` | Section quá dài cần thêm sub-chunking phụ |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược tốt nhất là `CustomSectionHeaderChunker` kết hợp với Metadata Filtering. Vì văn bản quy định đại học mang tính pháp lý/thủ tục, từng điều khoản (Section) là một đơn vị thông tin hoàn chỉnh. Tách theo tiêu đề mục giúp Vector Embedding đại diện chính xác trọn vẹn ngữ nghĩa của quy định đó mà không bị nhiễu.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được xem là đạt học phần tiên quyết A để đăng ký học phần B khi đáp ứng điều kiện điểm số nào? | Sinh viên bắt buộc phải học và đạt điểm từ C (hoặc Pass) trở lên ở học phần A thì mới đủ điều kiện đăng ký học phần B. | `k3-prerequisites-policy` (Mục 1: Định nghĩa Học phần Tiên quyết) |
| 2 | Nếu xảy ra xung đột lịch học hoặc trùng lịch thi trên hệ thống SIS khi đăng ký học phần thì sinh viên cần xử lý như thế nào? | Hệ thống SIS sẽ tự động chặn đăng ký. Sinh viên cần chủ động chọn nhóm lớp khác hoặc gửi Ticket hỗ trợ cho Registrar Office trước hạn chót. | `k3-course-registration` (Mục 3: Xử lý sự cố trùng lịch) |
| 3 | Hậu quả gì sẽ xảy ra đối với sinh viên nếu chậm nộp học phí quá hạn quy định của nhà trường? | Sinh viên nợ học phí quá hạn sẽ bị tạm khóa tài khoản SIS Portal, không được tham gia thi kết thúc học phần và không được đăng ký học phần học kỳ tiếp theo. | `k3-tuition-policy` (Mục 3: Xử lý nợ học phí) |
| 4 | Theo hướng dẫn dành cho giảng viên, thời hạn tối đa để giảng viên hoàn tất nhập điểm thi kết thúc học phần là bao lâu? | Điểm thi kết thúc học phần phải được nhập hoàn tất trong vòng 7 ngày làm việc kể từ ngày thi. | `k3-faculty-grading-guide` (Mục 2: Quy định nhập điểm thành phần) [Filter: `audience: faculty`] |
| 5 | Sinh viên bình thường được đăng ký tối đa bao nhiêu tín chỉ và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính quy? | Sinh viên bình thường được đăng ký tối đa 24 tín chỉ / học kỳ và tối thiểu 12 tín chỉ / học kỳ (trừ học kỳ cuối). | `k3-course-registration` (Mục 2: Ràng buộc tín chỉ) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Điều kiện học phần tiên quyết | `CustomSectionHeaderChunker` | Có (Top-1) | Trả về trọn vẹn Mục 1 quy định tiên quyết |
| 2 | Trùng lịch đăng ký trên SIS | `CustomSectionHeaderChunker` | Có (Top-1) | Trả về chính xác quy trình gửi Ticket |
| 3 | Hậu quả nợ học phí quá hạn | `CustomSectionHeaderChunker` | Có (Top-1) | Trả về trọn vẹn Mục 3 xử lý nợ học phí |
| 4 | Thời hạn nhập điểm của giảng viên | `CustomSectionHeaderChunker` + Filter | Có (Top-1) | Khi có Filter `audience: faculty` trả về Top-1 100% |
| 5 | Ràng buộc tín chỉ học kỳ | `CustomSectionHeaderChunker` | Có (Top-1) | Trả về chính xác 24 max / 12 min tín chỉ |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Cực kỳ giúp ích ở Câu hỏi số 4! Khi chưa lọc metadata, tìm kiếm vector bị nhiễu bởi các từ khóa "học phần", "thời hạn" ở tài liệu sinh viên. Khi lọc trước theo `audience: faculty`, kết quả trả về chính xác 100% ở vị trí Top-1.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Cấu trúc dữ liệu quyết định chiến lược Chunking:** Văn bản quy định nên ưu tiên chunking theo Header/Section để tránh xé lẻ điều khoản.
2. **Metadata Pre-filtering nhân đôi chính xác:** Lọc đối tượng (`audience`) trước khi tìm kiếm vector giúp RAG Agent tránh nhầm lẫn nội dung giữa sinh viên và giảng viên.
3. **Chunk size quá nhỏ gây mất ngữ cảnh:** Chunking cố định size nhỏ (như 120 chars) làm mất liên kết giữa tiêu đề bài viết và nội dung.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ tài liệu nhưng chiến lược chunking khác nhau tạo ra sự chênh lệch rõ rệt về điểm truy xuất (từ 8/10 lên 10/10). Việc hiểu rõ đặc thụ cấu trúc văn bản đầu vào giúp thiết kế custom chunker tối ưu vượt trội so với các thuật toán cắt chuỗi thông thường.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thiết kế hệ thống metadata phong phú hơn nữa (bổ sung trường `chapter`, `effective_date`) và kết hợp với chiến lược Semantic Chunking (tách theo độ tương đồng ngữ nghĩa giữa các đoạn văn).

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
