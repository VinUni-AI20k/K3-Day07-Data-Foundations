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

Chạy `ChunkingStrategyComparator().compare(chunk_size=200)` trên 3 tài liệu đại diện (ngắn/trung/dài), **đã bóc front matter** trước khi so sánh (dùng `ingest.load_documents()` — `Document.content` chỉ còn phần thân, không lẫn khối YAML):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `huong-dan-dang-ky-hoc-phan` (2,062 ký tự) | FixedSizeChunker (`fixed_size`) | 14 | 193.7 | Không đảm bảo — cắt cứng theo ký tự, có thể chặt giữa câu |
| `huong-dan-dang-ky-hoc-phan` | SentenceChunker (`by_sentences`) | 5 | 409.6 | Có, trọn câu — nhưng chunk to gần gấp đôi fixed_size, dễ gộp nhiều ý không liên quan vào 1 chunk |
| `huong-dan-dang-ky-hoc-phan` | RecursiveChunker (`recursive`) | 16 | 127.1 | Có, ưu tiên `\n\n`/câu trước khi cắt cứng — chunk nhỏ nhất trong 3 chiến lược nên giữ ngữ cảnh cục bộ tốt nhưng dễ mất ngữ cảnh rộng hơn |
| `che-do-hoc-bong-sinh-vien` (3,186 ký tự) | FixedSizeChunker | 21 | 199.3 | Không đảm bảo |
| `che-do-hoc-bong-sinh-vien` | SentenceChunker | 7 | 452.6 | Có, trọn câu |
| `che-do-hoc-bong-sinh-vien` | RecursiveChunker | 25 | 125.9 | Có, ưu tiên ranh giới tự nhiên |
| `quy-che-dao-tao-tin-chi` (39,962 ký tự — văn bản quy chế có `CHƯƠNG`/`Điều N.`) | FixedSizeChunker | 267 | 199.5 | Không — với văn bản pháp quy nhiều `Điều`, cắt cứng dễ chặt đôi 1 điều khoản giữa chừng |
| `quy-che-dao-tao-tin-chi` | SentenceChunker | 84 | 473.7 | Có, trọn câu nhưng không tôn trọng ranh giới `Điều` — 1 chunk có thể lẫn cuối `Điều` này với đầu `Điều` sau |
| `quy-che-dao-tao-tin-chi` | RecursiveChunker | 282 | 140.0 | Có, ưu tiên `\n\n` trước — với văn bản dài nhiều đoạn ngắn thì vẫn có thể cắt giữa 1 `Điều` nếu đoạn đó dài hơn `chunk_size` |

