# Bước 2: Thu Thập & Chuẩn Hóa Dữ Liệu Corpus (K3 University Services)

Tài liệu này tổng hợp toàn bộ kết quả thực hiện của **Thành viên 2** ở Bước 2 để các thành viên trong nhóm tham chiếu khi triển khai Bước 3 và Bước 4.

---

## 1. Tổng quan Bộ Tài Liệu (Corpus Data)

- **Chủ đề K3:** Dịch vụ & Quy định Đại học (VinUniversity).
- **Thư mục lưu trữ:** `data/k3_university/`
- **File kiểm kê nguồn:** `data/k3_university/sources.csv`
- **Số lượng tài liệu:** 6 tài liệu `.md` (đạt yêu cầu 5–10 tài liệu của bài Lab).

---

## 2. Danh Sách Tài Liệu & Đường Dẫn Nguồn (Data Inventory)

| # | File Path | Title | doc_id | Audience | Source URL |
|---|-----------|-------|--------|----------|------------|
| 1 | `data/k3_university/course-registration.md` | Quy định và Quy trình Đăng ký Học phần | `k3-course-registration` | `student` | https://registrar.vinuni.edu.vn/academics/class-schedule-course-registration/ |
| 2 | `data/k3_university/prerequisites-policy.md` | Quy định về Học phần Tiên quyết và Song hành | `k3-prerequisites-policy` | `student` | https://policy.vinuni.edu.vn/academic-regulations/ |
| 3 | `data/k3_university/course-withdrawal.md` | Quy trình Rút bớt Học phần và Hủy Đăng ký Môn học | `k3-course-withdrawal` | `student` | https://registrar.vinuni.edu.vn/academics/course-add-drop-withdrawal/ |
| 4 | `data/k3_university/tuition-policy.md` | Quy định về Thời hạn và Mức đóng Học phí Học kỳ | `k3-tuition-policy` | `student` | https://policy.vinuni.edu.vn/financial-regulations/ |
| 5 | `data/k3_university/scholarship-policy.md` | Tiêu chuẩn và Quy trình Xét Học bổng KKHT | `k3-scholarship-policy` | `student` | https://vinuni.edu.vn/admission/scholarships-and-financial-aid/ |
| 6 | `data/k3_university/faculty-grading-guide.md` | Hướng dẫn Duyệt Lớp và Nhập Điểm Học phần (Giảng viên) | `k3-faculty-grading-guide` | `faculty` | https://registrar.vinuni.edu.vn/faculty/grading-guidelines/ |

---

## 3. Cấu Trúc Metadata Chuẩn (Metadata Schema)

Tất cả các file đều tuân thủ chuẩn YAML Front Matter ở đầu file:

```yaml
---
doc_id: k3-scholarship-policy
title: Tiêu chuẩn và Quy trình Xét Học bổng Khuyến khích Học tập (VinUniversity)
audience: student
department: student-affairs
category: scholarship
language: vi
source_url: https://vinuni.edu.vn/admission/scholarships-and-financial-aid/
retrieved_at: 2026-08-03
document_version: "2026.1"
---
```

---

## 4. Ghi Chú Đặc Điểm Dữ Liệu Cho Bước 3 & Bước 4

1. **File dùng cho Benchmark Query thông thường:**
   - `k3-course-registration.md`: chứa thông tin đợt 1, đợt 2 Add/Drop Period.
   - `k3-prerequisites-policy.md`: chứa quy định môn tiên quyết (điểm C/Pass trở lên).
   - `k3-course-withdrawal.md`: chứa quy định điểm W và chính sách không hoàn phí sau tuần 2.
2. **File dùng cho Benchmark Query yêu cầu Metadata Filtering:**
   - `k3-scholarship-policy.md` (`audience: student`): chứa tiêu chuẩn GPA 3.20 duy trì học bổng 100%.
   - `k3-faculty-grading-guide.md` (`audience: faculty`): chứa quy định 7 ngày nhập điểm thi của giảng viên. Lọc `audience: student` sẽ chặn file này, giúp kiểm thử chính xác `search_with_filter()`.

---

## 5. Kết Quả Kiểm Tra Pipeline (`ingest.py`)

- Lệnh kiểm tra: `python -X utf8 ingest.py`
- Kết quả: **ingest self-check OK** (parse 100% metadata, gán `doc_id` + metadata lên từng chunk).
