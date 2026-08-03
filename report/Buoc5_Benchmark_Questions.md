# Kết Quả Bước 5 — Kiểm Tra Corpus & Chốt 5 Câu Hỏi Đánh Giá (Benchmark Questions)

**Ngày thực hiện:** 03/08/2026  
**Đơn vị/Nhóm:** Nhóm 2k345  
**Thành viên phụ trách:** Thành viên 3 (Nguyễn Đào Nam Hải - 2A202601037) & Nhóm trưởng  

---

## 1. Kết Quả Kiểm Tra Bộ Dữ Liệu (Corpus Verification)

Nhóm đã kiểm tra toàn bộ bộ dữ liệu quy định đại học (VinUniversity) tại thư mục `data/k3_university/`:
- **Số lượng tài liệu:** 6 file `.md` chính thức.
- **Tình trạng Metadata:** Đã có đầy đủ các trường `doc_id`, `title`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version`.
- **Độ sẵn sàng:** Tất cả tài liệu đều chứa thông tin công khai, có thể đối soát trực tiếp và đủ phong phú để xây dựng các dạng câu hỏi khác nhau.

---

## 2. Danh Sách 5 Câu Hỏi Đánh Giá (Benchmark Questions) & Câu Trả Lời Chuẩn (Gold Answers)

Bộ 5 câu hỏi được thiết kế theo đúng tiêu chuẩn đa dạng, bao quát các loại thông tin (Định nghĩa/Quy định, Quy trình, Hậu quả/Thời hạn, Cần Metadata Filtering, và Ràng buộc chỉ số):

| # | Loại câu hỏi | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Tài liệu & Chunk chứa thông tin | Metadata Filter gợi ý |
|---|---|---|---|---|---|
| 1 | **Định nghĩa / Điều kiện** | Sinh viên được xem là đạt học phần tiên quyết A để đăng ký học phần B khi đáp ứng điều kiện điểm số nào? | Sinh viên bắt buộc phải học và đạt điểm từ **C** (hoặc **Pass**) trở lên ở học phần A thì mới đủ điều kiện đăng ký học phần B. | `k3-prerequisites-policy.md` (Mục 1: Định nghĩa Học phần Tiên quyết) | `category: academic-rules` |
| 2 | **Quy trình / Thao tác** | Nếu xảy ra xung đột lịch học hoặc trùng lịch thi trên hệ thống SIS khi đăng ký học phần thì sinh viên cần xử lý như thế nào? | Hệ thống SIS sẽ tự động chặn đăng ký. Sinh viên cần chủ động **chọn nhóm lớp khác** hoặc **gửi Ticket hỗ trợ cho Registrar Office** trước hạn chót. | `k3-course-registration.md` (Mục 3: Xử lý sự cố trùng lịch) | `category: course-registration` |
| 3 | **Hậu quả / Thời hạn** | Hậu quả gì sẽ xảy ra đối với sinh viên nếu chậm nộp học phí quá hạn quy định của nhà trường? | Sinh viên nợ học phí quá hạn sẽ bị **tạm khóa tài khoản SIS Portal**, **không được tham gia thi kết thúc học phần** và **không được đăng ký học phần học kỳ tiếp theo**. | `k3-tuition-policy.md` (Mục 3: Xử lý nợ học phí) | `category: tuition-fee` |
| 4 | **Cần Filter Metadata** *(Yêu cầu lọc đối tượng/file)* | Theo hướng dẫn dành cho giảng viên, thời hạn tối đa để giảng viên hoàn tất nhập điểm thi kết thúc học phần là bao lâu? | Điểm thi kết thúc học phần phải được nhập hoàn tất **trong vòng 7 ngày làm việc** kể từ ngày thi. | `k3-faculty-grading-guide.md` (Mục 2: Quy định nhập điểm thành phần) | `audience: faculty` hoặc `doc_id: k3-faculty-grading-guide` |
| 5 | **Ràng buộc chỉ số / Con số** | Sinh viên bình thường được đăng ký tối đa bao nhiêu tín chỉ và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính quy? | Sinh viên bình thường được đăng ký **tối đa 24 tín chỉ / học kỳ** và **tối thiểu 12 tín chỉ / học kỳ** (trừ học kỳ cuối). | `k3-course-registration.md` (Mục 2: Ràng buộc tín chỉ) | `audience: student` |

---

## 3. Tiêu Chí Đánh Giá Cho Bước Tiếp Theo (Bước 6 - Bước 8)

- **Thành viên 3 (và các thành viên khác trong nhóm)** sẽ dùng đúng bộ 5 câu hỏi này để chạy kiểm thử trên chiến lược Chunking riêng của mình.
- **Quy tắc chấm điểm chất lượng truy xuất (2 điểm/câu):**
  - **2 điểm:** Top-3 có chứa chunk liên quan VÀ Agent trả lời chính xác.
  - **1 điểm:** Có chunk liên quan nhưng nằm ngoài Top-1 hoặc Agent trả lời chưa đầy đủ.
  - **0 điểm:** Không tìm thấy chunk liên quan trong Top-3.
