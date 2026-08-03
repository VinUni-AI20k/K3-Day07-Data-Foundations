# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Dịch vụ và quy định đại học UEH: đăng ký học phần, học phí, học bổng, thư viện, ký túc xá và thẻ sinh viên (nguồn công khai từ daotao.ueh.edu.vn và dsa.ueh.edu.vn).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Hướng dẫn đăng ký học phần trực tuyến | https://daotao.ueh.edu.vn/thong-bao-huong-dan-dang-ky-hoc-phan-truc-tuyen-cho-sinh-vien-dhcq-ltdhcq-vb2dhcq/ | 2026-08-03 / not-stated | 1,182 | audience, department, category, language |
| 2 | Kế hoạch đăng ký học phần HK cuối 2025 | https://daotao.ueh.edu.vn/thong-bao-ke-hoach-dang-ky-hoc-phan-va-nop-hoc-phi-hoc-ky-cuoi-nam-2025-doi-voi-sinh-vien-dai-hoc-chinh-quy-van-bang-2-lien-thong-dhcq-vua-lam-vua-hoc/ | 2026-08-03 / 2025-hoc-ky-cuoi | 7,137 | audience, department, category, language |
| 3 | Khung thu nội trú phí KTX 2025 | https://dsa.ueh.edu.vn/tin-tuc/thong-bao-khung-thoi-gian-thu-noi-tru-phi-ky-tuc-xa-ueh-nam-2025/ | 2026-08-03 / 2025 | 1,547 | audience, department, category, language |
| 4 | Thu nội trú phí KTX Quý III/2026 | https://dsa.ueh.edu.vn/tin-tuc/thong-bao-ve-viec-thu-noi-tru-phi-ky-tuc-xa-quy-iii-2026-thang-789-nam-2026/ | 2026-08-03 / 2026-q3 | 1,293 | audience, department, category, language |
| 5 | Văn hóa đọc & UEH Smart Library | https://dsa.ueh.edu.vn/tin-tuc/van-hoa-doc-tai-ueh-khi-tri-thuc-tro-thanh-von-lieng-cua-nhung-nha-lanh-dao-tuong-lai/ | 2026-08-03 / not-stated | 6,778 | audience=all, department, category, language |
| 6 | Đào tạo thư viện — buổi cho người học | https://dsa.ueh.edu.vn/ban-tin-portal/thu-vien-ueh-trien-khai-chuong-trinh-dao-tao-thuc-day-hoat-dong-doc-va-xuat-ban-bai-bao-khoa-hoc/ | 2026-08-03 / 2025-05-05 | 1,202 | audience=student, department, category, language |
| 7 | Đào tạo thư viện — buổi cho giảng viên | https://dsa.ueh.edu.vn/ban-tin-portal/thu-vien-ueh-trien-khai-chuong-trinh-dao-tao-thuc-day-hoat-dong-doc-va-xuat-ban-bai-bao-khoa-hoc/ | 2026-08-03 / 2025-05-05 | 1,238 | audience=faculty, department, category, language |
| 8 | Chính sách học bổng UEH (tổng quan) | https://dsa.ueh.edu.vn/tin-tuc/chinh-sach-hoc-bong/ | 2026-08-03 / not-stated | 12,732 | audience, department, category, language |
| 9 | Quy định xét cấp học bổng khuyến khích | https://daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy/ | 2026-08-03 / not-stated | 5,283 | audience, department, category, language |
| 10 | Dịch vụ thẻ sinh viên UEH | https://dsa.ueh.edu.vn/chuyen-trang-ho-tro-dich-vu-tien-ich-ueh/the-sinh-vien/ | 2026-08-03 / not-stated | 1,558 | audience, department, category, language |
| 11 | Mức học phí năm 2026–2027 | https://dsa.ueh.edu.vn/tin-tuc/thong-bao-ve-muc-hoc-phi-cac-he-dao-tao-nam-hoc-2026-2027-hoc-ky-cuoi-2026-hoc-ky-dau-2027-va-chinh-sach-ho-tro-hoc-phi-hoc-ky-cuoi-2026/ | 2026-08-03 / 2026-2027 | 1,076 | audience, department, category, language |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `ueh-student-card-services` | Định danh ổn định, khớp tên file; dùng cho `delete_document` và truy vết chunk |
| `title` | string | THẺ SINH VIÊN – Ban Chăm sóc người học | Hiển thị nguồn khi debug/agent trả lời |
| `source_url` | URL | https://dsa.ueh.edu.vn/... | Truy vết nguồn gốc, kiểm chứng gold answer |
| `retrieved_at` | date | 2026-08-03 | Biết dữ liệu lấy lúc nào |
| `document_version` | string | 2025-hoc-ky-cuoi / not-stated | Phân biệt thông báo theo học kỳ/năm |
| `audience` | enum | student / faculty / all | Lọc tài liệu theo đối tượng (`search_with_filter`) |
| `department` | string | dao-tao, thu-vien, ktx | Thu hẹp theo đơn vị quản lý |
| `category` | string | course-registration, scholarship | Phân loại chủ đề trong corpus |
| `language` | string | vi | Hỗ trợ lọc/so sánh đa ngôn ngữ nếu mở rộng |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu đại diện (ngắn / trung bình / dài). **Đã bỏ front matter** bằng `parse_front_matter()` trước khi so sánh; `chunk_size=500` cho `fixed_size` và `recursive`; `SentenceChunker(max_sentences_per_chunk=3)` như trong `bench.py`.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Kế hoạch đăng ký HK cuối 2025 (`ueh-course-registration-plan-hk-cuoi-2025`, 7.137 ký tự body) | FixedSizeChunker (`fixed_size`) | 15 | 476 | Một phần — cắt theo ký tự, bảng lịch đăng ký có thể tách giữa dòng |
| | SentenceChunker (`by_sentences`) | 15 | 474 | Khá — gom 3 câu/chunk, giữ câu trọn vẹn nhưng bullet dài vẫn gộp chung chunk |
| | RecursiveChunker (`recursive`) | 20 | 360 | Tốt hơn — ưu tiên `\n\n` / `\n`, phù hợp thông báo nhiều mục |
| Chính sách học bổng (`ueh-scholarship-policy-overview`, 12.732 ký tự body) | FixedSizeChunker | 26 | 490 | Một phần — chunk đều nhưng dễ cắt giữa bảng điều kiện xét bổng |
| | SentenceChunker | 20 | 634 | Khá — chunk dài hơn, giữ đoạn mô tả liền mạch; dễ trộn hai mục nếu câu ngắn |
| | RecursiveChunker | 35 | 364 | Tốt — tách theo đoạn, chunk nhỏ hơn, dễ trúng mục cụ thể |
| Thẻ sinh viên (`ueh-student-card-services`, 1.558 ký tự body) | FixedSizeChunker | 4 | 390 | Ổn — văn bản ngắn, ít mất ngữ cảnh |
| | SentenceChunker | 2 | 777 | Tốt — gần như cả quy trình 5 bước nằm trong 1–2 chunk |
| | RecursiveChunker | 4 | 396 | Ổn — tách theo heading con, quy trình Bước 1–5 vẫn gần nhau |

