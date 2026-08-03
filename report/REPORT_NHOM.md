# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K3 Day 07
**Thành viên:**
- Nguyễn Xuân Phượng - Nhóm trưởng - `2A202601874`
- Lê Nguyễn Minh Đức - Thành viên - `2A202601013`
- Nguyễn Đào Nam Hải - Thành viên - `2A202601037`
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân nộp riêng trong `REPORT_CANHAN_2A202601874.md` và các bản cá nhân tương ứng. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm:** 40 = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5)

---

## 1. Kết Quả Bước 1 - Chốt Đề Tài Và Phạm Vi Dữ Liệu

**Đề tài nhóm đã chốt:**

Đăng ký môn học và quy định học vụ cho sinh viên.

**Phạm vi cụ thể:**
- Quy trình đăng ký học phần
- Thêm / bỏ / rút học phần
- Điều kiện tiên quyết và ràng buộc học phần
- Lịch học và thời điểm mở đăng ký
- Quyền mượn và quy định sử dụng thư viện

**Lý do chọn đề tài:**
- Phù hợp đúng chủ đề K3: dịch vụ / quy định đại học
- Có thể tìm nguồn công khai, rõ ràng, truy vết được
- Dễ xây dựng benchmark queries kiểm chứng được
- Phù hợp để so sánh chunking và metadata filtering

---

## 2. Kết Quả Bước 2-4 - Thu Thập, Chuẩn Hóa Và Kiểm Kê Corpus

**Tổng quan corpus:**
- Thư mục dữ liệu: `data/k3_university/`
- Số tài liệu: 5 file `.md`
- File kiểm kê nguồn: `data/k3_university/sources.csv`

### Danh sách tài liệu

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Metadata chính |
|---|---|---|---|---|
| 1 | Hướng dẫn đăng ký học phần | https://registrar.vinuni.edu.vn/academics/class-schedule-course-registration/ | 2026-08-03 / 2026-08-03 | `audience: student`, `department: academic-affairs` |
| 2 | Quy định đăng ký, thêm, bỏ và rút học phần | https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergraduate-programs/ | 2026-08-03 / 2026-08-03 | `audience: student`, `department: registrar` |
| 3 | Quy trình lập lịch học và mở đăng ký | https://policy.vinuni.edu.vn/all-policies/university-academic-scheduling-procedures/ | 2026-08-03 / 2021-11-22 | `audience: staff`, `department: registrar` |
| 4 | Quyền mượn thư viện cho sinh viên bậc đại học | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ | 2026-08-03 / 2026-08-03 | `audience: student`, `department: library` |
| 5 | Quy định truy cập và sử dụng thư viện | https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/ | 2026-08-03 / 2026-08-03 | `audience: all`, `department: library` |

### Metadata schema

| Trường | Kiểu | Tác dụng |
|---|---|---|
| `doc_id` | `str` | Định danh duy nhất để truy vết và xóa |
| `title` | `str` | Hiển thị tên tài liệu |
| `audience` | `str` | Dùng cho metadata filtering |
| `department` | `str` | Phân biệt đơn vị ban hành |
| `language` | `str` | Lọc ngôn ngữ |
| `source_url` | `str` | Truy vết nguồn gốc |
| `retrieved_at` | `str` | Theo dõi ngày lấy |
| `document_version` | `str` | Theo dõi phiên bản / ngày hiệu lực |

**Kết luận Bước 2-4:**
- Corpus đã có 5 tài liệu đúng phạm vi
- Metadata đủ để dùng `search_with_filter()`
- Ít nhất 1 tài liệu có `audience: student` và 1 tài liệu có `audience: staff`, giúp benchmark filter tốt hơn

---

## 3. Kết Quả Bước 5 - Chốt 5 Câu Hỏi Benchmark

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? | Metadata filter gợi ý |
|---|---|---|---|---|
| 1 | Sinh viên đăng ký học phần ở hệ thống nào và cần kiểm tra gì sau khi hoàn tất? | Sinh viên đăng ký học phần trên SIS và sau khi hoàn tất cần kiểm tra lại trạng thái đăng ký trong thời khóa biểu cá nhân. | `vinuni-course-registration` | `audience: student` |
| 2 | Nếu một môn chưa hiển thị, có xung đột lịch hoặc báo lỗi tiên quyết, sinh viên cần làm gì? | Sinh viên cần kiểm tra điều kiện môn học và liên hệ Văn phòng Đăng ký nếu mình đủ điều kiện nhưng hệ thống vẫn chặn; các trường hợp đặc biệt phải gửi yêu cầu riêng theo hướng dẫn của Registrar. | `vinuni-course-registration` | `audience: student` |
| 3 | Đến ngày làm việc thứ mấy của học kỳ chính sinh viên còn được thêm học phần? | Sinh viên được phép thêm học phần chậm nhất đến hết ngày làm việc thứ 10 của học kỳ chính. | `vinuni-academic-regulations-add-drop` | `audience: student` |
| 4 | Sinh viên bậc đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn như thế nào? | Sinh viên bậc đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần; sách có thể được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và chưa có người khác đặt giữ. | `vinuni-library-borrowing-undergraduate` | `audience: student` |
| 5 | Quy định truy cập thư viện cho biết ai được vào thư viện và sử dụng tài nguyên điện tử? | Chỉ sinh viên, giảng viên và nhân viên có thẻ VinUni hợp lệ mới được vào thư viện, mượn tài liệu và sử dụng tài nguyên điện tử. | `vinuni-library-access-policy` | `audience: all` |

**Ghi chú:** Câu 2 nên ưu tiên dùng `metadata_filter={"audience": "student"}` để tránh lẫn với tài liệu `staff` trong corpus.

---

## 4. Trạng Thái Phần Tiếp Theo

- Bước 6: phân công chiến lược chunking cho từng thành viên
- Bước 7: chạy benchmark và đo retrieval quality
- Bước 8: phân tích kết quả / failure cases

> Các bước này sẽ được điền sau khi nhóm chạy retrieval trên corpus hiện tại.

