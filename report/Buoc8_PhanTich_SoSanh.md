# Kết Quả Bước 8 — Phân Tích So Sánh, Phân Tích Lỗi & Bài Học Nhóm

**Ngày thực hiện:** 03/08/2026  
**Nhóm:** K3 Day 07  

---

## 1. Bảng So Sánh Chiến Lược Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| **Thành viên 1** (Nguyễn Xuân Phượng) | `SentenceChunker` | 9/10 | Giữ được cấu trúc câu hoàn chỉnh, tránh xé lẻ từ ngữ. | Không phân biệt được ranh giới giữa các phần/mục lớn khi gộp 3 câu. |
| **Thành viên 2** (Lê Nguyễn Minh Đức) | `RecursiveChunker` | 8/10 | Linh hoạt, cắt nhỏ văn bản đều đặn theo kích thước mong muốn. | Kích thước chunk quá nhỏ (avg 121 chars) dễ làm thất lạc mối liên hệ giữa tiêu đề và nội dung. |
| **Thành viên 3** (Nguyễn Đào Nam Hải) | `CustomSectionHeaderChunker` | 10/10 | Bảo tồn 100% ngữ cảnh của một điều khoản quy định theo Header `##`. Ngữ nghĩa cực kỳ mạch lạc. | Nếu một Section quá dài (trên 1,000 từ) sẽ cần thêm bước sub-chunking phụ. |

### Chiến lược nào tốt nhất cho chủ đề quy định đại học? Tại sao?
> **Chiến lược tốt nhất:** `CustomSectionHeaderChunker` (kết hợp với Metadata Filtering).
> **Lý do:** Văn bản quy định đại học mang tính pháp lý/thủ tục, từng điều khoản (section) là một đơn vị thông tin độc lập hoàn chỉnh. Việc tách theo tiêu đề mục giúp Vector Embedding đại diện chính xác trọn vẹn ngữ nghĩa của quy định đó, không bị nhiễu bởi các đoạn văn xung quanh.

---

## 2. Phân Tích Lỗi Truy Xuất (Failure Analysis)

Nhóm đã tìm thấy 1 trường hợp lỗi tiêu biểu trong quá trình so sánh:

- **Câu hỏi gặp sự cố (Query):** *"Theo hướng dẫn dành cho giảng viên, thời hạn tối đa để giảng viên hoàn tất nhập điểm thi kết thúc học phần là bao lâu?"* (Câu hỏi số 4).
- **Trường hợp lỗi:** Khi chưa dùng Metadata Filter trên chiến lược `RecursiveChunker` hoặc `FixedSizeChunker`, hệ thống trả về Top-1 chunk từ file `course-registration.md` (nói về thời hạn đăng ký học phần của sinh viên) thay vì file `faculty-grading-guide.md` (hướng dẫn cho giảng viên).
- **Nguyên nhân chính:** 
  1. Từ khóa *"thời hạn"*, *"học phần"* xuất hiện ở cả tài liệu dành cho sinh viên và giảng viên, làm điểm vector similarity bị nhiễu lexical/semantic overlap.
  2. Không lọc metadata theo trường `audience` trước khi thực hiện similarity search.
- **Đề xuất cải thiện:** Sử dụng `search_with_filter(query, metadata_filter={"audience": "faculty"})` để loại bỏ hoàn toàn các tài liệu dành cho sinh viên trước khi tìm kiếm vector. Khi áp dụng filter này, kết quả trả về chính xác 100% ở vị trí Top-1 (`7 ngày làm việc`).

---

## 3. Vai Trò Của Metadata Filtering

> **Lọc bằng Metadata có giúp ích không?** 
> Có, cực kỳ hữu ích! Đặc biệt ở **Câu hỏi số 4**. Khi lọc trước theo `audience: faculty` hoặc `category: grading-policy`, không gian tìm kiếm giảm đi 80%, loại bỏ nhiễu từ các văn bản quy định của sinh viên và nâng độ chính xác Top-1 từ Top-3 lên Top-1 tuyệt đối.

---

## 4. Những Phân Tích (Insights) & Bài Học Rút Ra Khi Demo

1. **Cấu trúc dữ liệu quyết định chiến lược Chunking:** Văn bản có cấu trúc phân mục (như quy định, luật, FAQ) nên ưu tiên chunking theo Header/Section thay vì dùng Fixed-size cố định.
2. **Metadata Filtering là "vũ khí" nhân đôi độ chính xác:** Kết hợp Hybrid Search (Metadata Pre-filtering + Vector Similarity Search) giúp RAG Agent không bị nhầm lẫn giữa các đối tượng người dùng khác nhau (sinh viên vs giảng viên).
3. **Đánh giá RAG cần bộ Benchmark chuẩn:** Việc xây dựng 5 câu hỏi gold answer kiểm chứng được giúp nhóm đo lường được hiệu quả của từng thay đổi nhỏ trong codebase.

---

## 5. Tự Đánh Giá Tổng Thể Phần Nhóm: **40 / 40 điểm**
- Lựa chọn tài liệu (Document Set Quality): **10 / 10**
- Thiết kế chiến lược (Strategy Design): **15 / 15**
- Chất lượng truy xuất (Retrieval Quality): **10 / 10**
- Thuyết trình (Demo Insights): **5 / 5**
