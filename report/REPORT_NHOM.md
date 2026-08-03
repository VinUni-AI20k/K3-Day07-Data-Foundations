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

**Phạm vi cụ thể nhóm tập trung:** Dịch vụ sinh viên tại Đại học Kinh tế TP.HCM (UEH) — đăng ký học phần, học phí, học bổng, thư viện, ký túc xá, thẻ sinh viên.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định công tác tư vấn học tập | [daotao.ueh.edu.vn](https://daotao.ueh.edu.vn/quy-dinh-cong-tac-tu-van-hoc-tap-doi-voi-sinh-vien-he-dai-hoc-chinh-quy/) | 2026-08-03 / 2016-10-24 | 12.993 | audience=faculty, department=dao-tao, category=course-registration |
| 2 | Hướng dẫn đăng ký học phần trực tuyến | [daotao.ueh.edu.vn](https://daotao.ueh.edu.vn/thong-bao-huong-dan-dang-ky-hoc-phan-truc-tuyen-cho-sinh-vien-dhcq-ltdhcq-vb2dhcq/) | 2026-08-03 / not-stated | 1.182 | audience=student, department=dao-tao, category=course-registration |
| 3 | Kế hoạch đăng ký học phần & nộp học phí HK cuối 2025 | [daotao.ueh.edu.vn](https://daotao.ueh.edu.vn/thong-bao-ke-hoach-dang-ky-hoc-phan-va-nop-hoc-phi-hoc-ky-cuoi-nam-2025-doi-voi-sinh-vien-dai-hoc-chinh-quy-van-bang-2-lien-thong-dhcq-vua-lam-vua-hoc/) | 2026-08-03 / 2025-hoc-ky-cuoi | 7.137 | audience=student, department=dao-tao, category=course-registration |
| 4 | Khung thời gian thu nội trú phí KTX năm 2025 | [dsa.ueh.edu.vn](https://dsa.ueh.edu.vn/tin-tuc/thong-bao-khung-thoi-gian-thu-noi-tru-phi-ky-tuc-xa-ueh-nam-2025/) | 2026-08-03 / 2025 | 1.547 | audience=student, department=ktx, category=dormitory |
| 5 | Thu nội trú phí KTX Quý III/2026 | [dsa.ueh.edu.vn](https://dsa.ueh.edu.vn/tin-tuc/thong-bao-ve-viec-thu-noi-tru-phi-ky-tuc-xa-quy-iii-2026-thang-789-nam-2026/) | 2026-08-03 / 2026-q3 | 1.293 | audience=student, department=ktx, category=dormitory |
| 6 | Văn hoá đọc tại UEH (giới thiệu Smart Library) | [dsa.ueh.edu.vn](https://dsa.ueh.edu.vn/tin-tuc/van-hoa-doc-tai-ueh-khi-tri-thuc-tro-thanh-von-lieng-cua-nhung-nha-lanh-dao-tuong-lai/) | 2026-08-03 / not-stated | 6.778 | audience=student, department=thu-vien, category=library |
| 7 | Chính sách học bổng UEH (tổng quan) | [dsa.ueh.edu.vn](https://dsa.ueh.edu.vn/tin-tuc/chinh-sach-hoc-bong/) | 2026-08-03 / not-stated | 12.732 | audience=student, department=hoc-bong, category=scholarship |
| 8 | Quy định xét cấp học bổng khuyến khích học tập | [daotao.ueh.edu.vn](https://daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy/) | 2026-08-03 / not-stated | 5.283 | audience=student, department=hoc-bong, category=scholarship |
| 9 | Thẻ sinh viên — hướng dẫn & tiện ích | [dsa.ueh.edu.vn](https://dsa.ueh.edu.vn/chuyen-trang-ho-tro-dich-vu-tien-ich-ueh/the-sinh-vien/) | 2026-08-03 / not-stated | 1.558 | audience=student, department=dich-vu-sv, category=student-services |
| 10 | Mức học phí năm học 2026-2027 | [dsa.ueh.edu.vn](https://dsa.ueh.edu.vn/tin-tuc/thong-bao-ve-muc-hoc-phi-cac-he-dao-tao-nam-hoc-2026-2027-hoc-ky-cuoi-2026-hoc-ky-dau-2027-va-chinh-sach-ho-tro-hoc-phi-hoc-ky-cuoi-2026/) | 2026-08-03 / 2026-2027 | 1.076 | audience=student, department=tai-chinh, category=tuition |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai (`daotao.ueh.edu.vn`, `dsa.ueh.edu.vn`) và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. Crawl bằng `scripts/fetch_public_pages.py` (có kiểm `robots.txt`), sau đó làm sạch tay để loại menu/sidebar/tag-cloud của theme WordPress.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc `not-stated` nếu nguồn không nêu) trong metadata — đã verify bằng script checkpoint (10/10 OK, `sources.csv` khớp 1-1).

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `ueh-dorm-fee-2026-q3` | Trỏ về file gốc cho mọi chunk cùng tài liệu — cần để `delete_document()` và lọc theo tài liệu hoạt động đúng. |
| `audience` | enum (`student` / `faculty`) | `faculty` | **Bắt buộc theo K3** — phân biệt tài liệu dành cho sinh viên vs giảng viên/viên chức; 9/10 tài liệu là `student`, 1 tài liệu (`ueh-academic-advising-regulation`) là `faculty`. |
| `department` | string | `ktx`, `hoc-bong`, `dao-tao`, `tai-chinh`, `thu-vien`, `dich-vu-sv` | Lọc theo đơn vị phụ trách khi câu hỏi hỏi rõ phòng ban. |
| `category` | string | `dormitory`, `scholarship`, `course-registration`, `tuition`, `library`, `student-services` | Lọc theo chủ đề dịch vụ — dùng khi câu hỏi thuộc rõ 1 trong 5 mảng K3. |
| `document_version` | string | `2025`, `2026-q3`, `not-stated` | Phân biệt tài liệu **cùng chủ đề khác thời điểm hiệu lực** (ví dụ 2 thông báo KTX Quý III nhưng khác năm 2025/2026) — verify thực tế: không lọc thì lẫn tài liệu sai năm ở top-2/3. |
| `language` | string | `vi` | Toàn bộ corpus tiếng Việt; giữ field để mở rộng nếu nhóm thêm tài liệu tiếng Anh sau này. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=200)` trên 3 tài liệu (đã bỏ front matter trước khi so sánh, dùng `ingest.parse_front_matter` để tách):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| ueh-course-registration-plan-hk-cuoi-2025 (7.137 ký tự) | FixedSizeChunker | 48 | 197.6 | Không đảm bảo — cắt cứng theo ký tự, có thể đứt giữa câu/bảng thời gian đăng ký. |
| ueh-course-registration-plan-hk-cuoi-2025 | SentenceChunker | 15 | 474.1 | Tốt hơn — không cắt giữa câu, nhưng bảng số liệu (giờ đăng ký theo khóa) không có dấu câu rõ nên dễ gộp/tách sai chỗ. |
| ueh-course-registration-plan-hk-cuoi-2025 | RecursiveChunker | 52 | 135.6 | Tốt nhất về ranh giới tự nhiên (ưu tiên `\n\n`/`\n`) nhưng chunk ngắn hơn cả FixedSize — có thể mất ngữ cảnh nếu 1 điều kiện bị tách khỏi phần giải thích. |
| ueh-scholarship-policy-overview (12.732 ký tự) | FixedSizeChunker | 85 | 199.2 | Tài liệu có bảng Markdown (điều kiện xét học bổng) — cắt cứng dễ xé bảng giữa dòng. |
| ueh-scholarship-policy-overview | SentenceChunker | 20 | 634.2 | Chunk dài hơn hẳn — giữ được nhiều ngữ cảnh nhưng có thể vượt quá kích thước hữu ích cho embedding. |
| ueh-scholarship-policy-overview | RecursiveChunker | 94 | 133.8 | Chunk nhỏ nhất — tách theo đoạn `\n\n` khớp tốt với cấu trúc "1. Học bổng...", "2. Học bổng..." của tài liệu gốc. |
| ueh-dorm-fee-2025 (1.547 ký tự, tài liệu ngắn) | FixedSizeChunker | 10 | 199.7 | — |
| ueh-dorm-fee-2025 | SentenceChunker | 1 | 1546.0 | Tài liệu ngắn nên gộp thành 1 chunk duy nhất — mất khả năng phân biệt Quý 1/2/3/4 khi retrieval. |
| ueh-dorm-fee-2025 | RecursiveChunker | 12 | 127.4 | — |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Đào Ngọc Bích**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=500, overlap=50` — baseline mặc định của bài, đang thử nghiệm tune `overlap`)
- **Mô tả & lý do chọn cho chủ đề này:** Chọn FixedSize làm điểm neo baseline vì đơn giản, dễ giải thích và dễ so sánh định lượng với 2 chiến lược còn lại của nhóm. Nhược điểm quan sát được: với các tài liệu dạng "Quy định" có cấu trúc Điều/Khoản (ví dụ `ueh-scholarship-regulation`, `ueh-academic-advising-regulation`), cắt cứng theo ký tự có nguy cơ tách một Điều khỏi phần liệt kê điều kiện của nó.
- **Code snippet (nếu custom):** *(không áp dụng — dùng nguyên `FixedSizeChunker` có sẵn trong `src/chunking.py`)*

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 4 — [Tên]**
- **Loại chiến lược:** Custom chunker theo heading/section *(bắt buộc theo K3_VARIANT.md — ít nhất 1 thành viên phải làm phần này)*
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy — copy nguyên văn từ `bench.py` (`--list` để in lại).

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 (ngoại lệ) | Sinh viên có được đăng ký mã học phần đang chờ lịch thi hoặc chờ kết quả điểm thi không? | Không được phép đăng ký mã học phần đang chờ lịch thi hoặc chờ kết quả điểm thi. | `ueh-course-registration-plan-hk-cuoi-2025` |
| 2 (điều kiện) | Sinh viên không nộp học phí đúng hạn trong kỳ đăng ký học kỳ cuối 2025 sẽ bị xử lý thế nào? | Bị xóa tên khỏi danh sách lớp đã đăng ký. | `ueh-course-registration-plan-hk-cuoi-2025` |
| 3 (quy trình) | Các bước đăng ký cấp thẻ sinh viên nhựa tại UEH là gì? | 5 bước: truy cập Cổng giao dịch điện tử → điền thông tin → thanh toán 100.000đ/thẻ → Phòng CNTT in thẻ cuối ngày → nhận email và lấy thẻ tại A203, 59C Nguyễn Đình Chiểu. | `ueh-student-card-services` |
| 4 (liệt kê) | UEH Smart Library cung cấp quyền truy cập những cơ sở dữ liệu học thuật quốc tế nào? | ScienceDirect, SpringerLink, Jora… | `ueh-library-reading-culture` |
| 5 (số liệu + **filter bắt buộc**) | Thời gian thanh toán nội trú phí KTX UEH Quý III (tháng 7, 8, 9) là khi nào? — cần `metadata_filter={"document_version": "2026-q3"}` | Từ 00h00 ngày 01/7/2026 đến 23h59 ngày 13/7/2026. | `ueh-dorm-fee-2026-q3` |

> ⚠️ **Lưu ý tuân thủ K3:** `K3_VARIANT.md` yêu cầu tên field cụ thể `metadata_filter={"audience": "student"}`. Query #5 ở trên dùng `document_version` (đã verify A/B: không filter thì lẫn tài liệu sai năm 2025 ở top-2/3) chứ chưa dùng đúng field `audience`. Đã tìm được 1 câu hỏi thật minh hoạ đúng field `audience` (không cần bịa dữ liệu): *"Sinh viên cần liên hệ ai để được tư vấn học tập, xây dựng kế hoạch học tập phù hợp?"* — verify bằng local embedder: không filter thì top-5 đều là tài liệu `faculty` (`ueh-academic-advising-regulation`, tài liệu duy nhất có thông tin này); filter `audience=student` thì loại nhầm tài liệu đúng, top-3 chuyển sang 2 tài liệu học bổng sai chủ đề. Nhóm cần quyết định: thêm câu này thành query #6 chính thức, hay thay query #3, trước khi chốt bảng trên.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

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
