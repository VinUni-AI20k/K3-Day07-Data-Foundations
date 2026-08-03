# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Dịch vụ và quy định đăng ký học phần dành cho sinh viên HUST
**Thành viên:** 
1. Trần Việt Trường (Thành viên 1 - Custom Heading Chunker)
2. Hoàng Mạnh Dũng (Thành viên 2 - Recursive Chunker & Core Dev)
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học.

**Phạm vi cụ thể nhóm tập trung:**
> Nhóm tập trung thu thập 10 văn bản quy định, thông báo kế hoạch ĐKMH, học phí tín chỉ, xử lý lớp học phần đầy/không mở và quy trình đăng ký cho sinh viên SIE thuộc Đại học Bách khoa Hà Nội (HUST).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Kế hoạch học tập 2025-2026/2026-2027 | https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=27235 | 03/08/2026 / 2026-03 | 1,160 | `audience: student`, `department: dao-tao`, `category: class-registration` |
| 2 | Đăng ký lớp kỳ 2026.1 | https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240 | 03/08/2026 / 2026-07 | 1,095 | `audience: student`, `department: dao-tao`, `category: class-registration` |
| 3 | Đăng ký lớp kỳ hè 2025-2026 | https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29239 | 03/08/2026 / 2026-07 | 957 | `audience: student`, `department: dao-tao`, `category: class-registration` |
| 4 | Đăng ký bổ sung lớp Toán đã đầy | https://fami.hust.edu.vn/thong-bao-sinh-vien/thong-bao-dang-ky-bo-sung-cac-hoc-phan-mon-toan-ky-2025-2/ | 03/08/2026 / 2026-02-05 | 858 | `audience: student`, `department: fami`, `category: class-registration` |
| 5 | Học phí theo tín chỉ | https://www.hust.edu.vn/vi/sinh-vien/van-ban-quy-che/hoc-phi-383626.html | 03/08/2026 / 2019-03-28 | 787 | `audience: student`, `department: ke-toan`, `category: tuition` |
| 6 | Hướng dẫn đăng ký học tập SIE | https://soict.hust.edu.vn/huong-dan-dang-ky-hoc-tap-cho-sinh-vien-sie.html | 03/08/2026 / 2024-08-28 | 877 | `audience: sie-student`, `department: soict`, `category: sie-guidance` |
| 7 | Học phần thay thế SIE | https://soict.hust.edu.vn/huong-dan-sinh-vien-sie-dang-ky-hoc-phan-thay-the-ky-2024-2.html | 03/08/2026 / 2025-01-21 | 864 | `audience: sie-student`, `department: soict`, `category: sie-guidance` |
| 8 | Xử lý học phần không mở | https://fami.hust.edu.vn/thong-bao-sinh-vien/huong-dan-dang-ky-hoc-tap-cho-cac-hoc-phan-khong-mo-trong-hoc-ky-toi/ | 03/08/2026 / not-stated | 816 | `audience: student`, `department: fami`, `category: class-registration` |
| 9 | Hướng dẫn đăng ký lớp trên hệ thống | https://ctt.hust.edu.vn/Upload/.../HD%20DKHT-2026-V1_20251210.pdf | 03/08/2026 / 2025-12-10 | 822 | `audience: student`, `department: dao-tao`, `category: system-guide` |
| 10 | Quy chế đào tạo tín chỉ HUST | https://hust.edu.vn/uploads/sys/quality-assurance/.../quy-che-dao-tao-tin-chi2007.pdf | 03/08/2026 / 2007 | 876 | `audience: student`, `department: dao-tao`, `category: regulation` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu chỉ chứa trang/tài liệu công khai của HUST, không có dữ liệu cá nhân hoặc thông tin đăng nhập.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version`, `audience`, `department` và `category` trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | `string` | `student`, `sie-student` | Phân biệt đối tượng sinh viên đại trà và sinh viên chương trình hợp tác quốc tế (SIE) để lọc nhiễu hướng dẫn riêng. |
| `department` | `string` | `dao-tao`, `fami`, `soict` | Phân loại chính xác đơn vị phụ trách (Ban Đào tạo, Khoa Toán - Tin FAMI, Viện CNTT&TT SoICT). |
| `category` | `string` | `class-registration`, `tuition`, `sie-guidance` | Khoanh vùng mục đích quy trình để lọc pre-filtering nhanh chóng. |
| `source_url` | `string` | `https://ctt.hust.edu.vn/...` | Đảm bảo tính minh bạch và truy xuất nguồn gốc (provenance) của thông tin. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu `hust-credit-training-regulation.md`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Quy chế ĐKMH HUST | FixedSizeChunker (`fixed_size`) | 4 | 220.5 ký tự | Không hoàn toàn. Có đoạn bị cắt ngẫu nhiên giữa ranh giới. |
| Quy chế ĐKMH HUST | SentenceChunker (`by_sentences`) | 5 | 175.2 ký tự | Khá tốt. Tách chuẩn theo ranh giới câu. |
| Quy chế ĐKMH HUST | RecursiveChunker (`recursive`) | 4 | 218.8 ký tự | Rất tốt. Giữ trọn vẹn ngữ cảnh đoạn tiêu đề và danh sách điều khoản. |

### Chiến lược của từng thành viên

**Thành viên 1 — Trần Việt Trường**
- **Loại chiến lược:** Custom Heading/Section Chunker
- **Mô tả & lý do chọn:** Tách văn bản theo các tiêu đề `#`, `##` của các thông báo quy chế HUST, giữ toàn vẹn ngữ cảnh phần tiêu đề cho các chunk con bên dưới.

