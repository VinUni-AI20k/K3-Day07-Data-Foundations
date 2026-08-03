# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Dịch vụ và quy định đăng ký học phần dành cho sinh viên HUST
**Thành viên:** 

1. Hoàng Mạnh Dũng (Trưởng nhóm - Data & Core Dev)
2. Nguyễn Văn An (Benchmark Owner)
3. Trần Thị Bình (Demo & Strategy Analyst)
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học.

**Phạm vi cụ thể nhóm tập trung:**
> Nhóm tập trung thu thập toàn bộ các văn bản quy định, quy chế thang điểm, hướng dẫn thao tác CTT, nghĩa vụ học phí và quy trình Cố vấn học tập phê duyệt đăng ký học phần thuộc Đại học Bách khoa Hà Nội (HUST).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định đăng ký học phần tín chỉ HUST | https://ctt.hust.edu.vn/quy-dinh-dang-ky-hoc-phan | 2026-08-03 / QĐ-2025/QĐ-ĐHBKHN | 1,947 | `audience: student`, `department: ban-dao-tao`, `category: quy-dinh-hoc-vu` |
| 2 | Hướng dẫn thao tác đăng ký môn học Cổng CTT | https://ctt-daotao.hust.edu.vn/huong-dan-dkhp | 2026-08-03 / 2025-2026 | 1,597 | `audience: student`, `department: trung-tam-mta`, `category: huong-dan-su-dung` |
| 3 | Quy định môn tiên quyết T & học cải thiện | https://ctt.hust.edu.vn/quy-dinh-tien-quyet-hoc-lai | 2026-08-03 / QĐ-2024/QĐ-ĐHBKHN | 1,908 | `audience: student`, `department: ban-dao-tao`, `category: quy-dinh-hoc-vu` |
| 4 | Quy định nghĩa vụ học phí & rút học phần | https://ctt.hust.edu.vn/quy-dinh-hoc-phi-tin-chi | 2026-08-03 / 2025-2026 | 1,811 | `audience: student`, `department: ban-tai-chinh-ke-toan`, `category: hoc-phi` |
| 5 | Quy chế thang điểm & tính CPA/GPA | https://ctt.hust.edu.vn/quy-che-thang-diem-gpa-cpa | 2026-08-03 / QĐ-1550/QĐ-ĐHBKHN | 1,588 | `audience: student`, `department: ban-dao-tao`, `category: quy-dinh-hoc-vu` |
| 6 | Quy trình Cố vấn học tập phê duyệt ĐKMH | https://ctt.hust.edu.vn/quy-trinh-co-van-hoc-tap-phe-duyet | 2026-08-03 / 2025-2026 | 1,772 | `audience: faculty`, `department: ban-dao-tao`, `category: huong-dan-giang-vien` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | `string` | `student` / `faculty` | Lọc chính xác đối tượng xem quy định (sinh viên hay cố vấn học tập/giảng viên), loại bỏ nhiễu từ các văn bản hành chính dành cho cán bộ. |
| `department` | `string` | `ban-dao-tao`, `ban-tai-chinh-ke-toan`, `trung-tam-mta` | Khoanh vùng chính xác đơn vị phụ trách nội dung (ví dụ học phí do Ban Tài chính - Kế toán xử lý, hệ thống CTT do Trung tâm MTA). |
| `category` | `string` | `quy-dinh-hoc-vu`, `hoc-phi`, `huong-dan-su-dung` | Phân loại chủ đề tài liệu để lọc pre-filtering nhanh trước khi chạy tìm kiếm cosine similarity. |
| `source_url` | `string` | `https://ctt.hust.edu.vn/...` | Đảm bảo tính minh bạch và truy xuất nguồn gốc (provenance) của thông tin. |
| `document_version` | `string` | `QĐ-2025/QĐ-ĐHBKHN` | Đảm bảo truy vấn lấy đúng phiên bản văn bản quy định hiệu lực mới nhất. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên tài liệu `hust-quy-dinh-dang-ky-hoc-phan.md`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Quy định ĐKMH HUST | FixedSizeChunker (`fixed_size`) | 5 | 240.2 ký tự | Không hoàn toàn. Có đoạn bị ngắt giữa chừng ở ranh giới 300 ký tự. |
| Quy định ĐKMH HUST | SentenceChunker (`by_sentences`) | 6 | 198.8 ký tự | Khá tốt. Tách chuẩn theo ranh giới câu nhưng đôi khi gộp câu không liên quan vào 1 chunk. |
| Quy định ĐKMH HUST | RecursiveChunker (`recursive`) | 6 | 198.8 ký tự | Rất tốt. Giữ trọn vẹn các phần mục (`## 1.`, `## 2.`) và đoạn văn logic. |

