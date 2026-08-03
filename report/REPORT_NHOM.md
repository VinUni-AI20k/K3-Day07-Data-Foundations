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

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên bộ tài liệu `uet_handbook` (chunk_size=200):

| Tài liệu                                                                        | Chiến lược (Strategy)           | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?               |
| --------------------------------------------------------------------------------- | ---------------------------------- | ----------------- | --------------------- | --------------------------------------------- |
| Quy định Học bổng & Điểm rèn luyện (`hoc_bong_diem_ren_luyen.md`)       | FixedSizeChunker (`fixed_size`)  | 26                | 193.0 ký tự         | Trung bình (cắt ngang câu nếu hết limit) |
| Quy định Học bổng & Điểm rèn luyện (`hoc_bong_diem_ren_luyen.md`)       | SentenceChunker (`by_sentences`) | 8                 | 625.5 ký tự         | Tốt (giữ trọn vẹn từng câu)             |
| Quy định Học bổng & Điểm rèn luyện (`hoc_bong_diem_ren_luyen.md`)       | RecursiveChunker (`recursive`)   | 33                | 150.8 ký tự         | Rất tốt (chia theo đoạn văn và câu)    |
| Quy định Học phí & Chế độ chính sách (`hoc_phi_che_do_chinh_sach.md`)  | FixedSizeChunker (`fixed_size`)  | 26                | 194.7 ký tự         | Trung bình (cắt ngang câu nếu hết limit) |
| Quy định Học phí & Chế độ chính sách (`hoc_phi_che_do_chinh_sach.md`)  | SentenceChunker (`by_sentences`) | 5                 | 1001.6 ký tự        | Tốt (giữ trọn vẹn từng câu)             |
| Quy định Học phí & Chế độ chính sách (`hoc_phi_che_do_chinh_sach.md`)  | RecursiveChunker (`recursive`)   | 39                | 128.4 ký tự         | Rất tốt (chia theo đoạn văn và câu)    |
| Hướng dẫn Khám chữa bệnh & BHYT (`kham_chua_benh.md`)                     | FixedSizeChunker (`fixed_size`)  | 11                | 199.8 ký tự         | Trung bình (cắt ngang câu nếu hết limit) |
| Hướng dẫn Khám chữa bệnh & BHYT (`kham_chua_benh.md`)                     | SentenceChunker (`by_sentences`) | 3                 | 730.0 ký tự         | Tốt (giữ trọn vẹn từng câu)             |
| Hướng dẫn Khám chữa bệnh & BHYT (`kham_chua_benh.md`)                     | RecursiveChunker (`recursive`)   | 16                | 135.9 ký tự         | Rất tốt (chia theo đoạn văn và câu)    |
| Thông tin Ký túc xá (`ky_tuc_xa.md`)                                        | FixedSizeChunker (`fixed_size`)  | 7                 | 172.4 ký tự         | Trung bình (cắt ngang câu nếu hết limit) |
| Thông tin Ký túc xá (`ky_tuc_xa.md`)                                        | SentenceChunker (`by_sentences`) | 2                 | 602.0 ký tự         | Tốt (giữ trọn vẹn từng câu)             |
| Thông tin Ký túc xá (`ky_tuc_xa.md`)                                        | RecursiveChunker (`recursive`)   | 9                 | 132.9 ký tự         | Rất tốt (chia theo đoạn văn và câu)    |
| Lịch sử truyền thống & Quy tắc ứng xử (`lich_su_truyen_thong.md`)        | FixedSizeChunker (`fixed_size`)  | 9                 | 186.0 ký tự         | Trung bình (cắt ngang câu nếu hết limit) |
| Lịch sử truyền thống & Quy tắc ứng xử (`lich_su_truyen_thong.md`)        | SentenceChunker (`by_sentences`) | 6                 | 277.5 ký tự         | Tốt (giữ trọn vẹn từng câu)             |
| Lịch sử truyền thống & Quy tắc ứng xử (`lich_su_truyen_thong.md`)        | RecursiveChunker (`recursive`)   | 12                | 137.9 ký tự         | Rất tốt (chia theo đoạn văn và câu)    |
| Danh bạ thông tin liên hệ các đơn vị (`thong_tin_lien_he.md`)           | FixedSizeChunker (`fixed_size`)  | 13                | 199.8 ký tự         | Trung bình (cắt ngang câu nếu hết limit) |
| Danh bạ thông tin liên hệ các đơn vị (`thong_tin_lien_he.md`)           | SentenceChunker (`by_sentences`) | 4                 | 645.2 ký tự         | Tốt (giữ trọn vẹn từng câu)             |
| Danh bạ thông tin liên hệ các đơn vị (`thong_tin_lien_he.md`)           | RecursiveChunker (`recursive`)   | 16                | 160.4 ký tự         | Rất tốt (chia theo đoạn văn và câu)    |
| Hướng dẫn Thủ tục hành chính một cửa (`thu_tuc_hanh_chinh_mot_cua.md`) | FixedSizeChunker (`fixed_size`)  | 17                | 195.8 ký tự         | Trung bình (cắt ngang câu nếu hết limit) |
| Hướng dẫn Thủ tục hành chính một cửa (`thu_tuc_hanh_chinh_mot_cua.md`) | SentenceChunker (`by_sentences`) | 1                 | 3328.0 ký tự        | Tốt (giữ trọn vẹn từng câu)             |
| Hướng dẫn Thủ tục hành chính một cửa (`thu_tuc_hanh_chinh_mot_cua.md`) | RecursiveChunker (`recursive`)   | 24                | 137.2 ký tự         | Rất tốt (chia theo đoạn văn và câu)    |

