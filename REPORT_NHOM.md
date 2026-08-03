# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Balerion
**Thành viên:** Nguyễn Văn Đại, Trần Hoàng Vũ, Ngô Minh Phong, Nguyễn Thùy Trang
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> *Nhóm tập trung vào các chính sách tuyển sinh, quy chế học thuật, quy định học bổng và các mốc thời gian quan trọng áp dụng cho các chương trình đào tạo của VinUni năm 2026.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chính sách và quy định | https://registrar.vinuni.edu.vn/vi/ho... | 2026-08-03 / not-stated | 4,993 | audience, department, category, language |
| 2 | Tuyển sinh đại học VinUni năm 2026 - Hướng dẫn ứng tuyển | https://admissions.vinuni.edu.vn/vi/d... | 2026-08-03 / not-stated | 5,271 | audience, department, category, language |
| 3 | Các mốc quan trọng trong tuyển sinh đại học VinUni năm 2026 | https://admissions.vinuni.edu.vn/vi/d... | 2026-08-03 / not-stated | 3,860 | audience, department, category, language |
| 4 | Chương trình Thạc sĩ Khoa học Máy tính VinUni năm 2026 | https://admissions.vinuni.edu.vn/vi/t... | 2026-08-03 / not-stated | 2,438 | audience, department, category, language |
| 5 | Chương trình học bổng VinUni năm 2026 dành cho sinh viên đại học | https://admissions.vinuni.edu.vn/vi/h... | 2026-08-03 / not-stated | 3,674 | audience, department, category, language |
| 6 | Tuyển sinh chương trình Tiến sĩ VinUni năm 2026 | https://admissions.vinuni.edu.vn/vi/c... | 2026-08-03 / not-stated | 1,751 | audience, department, category, language |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| audience | chuỗi | "student" | Giúp lọc tài liệu nhắm đúng đối tượng người đọc (ví dụ: chỉ tìm thông tin cho sinh viên). |
| department | chuỗi | "admissions", "registrar" | Giúp giới hạn kết quả vào phòng ban quản lý vấn đề đó (như phòng tuyển sinh hay giáo vụ), tránh thông tin không liên quan. |
| category | chuỗi | "scholarships", "policies-regulation" | Phân loại nội dung tài liệu để hệ thống có thể ưu tiên tìm kiếm trong những nhóm chủ đề cụ thể một cách nhanh chóng. |
| language | chuỗi | "vi" | Cho phép hệ thống lọc tài liệu theo đúng ngôn ngữ người dùng đang hỏi, tránh nhầm lẫn. |

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
| 1 | Tất cả sinh viên đại học nhập học từ năm 2025 đến năm 2030 sẽ nhận được mức hỗ trợ học phí là bao nhiêu? | Tất cả sinh viên nhập học sẽ được hỗ trợ 35% học phí cho toàn bộ thời gian học tại trường. | undergraduate-scholarships-2026.md |
| 2 | Ứng viên nữ theo đuổi lĩnh vực khoa học công nghệ có thể nhận học bổng nào và trị giá bao nhiêu? | Ứng viên nữ có thể nhận Học bổng WIT (Women in Tech) trị giá 5% học phí. | undergraduate-scholarships-2026.md |
| 3 | Kỳ tuyển sinh sớm (Early Round) hệ đại học năm 2026 của VinUni diễn ra vào khoảng thời gian nào? | Kỳ Tuyển sinh Đợt 1 – Early Round diễn ra từ ngày 15/10/2025 đến 15/01/2026. | important-dates-2026.md |
| 4 | Sinh viên ứng tuyển vào kỳ Tuyển sinh sớm và tham gia VinUni Open Day sẽ nhận được đặc quyền tài chính gì? | Ứng viên nộp hồ sơ tại kỳ Tuyển sinh sớm và tham gia VinUni Open Day sẽ được miễn lệ phí tuyển sinh trị giá 2.000.000 VNĐ. | important-dates-2026.md |
| 5 | Chương trình Tiến sĩ tại VinUni tập trung nghiên cứu chuyên sâu vào những lĩnh vực trọng yếu nào? | Chương trình tập trung vào Trí tuệ nhân tạo, Khoa học máy tính, Công nghệ y sinh, và Kỹ thuật tiên tiến. | phd-admissions-2026.md |

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
