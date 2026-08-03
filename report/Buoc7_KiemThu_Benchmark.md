# Kết Quả Bước 7 — Thực Hiện Benchmark & So Sánh Truy Xuất (Retrieval Quality)

**Ngày thực hiện:** 03/08/2026  
**Nhóm:** K3 Day 07  

---

## 1. Kết Quả Chạy Đường Cơ Sở (Baseline Analysis)

Nhóm đã chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu quy định mẫu (`course-registration.md`, `tuition-policy.md`, `prerequisites-policy.md`):

| Tài liệu mẫu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình (ký tự) | Đánh giá giữ ngữ cảnh |
|---|---|---|---|---|
| Tập 3 tài liệu Quy định | **FixedSizeChunker** (`fixed_size`, size=200, overlap=20) | 22 | 192.6 | **Trung bình:** Cắt cố định ký tự nên có thể cắt rách giữa câu hoặc rách từ ở biên chunk. |
| Tập 3 tài liệu Quy định | **SentenceChunker** (`by_sentences`, max=3 câu) | 11 | 344.8 | **Khá:** Bảo toàn nguyên vẹn ngữ cảnh từng câu, nhưng chunk hơi dài khi gộp 3 câu. |
| Tập 3 tài liệu Quy định | **RecursiveChunker** (`recursive`, size=200) | 31 | 121.6 | **Trung bình:** Tách nhỏ linh hoạt theo đoạn/dòng, nhưng đôi khi làm tách rời tiêu đề khỏi nội dung bên dưới. |
| Tập 3 tài liệu Quy định | **CustomSectionHeaderChunker** (Custom - Thành viên 3) | 8 | 480.2 | **Rất tốt:** Tách trọn vẹn từng mục quy định theo Header `##`, ngữ cảnh 100% nguyên vẹn. |

---

## 2. Kết Quả Chạy 5 Câu Hỏi Benchmark Chi Tiết

Tất cả 3 thành viên đã chạy 5 câu hỏi benchmark trên chiến lược của mình:

| # | Câu hỏi (Query) | Kết quả Thành viên 1 (`SentenceChunker`) | Kết quả Thành viên 2 (`RecursiveChunker`) | Kết quả Thành viên 3 (`CustomSectionHeader`) | Chiến lược tốt nhất |
|---|---|---|---|---|---|
| **1** | Sinh viên được xem là đạt học phần tiên quyết A để đăng ký học phần B khi đáp ứng điều kiện điểm số nào? | **Top-1:** Đạt điểm từ C hoặc Pass trở lên (`k3-prerequisites-policy`). Score: 0.88. *(Đúng)* | **Top-1:** Đạt điểm C hoặc Pass trở lên. Score: 0.84. *(Đúng)* | **Top-1:** Trọn vẹn Mục 1 Quy định học phần tiên quyết. Score: 0.92. *(Đúng)* | **CustomSectionHeader** |
| **2** | Nếu xảy ra xung đột lịch học hoặc trùng lịch thi trên hệ thống SIS khi đăng ký học phần thì sinh viên cần xử lý như thế nào? | **Top-1:** Chọn nhóm lớp khác hoặc gửi Ticket cho Registrar Office. Score: 0.86. *(Đúng)* | **Top-1:** Tự động chặn đăng ký, gửi Ticket. Score: 0.82. *(Đúng)* | **Top-1:** Trọn vẹn Mục 3 Xử lý sự cố trùng lịch. Score: 0.90. *(Đúng)* | **CustomSectionHeader** |
| **3** | Hậu quả gì sẽ xảy ra đối với sinh viên nếu chậm nộp học phí quá hạn quy định của nhà trường? | **Top-1:** Tạm khóa tài khoản SIS, cấm thi và cấm đăng ký HP tiếp theo. Score: 0.91. *(Đúng)* | **Top-1:** Bị tạm khóa tài khoản SIS Portal. Score: 0.87. *(Đúng)* | **Top-1:** Trọn vẹn Mục 3 Xử lý nợ học phí. Score: 0.94. *(Đúng)* | **CustomSectionHeader** |
| **4** | Theo hướng dẫn dành cho giảng viên, thời hạn tối đa để giảng viên hoàn tất nhập điểm thi kết thúc học phần là bao lâu? | **Top-2:** Nhập điểm thi kết thúc học phần trong 7 ngày làm việc. Score: 0.79. *(Cần filter `audience=faculty`)* | **Top-3:** Trong vòng 7 ngày làm việc. Score: 0.75. *(Lẫn với quy định sinh viên)* | **Top-1 (với Metadata Filter `audience=faculty`):** Nhập điểm trong 7 ngày làm việc. Score: 0.91. *(Rất chính xác)* | **CustomSectionHeader + Filter** |
| **5** | Sinh viên bình thường được đăng ký tối đa bao nhiêu tín chỉ và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính quy? | **Top-1:** Tối đa 24 tín chỉ, tối thiểu 12 tín chỉ / học kỳ. Score: 0.89. *(Đúng)* | **Top-1:** Tối đa 24 tín chỉ, tối thiểu 12 tín chỉ. Score: 0.85. *(Đúng)* | **Top-1:** Trọn vẹn Mục 2 Ràng buộc tín chỉ. Score: 0.93. *(Đúng)* | **CustomSectionHeader** |

---

## 3. Tổng Kết Chất Lượng Truy Xuất (Retrieval Score)

- **Thành viên 1 (`SentenceChunker`):** 9 / 10 điểm (4/5 câu Top-1, câu 4 nằm ở Top-2 do thiếu filter).
- **Thành viên 2 (`RecursiveChunker`):** 8 / 10 điểm (3/5 câu Top-1, 2 câu Top-2/Top-3).
- **Thành viên 3 (`CustomSectionHeaderChunker`):** 10 / 10 điểm (5/5 câu Top-1 chính xác tuyệt đối nhờ giữ nguyên ngữ cảnh Section và Metadata Filter).
- **Tổng điểm chất lượng truy xuất phần nhóm:** **10 / 10 điểm**.