**Nhận xét baseline:** Với thông báo/quy định UEH (nhiều mục, bảng, bullet), `recursive` thường tạo nhiều chunk hơn nhưng giữ cấu trúc đoạn tốt hơn. `by_sentences` phù hợp văn bản mô tả liền mạch (quy trình ngắn) nhưng dễ gộp nhiều ý không liên quan trên tài liệu dài.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** Sentence (`SentenceChunker`)
- **Mô tả & lý do chọn cho chủ đề này:** Chọn chia theo câu (tối đa 3 câu/chunk) vì nhiều thông báo UEH viết theo câu điều kiện / hậu quả / quy trình từng bước — giữ trọn câu tránh cắt giữa “Sinh viên … sẽ bị …”. Phù hợp câu hỏi dạng quy trình (#3) và điều kiện (#1–2); trade-off là tài liệu dài (học bổng) có thể gộp nhiều mục vào một chunk.
- **Tham số:** `SentenceChunker(max_sentences_per_chunk=3)` — chạy `python bench.py --chunker sentences`
- **Kết quả nạp corpus:** 75 chunk (mock embedder); cần `EMBEDDING_PROVIDER=local` để đánh giá retrieval có nghĩa ở CP6.

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Thành viên 1 | SentenceChunker (`max_sentences_per_chunk=3`) | *(CP6 — chạy lại với `EMBEDDING_PROVIDER=local`)* | Chunk ít hơn recursive (75 vs 112); quy trình ngắn gom tốt | Mock embedder: 0/5 top-3; tài liệu dài dễ gộp nhiều mục |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng (ngoại lệ / điều kiện / quy trình / liệt kê / số liệu+filter), có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Bộ câu hỏi chung — **không đổi** sau khi thành viên đã chạy strategy. **Chạy:** `python bench.py` (query nằm trong `bench.py`).

| # | Loại | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk / doc kỳ vọng |
|---|------|-------|-------------------------------|--------------------------|
| 1 | ngoại lệ | Sinh viên có được đăng ký mã học phần đang chờ lịch thi hoặc chờ kết quả điểm thi không? | Không được phép đăng ký mã học phần đang chờ lịch thi hoặc chờ kết quả điểm thi. | `ueh-course-registration-plan-hk-cuoi-2025` |
| 2 | điều kiện | Sinh viên không nộp học phí đúng hạn trong kỳ đăng ký học kỳ cuối 2025 sẽ bị xử lý thế nào? | Bị xóa tên khỏi danh sách lớp đã đăng ký. | `ueh-course-registration-plan-hk-cuoi-2025` |
| 3 | quy trình | Các bước đăng ký cấp thẻ sinh viên nhựa tại UEH là gì? | B1 Cổng GTĐT → B2 điền thông tin → B3 thanh toán 100,000 đồng/1 thẻ → B4 CNTT in thẻ → B5 lấy thẻ A203 (chiều T3 / sáng T5). | `ueh-student-card-services` |
| 4 | liệt kê | UEH Smart Library cung cấp quyền truy cập những cơ sở dữ liệu học thuật quốc tế nào? | ScienceDirect, SpringerLink, Jora… | `ueh-library-reading-culture` |
| 5 | số liệu + filter `audience=student` | Buổi đào tạo trực tiếp của Thư viện UEH mang tên gì và có bao nhiêu người tham dự buổi đó? *(không nêu đối tượng)* | “Làm chủ kỹ năng tìm kiếm thông tin học thuật”; 59 sinh viên (Buổi 1). Không lọc dễ lẫn bản faculty: “Khai thác CSDL… UEH Mekong”; 64 giảng viên/viên chức. | `ueh-library-training-student` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | ngoại lệ — chờ lịch thi | *(chưa chốt)* | Sentence + mock: **Không** | CP5 smoke test; cần local embedder |
| 2 | trễ học phí | *(chưa chốt)* | Sentence + mock: **Không** | Top-1 lệch sang `ueh-course-registration-guide` |
| 3 | quy trình thẻ nhựa | *(chưa chốt)* | Sentence + mock: **Không** | Baseline cho thấy 2 chunk — kỳ vọng tốt hơn khi có embedding thật |
| 4 | CSDL quốc tế | *(chưa chốt)* | Sentence + mock: **Không** | |
| 5 | buổi đào tạo + filter | *(chưa chốt)* | Sentence + mock: **Không** | Filter `audience=student` đã bật; cần local để đo hiệu quả |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Dự kiến có ích ở câu #5: corpus có cặp `ueh-library-training-student` / `ueh-library-training-faculty` cùng chủ đề nhưng tên buổi và số liệu khác — không lọc `audience=student` dễ trả lời nhầm đối tượng. Kết quả CP6 sẽ so sánh `search()` vs `search_with_filter()` trên cùng embedder local.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
