# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** VinBrothers
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Dịch vụ và quy định học vụ dành cho người học của **một trường duy nhất** (Trường Đại học Công nghiệp TP.HCM — IUH), lấy từ trang "Cẩm nang người học" công khai: đăng ký học phần & quy chế tín chỉ, học phí (miễn giảm + nộp trực tuyến), học bổng, thư viện, nội quy học đường, nghỉ học tạm thời, hỗ trợ sinh viên. Chọn **một trường** là có chủ ý: nếu trộn nhiều trường thì cùng một câu hỏi ("thời hạn nghỉ học tạm thời tối đa?") sẽ có nhiều câu trả lời chuẩn xung đột nhau, không đánh giá được retrieval.

### Danh sách tài liệu (Data Inventory)

Thu thập bằng `scripts/fetch_public_pages.py` (tự kiểm tra `robots.txt` — `camnang.iuh.edu.vn` trả `Allow: /`, chờ ≥1s/request, chỉ nhận HTML/text công khai). Danh sách URL tái lập được lưu ở [`data/urls.csv`](../data/urls.csv); bảng kiểm kê máy đọc được ở [`data/k3_university/sources.csv`](../data/k3_university/sources.csv).

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Chế độ học bổng dành cho sinh viên (`che-do-hoc-bong-sinh-vien`) | https://camnang.iuh.edu.vn/che-do-hoc-bong-danh-cho-sinh-vien.php | 2026-08-03 / not-stated | 3,186 | audience=student, department=student-affairs, category=scholarship, language=vi |
| 2 | Chính sách miễn giảm học phí và hỗ trợ chi phí học tập (`chinh-sach-mien-giam-hoc-phi`) | https://camnang.iuh.edu.vn/chinh-sach-mien-giam-hoc-phi-va-ho-tro-chi-phi-hoc-tap.php | 2026-08-03 / not-stated | 4,973 | audience=student, department=student-affairs, category=tuition-policy, language=vi |
| 3 | Hướng dẫn đăng ký học phần (`huong-dan-dang-ky-hoc-phan`) | https://camnang.iuh.edu.vn/huong-dan-dang-ky-hoc-phan.php | 2026-08-03 / not-stated | 2,062 | audience=student, department=academic-affairs, category=course-registration, language=vi |
| 4 | Hướng dẫn nộp học phí trực tuyến (`huong-dan-nop-hoc-phi-truc-tuyen`) | https://camnang.iuh.edu.vn/huong-dan-nop-tien-hoc-phi-bang-hinh-thuc-truc-tuyen.php | 2026-08-03 / not-stated | 2,159 | audience=student, department=finance, category=tuition-payment, language=vi |
| 5 | Hướng dẫn sử dụng thư viện (`huong-dan-su-dung-thu-vien`) | https://camnang.iuh.edu.vn/huong-dan-su-dung-thu-vien.php | 2026-08-03 / not-stated | 1,681 | audience=**all**, department=library, category=library-service, language=vi |
| 6 | Nội quy học đường (`noi-quy-hoc-duong`) | https://camnang.iuh.edu.vn/noi-quy-hoc-duong.php | 2026-08-03 / not-stated | 3,182 | audience=**all**, department=student-affairs, category=campus-rule, language=vi |
| 7 | Quy chế đào tạo theo hệ thống tín chỉ (`quy-che-dao-tao-tin-chi`) | https://camnang.iuh.edu.vn/quy-che-dao-tao-theo-he-thong-tin-chi.php | 2026-08-03 / not-stated | 39,962 | audience=student, department=academic-affairs, category=academic-regulation, language=vi |
| 8 | Quy định về nghỉ học tạm thời và bảo lưu kết quả học tập (`quy-dinh-nghi-hoc-tam-thoi`) | https://camnang.iuh.edu.vn/quy-dinh-ve-nghi-hoc-tam-thoi-va-bao-luu-ket-qua-hoc-tap.php | 2026-08-03 / not-stated | 1,649 | audience=student, department=academic-affairs, category=leave-of-absence, language=vi |
| 9 | Tư vấn tâm lý và chăm sóc sức khỏe (`tu-van-tam-ly-cham-soc-suc-khoe`) | https://camnang.iuh.edu.vn/tu-van-tam-ly-cham-soc-suc-khoe.php | 2026-08-03 / not-stated | 1,190 | audience=**all**, department=student-affairs, category=student-support, language=vi |