### Chiến lược của từng thành viên

**Thành viên 1 — Phạm Đức Thiện**

- **Loại chiến lược:** `RecursiveChunker` (chunk_size=300, separators=["\n\n", "\n", ". ", " "])
- **Số chunk tạo ra:** 93 chunks (toàn bộ 7 tài liệu)
- **Mô tả & lý do chọn cho chủ đề này:** Phù hợp với văn bản quy định đại học có cấu trúc phân tầng (mục, đoạn, câu). Giúp giữ nguyên tính toàn vẹn của một điều khoản quy định mà không bị cắt đứt ngữ cảnh.

---

**Thành viên 2 — Trần Công Chiến**

- **Loại chiến lược:** `SentenceChunker` (max_sentences_per_chunk=3)
- **Số chunk tạo ra:** 30 chunks (toàn bộ 7 tài liệu)
- **Mô tả & lý do chọn:** Chia nhỏ văn bản theo đơn vị câu độc lập. Thích hợp cho các quy định ngắn gọn, giúp mỗi chunk chứa một ý hoàn chỉnh.

---

**Thành viên 3 — Nguyễn Ngọc Thuận & Phạm Khắc Duy**

- **Loại chiến lược:** `FixedSizeChunker` (chunk_size=250, overlap=50)
- **Số chunk tạo ra:** 109 chunks (toàn bộ 7 tài liệu)
- **Mô tả & lý do chọn:** Chiến lược đơn giản cố định kích thước, tạo overlap để tránh đứt đoạn thông tin ranh giới giữa các chunk.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query)                                                                                          | Câu trả lời chuẩn (Gold Answer)                                                                                                                                                                         | Chunk nào chứa thông tin?              |
| - | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1 | Điều kiện xét cấp học bổng khuyến khích học tập cho sinh viên là gì?                         | Sinh viên trong thời hạn đào tạo chuẩn, học tập và rèn luyện đạt từ khá trở lên, không bị kỷ luật từ mức khiển trách và tích lũy tối thiểu 15 tín chỉ trong học kỳ xét. | Chunk 2 (`hoc_bong_diem_ren_luyen`)     |
| 2 | Mức điểm chuẩn chung khi đánh giá điểm rèn luyện cho sinh viên không vi phạm là bao nhiêu? | Mức điểm chuẩn chung cho sinh viên không vi phạm quy chế là 70 điểm (tổng của 5 nội dung đánh giá), sau đó mới tính cộng thưởng hoặc trừ phạt.                                   | Chunk 9 (`hoc_bong_diem_ren_luyen`)     |
| 3 | Đối tượng sinh viên nào được hưởng chính sách giảm 50% học phí?                            | Sinh viên là con cán bộ, công chức, viên chức, công nhân mà cha hoặc mẹ bị tai nạn lao động hoặc mắc bệnh nghề nghiệp được hưởng trợ cấp thường xuyên.                      | Chunk 19 (`hoc_phi_che_do_chinh_sach`)  |
| 4 | Sinh viên liên hệ đơn vị nào để làm thủ tục khám chữa bệnh và thanh toán BHYT?            | Liên hệ Phòng Công tác Sinh viên (ĐT: 024 3754 8864 hoặc cô Bùi Thị Thu Hương) để được hướng dẫn thủ tục BHYT và khám chữa bệnh.                                                 | Chunk 8 (`kham_chua_benh`)              |
| 5 | Cổng thủ tục hành chính một cửa giải quyết công việc gì cho sinh viên?                        | Cho phép sinh viên nộp hoặc xin các thủ tục giấy tờ hành chính trực tuyến (Online) với Phòng Công tác Sinh viên mà không cần đến trực tiếp.                                        | Chunk 13 (`thu_tuc_hanh_chinh_mot_cua`) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi                                | Chiến lược tốt nhất cho câu này                                       | Có chunk liên quan trong top-3? | Ghi chú                                                              |
| - | ---------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------- |
| 1 | Điều kiện xét học bổng KKHT        | RecursiveChunker                                                             | Có (Top-1)                       | Trả về đúng chunk điều kiện tiêu chuẩn học bổng            |
| 2 | Mức điểm chuẩn rèn luyện 70 điểm | SentenceChunker                                                              | Có (Top-1)                       | Trả về đúng đoạn quy định mức điểm chuẩn                  |
| 3 | Chính sách giảm 50% học phí         | RecursiveChunker (với metadata filter`doc_id: hoc_phi_che_do_chinh_sach`) | Có (Top-1)                       | Lọc theo doc_id loại bỏ nhiễu từ các file học bổng khác      |
| 4 | Thủ tục KCB & Thanh toán BHYT         | RecursiveChunker (với metadata filter`doc_id: kham_chua_benh`)            | Có (Top-1)                       | Trả về đúng SĐT và người phụ trách phòng CTSV              |
| 5 | Thủ tục hành chính một cửa online  | SentenceChunker (với metadata filter`doc_id: thu_tuc_hanh_chinh_mot_cua`) | Có (Top-1)                       | Lọc theo metadata giúp trả về đúng hướng dẫn cổng một cửa |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Lọc bằng metadata (`search_with_filter`) cực kỳ hiệu quả ở các câu 3, 4 và 5. Việc lọc theo `doc_id` (`hoc_phi_che_do_chinh_sach`, `kham_chua_benh`, `thu_tuc_hanh_chinh_mot_cua`) giúp thu hẹp ngay lập tức phạm vi tìm kiếm vector, loại bỏ các chunk chứa từ khóa trùng lặp từ các tài liệu quy định khác, đảm bảo trả về chính xác Chunk Top-1 mong muốn.

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