### Chiến lược của từng thành viên

**Thành viên 1 — Hoàng Mạnh Dũng**
- **Loại chiến lược:** RecursiveChunker (với `chunk_size=400`, `separators=["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả & lý do chọn cho chủ đề này:** Ưu tiên giữ toàn vẹn cấu trúc tiêu đề mục và các điều khoản trong văn bản quy chế HUST. Tránh việc cắt ngang giữa câu quy định số tín chỉ tối thiểu/tối đa.

**Thành viên 2 — Nguyễn Văn An**
- **Loại chiến lược:** SentenceChunker (với `max_sentences_per_chunk=2`)
- **Mô tả & lý do chọn:** Tập trung nhóm theo các đơn vị câu hoàn chỉnh. Lý do là các quy định học vụ thường phát biểu súc tích trong 1-2 câu ngắn.

**Thành viên 3 — Trần Thị Bình**
- **Loại chiến lược:** FixedSizeChunker (với `chunk_size=300`, `overlap=50`)
- **Mô tả & lý do chọn:** Sử dụng FixedSizeChunker với overlap 50 ký tự làm đường cơ sở có độ phủ ngữ cảnh đệm giữa các ranh giới.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Mạnh Dũng | RecursiveChunker (size=400) | 10 / 10 | Bắt trọn vẹn danh sách điều khoản, bảo toàn tiêu đề mục và thứ tự logic. | Số lượng chunk ít hơn nhưng kích thước chunk lớn hơn. |
| Nguyễn Văn An | SentenceChunker (max_sentences=2) | 8 / 10 | Chunk gọn, chính xác khi query đúng từ khóa ngắn trong câu. | Có thể bị mất liên kết giữa tiêu đề mục lớn và câu chi tiết bên dưới. |
| Trần Thị Bình | FixedSizeChunker (size=300, overlap=50) | 7 / 10 | Đơn giản, tốc độ xử lý nhanh, không bị bỏ sót ký tự. | Cắt ngẫu nhiên không theo ranh giới câu làm giảm độ mạch lạc ngữ nghĩa. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược **RecursiveChunker** là tốt nhất cho bộ tài liệu quy định đăng ký học phần HUST. Văn bản quy chế Bách Khoa được trình bày theo cấu trúc phân cấp tiêu đề (`#`, `##`, `-`) và điều khoản rõ ràng. RecursiveChunker tách theo đoạn (`\n\n`) trước tiên nên giữ trọn vẹn ngữ cảnh của từng điều khoản mà không làm xé lẻ thông tin.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên bình thường và sinh viên bị cảnh báo học tập tại HUST được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ? | Sinh viên bình thường được đăng ký 12-24 tín chỉ; sinh viên bị cảnh báo học tập mức 1/2 chỉ được đăng ký 10-14 tín chỉ. | `hust-quy-dinh-dang-ky-hoc-phan::chunk_0` |
| 2 | Các bước thao tác đăng ký môn học trên cổng CTT HUST (ctt.hust.edu.vn) như thế nào? | Đăng nhập email HUST -> Chọn học kỳ tác nghiệp -> Nhập mã LHP -> Kiểm tra kíp học trùng lịch -> Bấm Đăng ký và lưu phiếu. | `hust-huong-dan-thao-tac-ctt::chunk_1` |
| 3 | Học phần tiên quyết ký hiệu T tại HUST là gì và điều kiện để đăng ký học cải thiện điểm? | Môn T yêu cầu đã học và đạt điểm D trở lên ở môn trước. Học cải thiện áp dụng cho môn đạt điểm D, D+, C, C+ (bị điểm F phải học lại). | `hust-dieu-kien-tien-quyet-hoc-lai::chunk_0` |
| 4 | Thời hạn nộp học phí tín chỉ HUST và chính sách hoàn tiền khi rút học phần trong tuần 1 của học kỳ ra sao? | Hạn nộp học phí từ tuần 5 đến tuần 7. Rút học phần trong tuần 1 của học kỳ được hoàn 100% học phí (tuần 2-4 rút không hoàn tiền). | `hust-quy-dinh-hoc-phi-dang-ky::chunk_1` |
| 5 | Cố vấn học tập Bách Khoa có trách nhiệm gì trong việc phê duyệt đơn đăng ký vượt tải cho sinh viên? (Lọc filter `audience: faculty`) | Cố vấn học tập (dành cho giảng viên) duyệt đơn đăng ký vượt tải (trên 24 tín chỉ) cho sinh viên CPA >= 3.2 hoặc duyệt học dưới tải. | `hust-quy-trinh-co-van-hoc-tap-duyet::chunk_0` |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Giới hạn tín chỉ ĐKMH | RecursiveChunker | Có (Top-1) | Đạt 2/2 điểm |
| 2 | Các bước đăng ký portal CTT | RecursiveChunker / Sentence | Có (Top-1) | Đạt 2/2 điểm |
| 3 | Môn tiên quyết T & học cải thiện | RecursiveChunker | Có (Top-1) | Đạt 2/2 điểm |
| 4 | Học phí & hoàn phí rút môn | RecursiveChunker | Có (Top-1) | Đạt 2/2 điểm |
| 5 | Trách nhiệm Cố vấn học tập | RecursiveChunker + Metadata Filter | Có (Top-1) | Đạt 2/2 điểm — Lọc sạch 100% tài liệu dành cho sinh viên |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc bằng metadata phát huy hiệu quả tuyệt đối ở **Câu hỏi 5** khi sử dụng `metadata_filter={"audience": "faculty"}`. Do câu hỏi đề cập đến "phê duyệt đơn đăng ký vượt tải", nếu không dùng filter hệ thống có thể truy xuất các đoạn hướng dẫn của sinh viên (`audience: student`). Nhờ có metadata filter, hệ thống loại bỏ hoàn toàn 5 tài liệu dành cho sinh viên và trả về chính xác 100% tài liệu hướng dẫn dành riêng cho Giảng viên / Cố vấn học tập.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Cấu trúc văn bản quyết định chiến lược chunking:** Với văn bản pháp lý/quy chế Bách Khoa, `RecursiveChunker` vượt trội hơn hẳn `FixedSizeChunker` nhờ tôn trọng ranh giới phân cấp tiêu đề.
2. **Sức mạnh của Metadata Pre-filtering:** Metadata `audience` và `department` giúp triệt tiêu nhiễu ngữ nghĩa (cross-domain noise) trước khi tính toán cosine similarity.
3. **Sự khác biệt giữa Mock vs Real Embeddings:** Mock embedder chỉ phù hợp cho unit test kiểm thử logic code; để đánh giá chất lượng retrieval ngữ nghĩa tiếng Việt bắt buộc phải dùng mô hình nhúng đa ngôn ngữ như `paraphrase-multilingual-MiniLM-L12-v2`.

**Bài học rút ra khi so sánh trong nhóm:**
> Việc thử nghiệm nhiều chiến lược chunking trên cùng một corpus dữ liệu thật giúp nhóm nhận ra không có một tham số cố định nào hoàn hảo cho mọi tài liệu. Việc kết hợp chunking theo đoạn logic với metadata chi tiết chính là chìa khóa để xây dựng hệ thống RAG đạt độ chính xác cao.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm các trường metadata chi tiết hơn như `academic_year` (năm học) và `program_type` (chuẩn, ELITECH, SIE) để hỗ trợ bộ lọc truy xuất phức tạp hơn cho hệ thống tư vấn học vụ tự động HUST.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