**Tổng:** 9 tài liệu / 60,044 ký tự → 135 chunk với `FixedSizeChunker(500, 50)`.

**Ghi chú về làm sạch dữ liệu:**
- `document_version = not-stated` cho cả 9 tài liệu: nguồn **không công bố** ngày hiệu lực/phiên bản. Ghi `not-stated` theo đúng `docs/DATA_COLLECTION.md` thay vì tự suy đoán một con số.
- Đã bỏ khỏi phần nội dung: breadcrumb (`Trang chủ` / `Học tập tại IUH`), tiêu đề site lặp lại, và khối sidebar `Bài phổ biến nhất` / `Bài viết liên quan` ở cuối mỗi trang — nếu để lại, các chunk cuối tài liệu sẽ chỉ chứa danh sách link và làm loãng retrieval.
- **Một trang bị loại:** `quy-trinh-phuc-khao-diem.php` — sau khi bỏ boilerplate còn **0 ký tự** nội dung thật (quy trình không nằm trong HTML text), nên không dùng làm nguồn benchmark được.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. → 9/9 trang công khai, không cần đăng nhập; `robots.txt` cho phép; `license_or_permission=public-page`.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. → đã kiểm bằng script checklist mục 6 (`docs/DATA_COLLECTION.md`): 9/9 file OK, `sources.csv` khớp 1–1.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | str | `huong-dan-su-dung-thu-vien` | Khóa định danh ổn định, trùng tên file. `ingest.py` gắn lên **từng chunk** nên `delete_document()` xóa được trọn tài liệu và truy vết được chunk về nguồn. |
| `audience` | str | `student` \| `all` | **Trường phân vai bắt buộc của K3.** Lọc `{"audience": "student"}` loại các văn bản áp dụng chung, tránh trả về quy định không dành cho đối tượng đang hỏi. Corpus có 6 `student` / 3 `all` nên bộ lọc thực sự có việc để làm. |
| `department` | str | `library`, `finance`, `academic-affairs`, `student-affairs` | Khoanh vùng theo đơn vị phụ trách. Hữu ích khi câu hỏi lẫn từ khóa giữa các miền (ví dụ "học phí" xuất hiện cả trong văn bản học bổng lẫn văn bản thanh toán). |
| `category` | str | `scholarship`, `tuition-payment`, `leave-of-absence` | Nhãn mịn hơn `department`, dùng để tách hai tài liệu cùng đơn vị nhưng khác mục đích (miễn giảm học phí vs hướng dẫn nộp học phí). |
| `source_url` | str | `https://camnang.iuh.edu.vn/...` | Truy vết nguồn để đối chiếu gold answer; `KnowledgeBaseAgent` in kèm nguồn trong ngữ cảnh nên kiểm chứng được câu trả lời. |
| `retrieved_at` | str `YYYY-MM-DD` | `2026-08-03` | Biết dữ liệu cũ tới mức nào. Cần thiết vì embedding **không** mã hóa phủ định — nó không phân biệt được quy định còn hiệu lực với quy định đã bị thay thế. |
| `document_version` | str | `not-stated` | Phiên bản/ngày hiệu lực khi nguồn có công bố; ghi `not-stated` khi không có, để không ngụy tạo độ tin cậy. |
| `language` | str | `vi` | Sẵn sàng cho corpus song ngữ: embedder đa ngữ khớp chéo VI↔EN (đo được 0.866 giữa một cặp câu cùng ý), nên cần trường này để lọc theo ngôn ngữ khi cần. |
| `chunk_index` | int | `0`, `1`, `2`… | Do `ingest.chunk_document()` tự gắn. Cho biết chunk nằm ở đâu trong tài liệu → ghép lại được ngữ cảnh liền kề khi câu trả lời bị cắt qua ranh giới chunk. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

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
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

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