**Thành viên 2 — Hoàng Mạnh Dũng**
- **Loại chiến lược:** RecursiveChunker (với `chunk_size=400`, `separators=["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả & lý do chọn:** Áp dụng thuật toán chia đệ quy phân cấp từ đoạn đến câu. Giúp giữ mạch nội dung các điều khoản học phí và kế hoạch ĐKMH HUST.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Mạnh Dũng | RecursiveChunker (size=400) | 10 / 10 | Đơn giản, độ phủ ngữ cảnh tốt, truy xuất chính xác 5/5 query. | Đôi khi gom cả đoạn dài nếu không có phân cách `\n\n`. |
| Trần Việt Trường | Custom Heading Chunker | 9 / 10 | Giữ tiêu đề phần mục rất rõ ràng, thích hợp cho văn bản có `#`. | Cần xử lý bổ sung nếu văn bản không dùng tiêu đề Markdown. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược **RecursiveChunker** kết hợp linh hoạt với `metadata_filter` mang lại hiệu quả truy xuất tốt nhất cho bộ dữ liệu dịch vụ đào tạo HUST. Thuật toán giữ nguyên tính liên tục của các mốc thời gian ĐKMH và điều khoản học phí mà không bị cắt rách giữa chừng.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên bình thường và sinh viên bị cảnh báo học tập tại HUST được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ? | Sinh viên bình thường được đăng ký 12-24 tín chỉ (Elitech 12-28 TC). Sinh viên bị cảnh báo học tập chỉ được đăng ký tối đa 14 tín chỉ. | `hust-credit-training-regulation::chunk_0` |
| 2 | Các bước thao tác đăng ký lớp môn học trên hệ thống CTT HUST như thế nào? | Đăng nhập CTT -> Chọn mục Đăng ký lớp -> Nhập mã lớp kíp học -> Kiểm tra trùng thời khóa biểu -> Bấm Đăng ký. | `hust-course-registration-system-guide::chunk_0` |
| 3 | Hạn nộp học phí tín chỉ HUST và quy định xử lý khi chậm nộp học phí ra sao? | Hạn nộp học phí thông báo theo từng kỳ. Chậm nộp học phí bị hệ thống tự động hủy đăng ký lớp và khóa quyền đăng ký kỳ tiếp theo. | `hust-tuition-by-credits::chunk_0` |
| 4 | Thời gian đăng ký kế hoạch học tập kỳ 1 năm học 2026-2027 và kỳ hè 2025-2026 thực hiện vào lúc nào? | Đăng ký kế hoạch học tập kỳ hè 2025-2026 và kỳ 1 2026-2027 thực hiện đợt từ tháng 3/2026 theo thông báo CTT 27235. | `hust-study-plan-2026::chunk_0` |
| 5 | Sinh viên chương trình hợp tác quốc tế (SIE) có quy định gì riêng khi đăng ký học phần thay thế? (Filter `audience: sie-student`) | Sinh viên SIE đăng ký học phần thay thế theo hướng dẫn riêng của SoICT HUST, áp dụng cho các học phần không mở hoặc trùng lịch. | `hust-sie-course-substitution::chunk_0` |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Giới hạn tín chỉ ĐKMH HUST | RecursiveChunker | Có (Top-1) | Đạt 2/2 điểm |
| 2 | Các bước đăng ký CTT | RecursiveChunker / Heading | Có (Top-1) | Đạt 2/2 điểm |
| 3 | Học phí tín chỉ & Chế tài | RecursiveChunker | Có (Top-1) | Đạt 2/2 điểm |
| 4 | Đăng ký kế hoạch 20261 | RecursiveChunker | Có (Top-1) | Đạt 2/2 điểm |
| 5 | Học phần thay thế SIE | RecursiveChunker + Metadata Filter | Có (Top-1) | Đạt 2/2 điểm — Lọc sạch 100% tài liệu đại trà |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc bằng metadata phát huy hiệu quả tuyệt đối ở **Câu hỏi 5** với `metadata_filter={"audience": "sie-student"}`. Nếu không có bộ lọc, các câu hỏi tra cứu cho sinh viên SIE dễ bị nhầm lẫn với thông báo đăng ký chung. Metadata filter giúp loại bỏ toàn bộ 8 tài liệu sinh viên chuẩn, giữ lại đúng 2 tài liệu dành riêng cho sinh viên SIE.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Quản trị dữ liệu chuẩn:** Lưu nguồn gốc trong `sources.csv` và gán metadata `audience`, `department` ngay từ bước nạp dữ liệu giúp giải quyết triệt để bài toán nhiễu thông tin giữa các hệ đào tạo (Chuẩn vs SIE).
2. **Ưu thế của Recursive Chunking:** Giúp giữ nguyên các đoạn văn bản chứa thời gian hạn định ĐKMH HUST mà không bị xé nhỏ ranh giới.
3. **Ý nghĩa của Metadata Pre-filtering:** Lọc trước (pre-filter) giúp thu hẹp phạm vi không gian vector trước khi tính cosine similarity, tăng tốc độ và độ chính xác đáng kể.

**Bài học rút ra khi so sánh trong nhóm:**
> Nhóm nhận thấy việc kết hợp giữa dữ liệu thực tế chất lượng, metadata có cấu trúc rõ ràng và chiến lược chia nhỏ đệ quy chính là công thức tối ưu cho bài toán RAG truy xuất dịch vụ đại học.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chuẩn hóa thêm trường `semester` (ví dụ `20261`, `20253`) cho tất cả các thông báo để hỗ trợ tìm kiếm chính xác theo từng đợt ĐKMH trong năm học.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