**Nhận xét:** Cả 3 chiến lược built-in đều **không nhận biết ranh giới `Điều`/`CHƯƠNG`** của văn bản quy chế — đây chính là lý do một thành viên (xem "Chiến lược của từng thành viên" bên dưới) viết `HeadingChunker` tùy chỉnh tách theo heading trước khi mới cắt tiếp theo đoạn.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — Trần Văn Hiếu**
- **Loại chiến lược:** custom — `HeadingChunker` (`src/heading_chunker.py`)
- **Mô tả & lý do chọn cho chủ đề này:** `quy-che-dao-tao-tin-chi.md` là văn bản quy chế học vụ được biên soạn sẵn theo `CHƯƠNG`/`Điều N.` — mỗi `Điều` đã là một đơn vị ngữ nghĩa trọn vẹn (một quy định). `HeadingChunker` tách trước tại các dòng heading (`#`, `CHƯƠNG ...`, `Điều N. ...`), section nào vẫn dài hơn `chunk_size` mới hạ xuống cắt theo đoạn (`\n\n`) — và **gắn lại dòng heading vào đầu mỗi mảnh con** để mảnh thứ 2 trở đi không mất ngữ cảnh "mình thuộc Điều nào" (bug này từng khiến 1/5 câu benchmark thất bại hoàn toàn trước khi sửa — xem `REPORT_CANHAN.md` Mục 5). Baseline `ChunkingStrategyComparator` (dùng `chunk_size=200`) cho thấy cả 3 chiến lược có sẵn đều không nhận biết ranh giới `Điều`, nên đây là chiến lược bổ sung đúng khoảng trống đó, đồng thời đáp ứng yêu cầu riêng của K3_VARIANT.md ("ít nhất một thành viên thử chia theo tiêu đề/mục của quy định học vụ").
- **Code snippet:**
```python
class HeadingChunker:
    """Tách theo heading/section (markdown #, CHƯƠNG, Điều N.) thay vì theo size.
    Section dài hơn chunk_size mới hạ xuống cắt theo đoạn, và heading được
    gắn lại vào đầu mỗi mảnh con để không mất ngữ cảnh."""

    HEADING_PATTERN = re.compile(
        r"^(#{1,6}\s+.+|CHƯƠNG\s+[IVXLCDM\d]+.*|Điều\s+\d+\..*)$",
        re.MULTILINE,
    )

    def __init__(self, chunk_size: int = 800) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        matches = list(self.HEADING_PATTERN.finditer(text))
        if not matches:
            return self._split_long(text.strip())
        chunks = []
        if matches[0].start() > 0:
            chunks.extend(self._split_long(text[: matches[0].start()].strip()))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section = text[m.start():end].strip()
            if section:
                chunks.extend(self._split_section(section))
        return chunks

    def _split_section(self, section: str) -> list[str]:
        if len(section) <= self.chunk_size:
            return [section]
        heading, _, body = section.partition("\n")
        pieces = self._split_long(body.strip())
        return [f"{heading}\n\n{p}" for p in pieces] if pieces else [heading]
    # _split_long: gộp đoạn (\n\n) tới sát chunk_size, y hệt RecursiveChunker._split
```
> Bản đầy đủ (có `_split_long`, docstring giải thích thiết kế) ở `src/heading_chunker.py`.

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
| 1 | Sinh viên đăng ký học phần ở website nào và cần lưu ý gì trước khi đăng ký? | Đăng ký tại `https://dkhp.iuh.edu.vn/`, đăng nhập bằng tài khoản Cổng thông tin sinh viên. Trước khi đăng ký phải xem chương trình khung, đăng ký đúng mã lớp học phần / tên môn / số tín chỉ, và kiểm tra các điều kiện ràng buộc của môn học. | `huong-dan-dang-ky-hoc-phan` |
| 2 | Sinh viên nộp học phí trực tuyến bằng những cách nào? | Hai cách: (a) qua Agribank / NamAbank / Vietcombank — nộp tại quầy (cung cấp mã số sinh viên) hoặc gạch nợ trực tiếp trên app ngân hàng; (b) nộp online áp dụng cho **mọi** ngân hàng qua `https://sv.iuh.edu.vn/sinh-vien-dang-nhap.html`. | `huong-dan-nop-hoc-phi-truc-tuyen` |
| 3 | Mức học bổng khuyến khích học tập tối đa là bao nhiêu? | Lên tới **130% học phí**, xét cho sinh viên đại học hệ chính quy đang trong thời gian học tập chính khóa (theo Quyết định 2728/QĐ-ĐHCN ngày 23/11/2023). | `che-do-hoc-bong-sinh-vien` (chunk 3) |
| 4 | Kho sách ngoại văn của thư viện nằm ở tầng nào? | **Lầu 3**. (Lầu 4 là kho luận văn, đồ án tốt nghiệp, tạp chí chuyên ngành.) | `huong-dan-su-dung-thu-vien` |
| 5 | *(cần lọc metadata)* Sinh viên bị ốm phải điều trị dài ngày thì việc học được giải quyết thế nào? — chạy với `metadata_filter={"audience": "student"}` | Được nộp đơn xin **nghỉ học tạm thời** và bảo lưu kết quả học tập, gửi Phòng Đào tạo trình Ban Giám hiệu phê duyệt, kèm chứng nhận của cơ sở khám chữa bệnh có thẩm quyền theo quy định của Bộ Y tế. | `quy-dinh-nghi-hoc-tam-thoi` |

**Vì sao câu 5 cần lọc metadata (đã đo, không phải suy đoán):** không lọc thì hạng 2 là `tu-van-tam-ly-cham-soc-suc-khoe` (score 0.531, `audience=all`) — tài liệu này nói về trạm y tế và bảo hiểm y tế, **trùng nhiều từ khóa** ("ốm", "sức khỏe", "điều trị") nhưng không trả lời được câu hỏi về *việc học*. Lọc `audience=student` loại đúng nhiễu này và thay bằng `quy-che-dao-tao-tin-chi` (0.523) là văn bản học vụ thực sự liên quan.

> ⚠️ **Bài học ngược, đáng ghi cho mục 4:** bộ lọc **không phải lúc nào cũng tốt**. Với câu "Sinh viên cần mang theo giấy tờ gì khi vào trường?", đáp án đúng nằm ở `noi-quy-hoc-duong` (`audience=all`, score 0.675 — "không đeo thẻ sinh viên…"), và lọc `audience=student` **xóa mất chính đáp án đó**. Đây là đánh đổi precision/recall mà `docs/EVALUATION.md` mục 3 yêu cầu phân tích: lọc chỉ giúp khi tài liệu `all` là nhiễu, và gây hại khi tài liệu `all` chính là nguồn trả lời.

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
