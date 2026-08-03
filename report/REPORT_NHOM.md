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

## 1. Bước 1 - Chốt đề tài và phạm vi

Nhóm chốt đề tài: **Đăng ký môn học và quy định học vụ cho sinh viên**.

Phạm vi tập trung:
- Quy trình đăng ký học phần
- Thêm / bỏ / rút học phần
- Điều kiện tiên quyết và song hành
- Học phí và học bổng
- Duyệt lớp và nhập điểm dành cho giảng viên

Lý do chọn:
- Đúng chủ đề K3
- Có tài liệu công khai, truy vết được
- Có thể xây dựng benchmark đa dạng

---

## 2. Bước 2-4 - Corpus, metadata và kiểm kê nguồn

Corpus hiện có 6 tài liệu chính thức trong `data/k3_university/`:

| # | Tên tài liệu | doc_id | Audience |
|---|---|---|---|
| 1 | Quy định và Quy trình Đăng ký Học phần | `k3-course-registration` | `student` |
| 2 | Quy định về Học phần Tiên quyết và Song hành | `k3-prerequisites-policy` | `student` |
| 3 | Quy trình Rút bớt Học phần và Hủy Đăng ký Môn học | `k3-course-withdrawal` | `student` |
| 4 | Quy định về Thời hạn và Mức đóng Học phí Học kỳ | `k3-tuition-policy` | `student` |
| 5 | Tiêu chuẩn và Quy trình Xét Học bổng Khuyến khích Học tập | `k3-scholarship-policy` | `student` |
| 6 | Hướng dẫn Duyệt Lớp và Nhập Điểm Học phần dành cho Giảng viên | `k3-faculty-grading-guide` | `faculty` |

Metadata bắt buộc đã dùng:
- `doc_id`
- `title`
- `audience`
- `department`
- `category`
- `language`
- `source_url`
- `retrieved_at`
- `document_version`

`sources.csv` khớp 1-1 với các file tài liệu.

---

## 3. Bước 5 - Benchmark questions

Nhóm thống nhất 5 câu hỏi benchmark:
- điều kiện tiên quyết
- trùng lịch khi đăng ký
- quá hạn học phí
- thời hạn nhập điểm cho giảng viên
- ràng buộc tín chỉ học kỳ

Chi tiết xem [Buoc5_Benchmark_Questions.md](/home/x-phuong/Code/VinUni/K3-Day07-Data-Foundations/report/Buoc5_Benchmark_Questions.md).

---

## 4. Bước 6 - Phân công chiến lược

- Nguyễn Xuân Phượng: `SentenceChunker`
- Lê Nguyễn Minh Đức: `RecursiveChunker`
- Nguyễn Đào Nam Hải: `CustomSectionHeaderChunker`

Chi tiết xem [Buoc6_PhanCong_ChienLuoc.md](/home/x-phuong/Code/VinUni/K3-Day07-Data-Foundations/report/Buoc6_PhanCong_ChienLuoc.md).

---

## 5. Bước 7 - Kết quả benchmark

Kết quả tổng hợp:
- `SentenceChunker`: 9/10
- `RecursiveChunker`: 8/10
- `CustomSectionHeaderChunker`: 10/10

Metadata filter hữu ích nhất ở câu hỏi về giảng viên nhập điểm.

Chi tiết xem [Buoc7_KiemThu_Benchmark.md](/home/x-phuong/Code/VinUni/K3-Day07-Data-Foundations/report/Buoc7_KiemThu_Benchmark.md).

---

## 6. Bước 8 - Phân tích và bài học

Kết luận chính:
- Văn bản quy định nên chunk theo header/section nếu có cấu trúc rõ.
- Metadata filtering giúp giảm nhiễu khi corpus có nhiều đối tượng khác nhau.
- Bộ benchmark 5 câu giúp so sánh chiến lược khách quan hơn.

Chi tiết xem [Buoc8_PhanTich_SoSanh.md](/home/x-phuong/Code/VinUni/K3-Day07-Data-Foundations/report/Buoc8_PhanTich_SoSanh.md).

