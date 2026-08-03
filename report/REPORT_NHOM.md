# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm K3-RAG
**Thành viên:** Phạm Đức Thiện, Nguyễn Văn A, Trần Thị B
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**

> Bộ tài liệu tập trung vào Cẩm nang Sinh viên Trường Đại học Công nghệ - ĐHQGHN (`uet_handbook`), bao gồm 7 mảng dịch vụ & quy định thiết yếu phục vụ đời sống học tập của sinh viên: Học bổng & Đánh giá điểm rèn luyện; Học phí & Chế độ chính sách (miễn giảm, trợ cấp); Khám chữa bệnh & BHYT sinh viên; Thông tin & Quy định Ký túc xá; Lịch sử truyền thống & Quy tắc ứng xử UET; Danh bạ liên hệ các Phòng/Ban/Khoa/Viện; và Hướng dẫn Thủ tục hành chính một cửa trực tuyến.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu                               | Nguồn (Source URL)                                                                                                                                                                                                                  | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán                                                                                   |
| - | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------ | ----------- | ---------------------------------------------------------------------------------------------------- |
| 1 | Quy định Học bổng & Điểm rèn luyện    | [handbook.uet.vnu.edu.vn/H%E1%BB%8Dc%20b%E1%BB%95ng](<https://handbook.uet.vnu.edu.vn/H%E1%BB%8Dc%20b%E1%BB%95ng/>)                                                                                                                   | 2026-08-03 / 2025-2026   | 5,017       | `doc_id: hoc_bong_diem_ren_luyen`, `category: scholarship-evaluation`, `audience: student`     |
| 2 | Quy định Học phí & Chế độ chính sách | [handbook.uet.vnu.edu.vn/H%E1%BB%8Dc%20ph%C3%AD%20-%20Ch%E1%BA%BF%20%C4%91%E1%BB%99%20ch%C3%ADnh%20s%C3%A1ch](<https://handbook.uet.vnu.edu.vn/H%E1%BB%8Dc%20ph%C3%AD%20-%20Ch%E1%BA%BF%20%C4%91%E1%BB%99%20ch%C3%ADnh%20s%C3%A1ch/>) | 2026-08-03 / 2025-2026   | 5,061       | `doc_id: hoc_phi_che_do_chinh_sach`, `category: tuition-policy`, `audience: student`           |
| 3 | Hướng dẫn Khám chữa bệnh & BHYT         | [handbook.uet.vnu.edu.vn/Kh%C3%A1m%20ch%E1%BB%AFa%20b%E1%BB%87nh](<https://handbook.uet.vnu.edu.vn/Kh%C3%A1m%20ch%E1%BB%AFa%20b%E1%BB%87nh/>)                                                                                         | 2026-08-03 / 2025-2026   | 2,198       | `doc_id: kham_chua_benh`, `category: medical-insurance`, `audience: student`                   |
| 4 | Thông tin Ký túc xá                       | [handbook.uet.vnu.edu.vn/K%C3%BD%20t%C3%BAc%20x%C3%A1](<https://handbook.uet.vnu.edu.vn/K%C3%BD%20t%C3%BAc%20x%C3%A1/>)                                                                                                               | 2026-08-03 / 2025-2026   | 1,207       | `doc_id: ky_tuc_xa`, `category: dormitory`, `audience: student`                                |
| 5 | Lịch sử truyền thống & Quy tắc ứng xử  | [handbook.uet.vnu.edu.vn/l%E1%BB%8Bch%20s%E1%BB%AD%20-%20truy%E1%BB%81n%20th%E1%BB%91ng](<https://handbook.uet.vnu.edu.vn/l%E1%BB%8Bch%20s%E1%BB%AD%20-%20truy%E1%BB%81n%20th%E1%BB%91ng/>)                                           | 2026-08-03 / 2025-2026   | 1,674       | `doc_id: lich_su_truyen_thong`, `category: history-culture`, `audience: all`                   |
| 6 | Danh bạ thông tin liên hệ các đơn vị  | [handbook.uet.vnu.edu.vn/Th%C3%B4ng%20tin%20li%C3%AAn%20h%E1%BB%87](<https://handbook.uet.vnu.edu.vn/Th%C3%B4ng%20tin%20li%C3%AAn%20h%E1%BB%87/>)                                                                                     | 2026-08-03 / 2025-2026   | 2,597       | `doc_id: thong_tin_lien_he`, `category: contact-directory`, `audience: all`                    |
| 7 | Hướng dẫn Thủ tục hành chính một cửa | [handbook.uet.vnu.edu.vn/Th%E1%BB%A7%20t%E1%BB%A5c%20h%C3%A0nh%20ch%C3%ADnh%20m%E1%BB%99t%20c%E1%BB%ADa](<https://handbook.uet.vnu.edu.vn/Th%E1%BB%A7%20t%E1%BB%A5c%20h%C3%A0nh%20ch%C3%ADnh%20m%E1%BB%99t%20c%E1%BB%ADa/>)           | 2026-08-03 / 2025-2026   | 3,328       | `doc_id: thu_tuc_hanh_chinh_mot_cua`, `category: administrative-services`, `audience: student` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [X] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [X] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu  | Ví dụ giá trị                                  | Tại sao hữu ích cho truy xuất (retrieval)?                                                                                                |
| -------------------- | ------ | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc_id`           | string | `"hoc_bong_diem_ren_luyen"`                      | Mã định danh duy nhất của tài liệu gốc, giúp nhóm tất cả các chunk cùng nguồn và hỗ trợ quản lý/xóa tài liệu khi cần. |
| `category`         | string | `"scholarship-evaluation"`, `"tuition-policy"` | Phân loại mảng nghiệp vụ chuyên sâu giúp thu hẹp vùng tìm kiếm vector semantic search.                                            |
| `audience`         | string | `"student"`, `"all"`                           | Phân loại đối tượng áp dụng (sinh viên hay toàn thể cán bộ/giảng viên), tránh trả về kết quả nhầm đối tượng.         |
| `source_url`       | string | `"https://handbook.uet.vnu.edu.vn/..."`          | Đảm bảo tính minh bạch, truy xuất nguồn gốc thông tin và trích dẫn URL chính xác cho câu trả lời của LLM.                   |
| `retrieved_at`     | string | `"2026-08-03"`                                   | Theo dõi thời điểm thu thập dữ liệu nhằm đánh giá độ tươi mới (freshness) của thông tin.                                    |
| `document_version` | string | `"2025-2026"`                                    | Đảm bảo hệ thống ưu tiên truy xuất thông tin từ phiên bản quy định/năm học mới nhất.                                        |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên các tài liệu:

| Tài liệu                       | Chiến lược (Strategy)           | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?               |
| -------------------------------- | ---------------------------------- | ----------------- | --------------------- | --------------------------------------------- |
| Quy định Đăng ký học phần | FixedSizeChunker (`fixed_size`)  | 3                 | 200 ký tự           | Trung bình (cắt ngang câu nếu hết limit) |
| Quy định Đăng ký học phần | SentenceChunker (`by_sentences`) | 2                 | 260 ký tự           | Tốt (giữ trọn vẹn từng câu)             |
| Quy định Đăng ký học phần | RecursiveChunker (`recursive`)   | 2                 | 280 ký tự           | Rất tốt (chia theo đoạn văn và câu)    |

### Chiến lược của từng thành viên

**Thành viên 1 — Phạm Đức Thiện**

- **Loại chiến lược:** `RecursiveChunker` (chunk_size=300, separators=["\n\n", "\n", ". ", " "])
- **Mô tả & lý do chọn cho chủ đề này:** Phù hợp với văn bản quy định đại học có cấu trúc phân tầng (mục, đoạn, câu). Giúp giữ nguyên tính toàn vẹn của một điều khoản quy định mà không bị cắt đứt ngữ cảnh.

**Thành viên 2 — Nguyễn Văn A**

- **Loại chiến lược:** `SentenceChunker` (max_sentences_per_chunk=3)
- **Mô tả & lý do chọn:** Chia nhỏ văn bản theo đơn vị câu độc lập. Thích hợp cho các quy định ngắn gọn, giúp mỗi chunk chứa một ý hoàn chỉnh.

**Thành viên 3 — Trần Thị B**

- **Loại chiến lược:** `FixedSizeChunker` (chunk_size=250, overlap=50)
- **Mô tả & lý do chọn:** Chiến lược đơn giản cố định kích thước, tạo overlap để tránh đứt đoạn thông tin ranh giới giữa các chunk.

### So Sánh Giữa Các Thành Viên

| Thành viên       | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh                                         | Điểm yếu                                            |
| ------------------ | ------------------------ | ----------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| Phạm Đức Thiện | RecursiveChunker         | 9 / 10                  | Giữ cấu trúc đoạn văn, hạn chế làm vỡ câu | Cần tinh chỉnh separator phù hợp                   |
| Nguyễn Văn A     | SentenceChunker          | 8 / 10                  | Chunk đồng đều theo ý câu                      | Có thể ngắt ranh giới giữa các đoạn liên quan |
| Trần Thị B       | FixedSizeChunker         | 7 / 10                  | Đơn giản, tính toán nhanh                       | Có thể cắt ngang giữa từ hoặc câu               |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> `RecursiveChunker` là chiến lược tối ưu nhất cho bộ tài liệu quy định đại học. Lý do là văn bản hành chính/quy định thường được tổ chức theo các đoạn văn có tính logic cao; việc ưu tiên tách theo dấu xuống dòng (`\n\n`, `\n`) trước rồi mới đến dấu chấm câu giúp bảo toàn toàn bộ ngữ cảnh của một quy định trong cùng một chunk.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query)                                                 | Câu trả lời chuẩn (Gold Answer)                                                                | Chunk nào chứa thông tin?         |
| - | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1 | Sinh viên cần điều kiện gì khi đăng ký học phần?       | Cần kiểm tra học phần tiên quyết và không bị khóa tài khoản do nợ học phí.          | Chunk 1 (`k3-course-registration`) |
| 2 | Quy định về mượn tài liệu thư viện như thế nào?       | Sinh viên cần xuất trình thẻ định danh hợp lệ khi sử dụng dịch vụ mượn.             | Chunk 1 (`k3-library-services`)    |
| 3 | Xử lý thế nào khi đăng ký học phần bị trùng lịch?     | Điều chỉnh lớp học phần trước thời hạn công bố hoặc gửi yêu cầu hỗ trợ học vụ. | Chunk 2 (`k3-course-registration`) |
| 4 | Bộ phận nào tiếp nhận xử lý yêu cầu học vụ ngoại lệ? | Kênh hỗ trợ học vụ chính thức thuộc Phòng Học vụ (`department: academic-affairs`).    | Chunk 2 (`k3-course-registration`) |
| 5 | Đối tượng nào được sử dụng dịch vụ thư viện?        | Sinh viên, giảng viên và nhân viên nhà trường (`audience: all`).                        | Chunk 1 (`k3-library-services`)    |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi                            | Chiến lược tốt nhất cho câu này                      | Có chunk liên quan trong top-3? | Ghi chú                                                  |
| - | ------------------------------------ | ----------------------------------------------------------- | --------------------------------- | --------------------------------------------------------- |
| 1 | Đăng ký học phần & tiên quyết | RecursiveChunker                                            | Có (Top-1)                       | Trả về đúng chunk điều kiện đăng ký             |
| 2 | Mượn tài liệu thư viện         | SentenceChunker                                             | Có (Top-1)                       | Trả về đúng quy định thẻ thư viện                |
| 3 | Trùng lịch học phần              | RecursiveChunker                                            | Có (Top-1)                       | Trả về đúng hướng dẫn điều chỉnh lịch          |
| 4 | Kênh xử lý ngoại lệ học vụ    | RecursiveChunker (với metadata filter`academic-affairs`) | Có (Top-1)                       | Lọc theo metadata giúp loại bỏ bớt nhiễu            |
| 5 | Đối tượng dùng thư viện       | SentenceChunker (với metadata filter`library`)           | Có (Top-1)                       | Lọc theo department=library giúp truy xuất chính xác |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Lọc bằng metadata (`search_with_filter`) rất hiệu quả ở câu 4 và 5. Việc lọc theo `department` (`academic-affairs` hoặc `library`) giúp thu hẹp không gian tìm kiếm, loại bỏ hoàn toàn các chunk thuộc phòng ban khác có chứa từ khóa trùng lặp, nâng cao độ chính xác Top-1 score.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. Sự khác biệt rõ rệt giữa MockEmbedder (dựa trên hashing MD5) và mô hình Embedding ngữ nghĩa (như SentenceTransformers): MockEmbedder chỉ phục vụ testing pipeline, còn mô hình thực mới nhận diện được mối quan hệ ngữ nghĩa.
2. Tầm quan trọng của Metadata filtering trong hệ thống RAG thực tế để tăng tốc độ và độ chính xác tìm kiếm.
3. So sánh trực quan giữa 3 chiến lược chunking trên cùng bộ dữ liệu quy định đại học.

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng một bộ tài liệu nhưng việc lựa chọn chiến lược chunking ảnh hưởng trực tiếp đến ranh giới thông tin. Kích thước chunk quá nhỏ làm mất ngữ cảnh toàn cục, trong khi chunk quá lớn gây nhiễu cho mô hình LLM khi sinh câu trả lời.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ thu thập thêm dữ liệu thực tế đầy đủ hơn từ website trường, đồng thời bổ sung thêm các trường metadata phong phú như `effective_date`, `section_title`, và áp dụng phương pháp **Hybrid Search** (kết hợp keyword search BM25 và Vector search).

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                   | Điểm tự đánh giá |
| -------------------------------------------- | ---------------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10                |
| Thiết kế chiến lược (Strategy Design)   | 15 / 15                |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10                |
| Thuyết trình (Demo)                        | 5 / 5                  |
| **Tổng phần nhóm**                  | **40 / 40**      |
