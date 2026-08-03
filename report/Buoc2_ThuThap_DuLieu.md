# Bước 2: Thu Thập & Chuẩn Hóa Dữ Liệu Corpus (K3 University Services)

Tài liệu này tổng hợp kết quả Bước 2 của nhóm trên corpus hiện tại trong `data/k3_university/`.

**Thành viên phụ trách chính:** Lê Nguyễn Minh Đức

---

## 1. Tổng quan bộ tài liệu

- **Chủ đề K3:** Dịch vụ & Quy định Đại học (VinUniversity).
- **Thư mục lưu trữ:** `data/k3_university/`
- **File kiểm kê nguồn:** `data/k3_university/sources.csv`
- **Số lượng tài liệu:** 5 tài liệu `.md`

---

## 2. Danh sách tài liệu & nguồn

| # | File Path | Title | doc_id | Audience | Source URL |
|---|---|---|---|---|---|
| 1 | `data/k3_university/course-registration.md` | Hướng dẫn đăng ký học phần | `vinuni-course-registration` | `student` | https://registrar.vinuni.edu.vn/academics/class-schedule-course-registration/ |
| 2 | `data/k3_university/academic-regulations.md` | Quy định đăng ký, thêm, bỏ và rút học phần | `vinuni-academic-regulations-add-drop` | `student` | https://policy.vinuni.edu.vn/all-policies/academic-regulations-for-full-time-undergraduate-programs/ |
| 3 | `data/k3_university/academic-scheduling.md` | Quy trình lập lịch học và mở đăng ký | `vinuni-academic-scheduling` | `staff` | https://policy.vinuni.edu.vn/all-policies/university-academic-scheduling-procedures/ |
| 4 | `data/k3_university/library-services.md` | Quyền mượn thư viện cho sinh viên bậc đại học | `vinuni-library-borrowing-undergraduate` | `student` | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ |
| 5 | `data/k3_university/library-access-policy.md` | Quy định truy cập và sử dụng thư viện | `vinuni-library-access-policy` | `all` | https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/ |

---

## 3. Metadata chuẩn

Tất cả file `.md` đều dùng front matter YAML với các trường:

```yaml
---
doc_id: vinuni-course-registration
title: Hướng dẫn đăng ký học phần
audience: student
department: academic-affairs
language: vi
source_url: https://registrar.vinuni.edu.vn/academics/class-schedule-course-registration/
retrieved_at: 2026-08-03
document_version: "2026-08-03"
---
```

---

## 4. Ghi chú phục vụ Bước 5 và Bước 6

1. **Câu hỏi benchmark thông thường**
   - `vinuni-course-registration`
   - `vinuni-academic-regulations-add-drop`
   - `vinuni-library-borrowing-undergraduate`

2. **Câu hỏi cần metadata filtering**
   - `vinuni-academic-scheduling` có `audience: staff`
   - `vinuni-library-access-policy` có `audience: all`
   - Khi hỏi về quy định dành cho sinh viên, nên lọc `audience: student`

---

## 5. Kết quả kiểm tra pipeline

- Lệnh kiểm tra: `python -X utf8 ingest.py`
- Kết quả: `ingest self-check OK`

