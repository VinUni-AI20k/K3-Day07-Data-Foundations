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
| `huong-dan-dang-ky-hoc-phan` (2.062 ký tự) | FixedSizeChunker (`fixed_size`) | 5 | 452.4 | Cắt giữa câu; URL `dkhp.iuh.edu.vn` tách rời phần "Lưu ý" thao tác |
| | SentenceChunker (`by_sentences`) | 5 | 409.6 | Mỗi chunk trọn câu, dễ đọc nhất |
| | RecursiveChunker (`recursive`) | 5 | 410.8 | Bám ranh giới đoạn, tương đương sentence ở tài liệu ngắn |
| `huong-dan-su-dung-thu-vien` (1.681 ký tự) | FixedSizeChunker | 4 | 457.8 | Giữ nguyên khối "kho sách theo tầng" trong một chunk → trả lời tốt Q4 |
| | SentenceChunker | 5 | 333.0 | Chunk ngắn nhất; danh sách tầng bị tách nhỏ hơn |
| | RecursiveChunker | 4 | 418.8 | Tương đương fixed-size |
| `quy-che-dao-tao-tin-chi` (39.962 ký tự) | FixedSizeChunker | 89 | 498.5 | Chunk dày, ít mảnh vụn |
| | SentenceChunker | 84 | 473.7 | Ít chunk nhất → tài liệu dài ít lấn át hơn |
| | RecursiveChunker | **106** | 375.1 | **Nhiều mảnh vụn nhất** — văn bản quy chế nhiều xuống dòng nên `\n\n`/`\n` cắt vụn |

> **Nhận xét quan trọng từ baseline:** `quy-che-dao-tao-tin-chi` một mình chiếm **~2/3 toàn bộ corpus** (39.962 / 60.044 ký tự). Với `RecursiveChunker`, nó sinh 106 chunk — nghĩa là tài liệu này chiếm phần lớn không gian tìm kiếm và dễ "át" 8 tài liệu ngắn còn lại. Đây chính là nguyên nhân gốc của failure case ở mục 4.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Trương Công Thái Đức (2A202601581)**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)` — đường cơ sở
- **Mô tả & lý do chọn:** Cắt đều theo ký tự với overlap 10%. Chọn làm baseline vì đây là chiến lược duy nhất **không phụ thuộc cấu trúc văn bản** — corpus của nhóm là trang web đã làm sạch, định dạng không đồng nhất (có tài liệu dùng danh sách gạch đầu dòng, có tài liệu là đoạn văn dài), nên một mốc so sánh trung tính là cần thiết. Overlap 50 ký tự để câu bị cắt qua ranh giới vẫn xuất hiện trọn trong một chunk.

**Thành viên 2 — Trần Trung Hiếu (2A202602002)**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=500)`
- **Mô tả & lý do chọn:** Ưu tiên ranh giới tự nhiên `\n\n` → `\n` → `". "` → `" "`, kỳ vọng giữ trọn từng điều khoản của văn bản quy chế.

**Thành viên 3 — [Tên]**
- **Loại chiến lược:** *(đề xuất: `SentenceChunker` hoặc chunk theo heading — số liệu `SentenceChunker(3)` dưới đây do Thành viên 1 đo trước để nhóm có mốc so sánh, cần thành viên 3 xác nhận lại bằng code của mình)*
- **Mô tả & lý do chọn:**

### So Sánh Giữa Các Thành Viên

> **Cách chấm:** 2 điểm/câu theo `docs/SCORING.md`. Chấm ở **mức chunk**: mỗi câu hỏi được khai báo trước một **chuỗi bằng chứng** bắt buộc phải xuất hiện trong context top-3 (`dkhp.iuh.edu.vn`, `tất cả ngân hàng`, `130%`, `Lầu 3`, `Bộ Y tế`). Cùng corpus 9 tài liệu, cùng 5 câu hỏi, cùng `EMBEDDING_PROVIDER=local`, `top_k=3`.

| Thành viên | Chiến lược | Số chunk | Doc-level (/10) | **Chunk-level (/10)** | Điểm mạnh | Điểm yếu |
|-----------|----------|---------|-----------------|----------------------|-----------|----------|
| Thái Đức | `FixedSize(500, 50)` | 135 | 10 | **9** | Chunk dày, tài liệu ngắn không bị lép vế; thắng rõ ở Q5 (0.573, top-1 đúng) | Cắt giữa câu; ở Q1 tách URL khỏi phần hướng dẫn thao tác |
| Trần Trung Hiếu | `Recursive(500)` | 162 | 9 | **6** | Giữ ranh giới đoạn tốt; thắng ở Q2 (0.706 vs 0.670) | Cắt vụn văn bản dài (106/162 chunk là quy chế) → nhiều chunk chung chung chen top-3 |
| *(chưa nhận)* | `Sentence(3 câu)` | 137 | 8 | **8** | Chunk trọn câu, mạch lạc nhất; **không chênh** giữa hai cách chấm | Yếu nhất ở doc-level; Q5 không có tài liệu gold nào trong top-3 |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> `FixedSizeChunker(500, 50)` cho điểm cao nhất (**9/10** ở mức chunk), nhưng kết luận đáng giá hơn nằm ở **khoảng cách giữa hai cách chấm**: nếu chỉ kiểm `doc_id` gold có xuất hiện trong top-3 hay không thì Recursive được 9/10, nhưng khi bắt buộc context phải **chứa chuỗi trả lời**, nó rơi xuống 6/10 — **mất 3 điểm**. Lý do: Recursive cắt vụn `quy-che-dao-tao-tin-chi` thành 106 chunk cùng chủ đề, các chunk này điểm sát nhau (0.528 / 0.506 / 0.504 ở Q5) nên chiếm hết top-3 bằng đúng tài liệu mà **không chunk nào chứa đáp án**. Điểm cosine cao chỉ là tín hiệu *cùng chủ đề*, không phải bằng chứng *có câu trả lời*.
>
> Ngược lại `SentenceChunker` là chiến lược **duy nhất không chênh lệch** (8 = 8): chunk trọn câu nên hễ tài liệu đúng lọt top-3 thì đáp án cũng nằm trong đó. Nó thua về điểm tuyệt đối nhưng **đáng tin cậy nhất** — nếu ưu tiên không trả lời sai hơn là trả lời được nhiều, đây mới là lựa chọn đúng.
>
> Bài học chung: overlap quan trọng hơn thuật toán cắt. Cả ba chiến lược đều **hỏng ở Q1** vì URL `dkhp.iuh.edu.vn` và phần "Lưu ý" thao tác nằm ở hai chunk khác nhau, mà chỉ FixedSize có overlap — và 50 ký tự vẫn không đủ để bắc cầu.

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

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk **chứa đáp án** trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Đăng ký học phần ở website nào | *không chiến lược nào đạt* (cả 3 đều 1đ) | ❌ **Không** — cả 3 chiến lược đều trượt chuỗi `dkhp.iuh.edu.vn` | Failure case chính của nhóm, phân tích ở mục 4 |
| 2 | Nộp học phí trực tuyến | **FixedSize** (2đ) | ✅ chỉ FixedSize | Sentence & Recursive đều đưa `quy-che-dao-tao-tin-chi` chen vào hạng 2–3 |
| 3 | Mức học bổng tối đa | **FixedSize / Sentence** (2đ) | ✅ 2/3 chiến lược | Recursive: chuỗi `130%` rơi xuống hạng 2 (chunk 4) do cắt vụn hơn |
| 4 | Kho sách ngoại văn tầng nào | **cả 3** (2đ) | ✅ 3/3 | Câu dễ nhất — khối "kho sách theo tầng" ngắn, nằm gọn trong 1 chunk ở mọi chiến lược |
| 5 | Ốm dài ngày *(có lọc)* | **FixedSize** (2đ) | ✅ chỉ FixedSize | Recursive để `quy-che` chiếm 2 slot đầu; Sentence lấy đáp án từ **tài liệu khác** (xem ghi chú dưới) |

**Tổng điểm theo từng chiến lược:** FixedSize **9/10** · Sentence **8/10** · Recursive **6/10**

> **Ghi chú về Q5 và chuỗi bằng chứng:** chuỗi `Bộ Y tế` xuất hiện ở **hai** tài liệu — `quy-dinh-nghi-hoc-tam-thoi` (gold) và `quy-che-dao-tao-tin-chi` (điều khoản tương ứng trong quy chế). Với `SentenceChunker`, top-3 toàn là `quy-che-dao-tao-tin-chi` nhưng vẫn chứa đáp án đúng, nên vẫn tính 2 điểm. Đây là ca đáng lưu ý: **gold doc không phải nguồn duy nhất trả lời được**, nên chấm bằng `doc_id` sẽ báo sai là thất bại.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, nhưng **không đồng đều giữa các chiến lược** — nhóm chạy A/B (có filter vs không filter) trên cả 3:
>
> | Chiến lược | Không lọc (hạng 1–2) | Có lọc `audience=student` | Kết luận |
> |---|---|---|---|
> | FixedSize | 0.573 gold · **0.531 `tu-van-tam-ly` (all)** | 0.573 gold · 0.523 `quy-che` | Lọc **đẩy được nhiễu** khỏi hạng 2 |
> | Recursive | **0.566 `tu-van-tam-ly` (all) đứng hạng 1** · 0.528 `quy-che` | 0.528 `quy-che` · 0.506 `quy-che` | Lọc **cứu** trường hợp nhiễu chiếm hạng 1 |
> | Sentence | 3 kết quả đều `audience=student` | **giống hệt** | Lọc **không đổi gì** |
>
> Với `SentenceChunker`, hai kết quả **trùng khớp hoàn toàn** vì cả top-3 vốn đã là tài liệu `student`. Điều này cho thấy giá trị của metadata filter **phụ thuộc vào chiến lược chunking**, không phải thuộc tính cố định của câu hỏi: chunker nào để tài liệu `audience=all` lọt top-3 thì mới cần lọc.
>
> Và như đã ghi ở trên, lọc có mặt trái: ở câu "cần mang giấy tờ gì khi vào trường", đáp án nằm trong tài liệu `audience=all` nên lọc `student` **xóa mất đáp án**.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. **Chấm bằng `doc_id` làm đẹp điểm một cách giả tạo.** Cùng một bộ kết quả, `RecursiveChunker` được **9/10** nếu chỉ hỏi "gold doc có trong top-3 không", nhưng chỉ **6/10** khi bắt buộc context phải chứa chuỗi trả lời. Chênh 3 điểm. Nguyên nhân: nó chiếm trọn top-3 bằng đúng tài liệu gold mà không chunk nào chứa đáp án.
2. **Giá trị của metadata filter phụ thuộc chiến lược chunking, không phải câu hỏi.** Cùng câu Q5: với Recursive, lọc *cứu* kết quả (nhiễu `audience=all` đang đứng hạng 1); với FixedSize, lọc *cải thiện nhẹ*; với Sentence, lọc **không đổi gì** vì top-3 vốn đã đúng nhóm đối tượng.
3. **Overlap quan trọng hơn thuật toán cắt.** Cả 3 chiến lược đều thất bại ở Q1 vì URL và phần hướng dẫn thao tác nằm ở hai chunk khác nhau — chỉ FixedSize có overlap, và 50 ký tự vẫn không đủ bắc cầu.

### Failure case (bằng chứng từ top-k)

**Câu hỏi:** *"Sinh viên đăng ký học phần ở website nào và cần lưu ý gì trước khi đăng ký?"*
**Chuỗi bằng chứng cần có:** `dkhp.iuh.edu.vn`

**Bằng chứng top-3 (FixedSize, `EMBEDDING_PROVIDER=local`):**

| Hạng | Score | Tài liệu | chunk | Chứa `dkhp.iuh.edu.vn`? |
|---|---|---|---|---|
| 1 | 0.815 | `huong-dan-dang-ky-hoc-phan` | 2 | ❌ |
| 2 | 0.714 | `quy-che-dao-tao-tin-chi` | 20 | ❌ |
| 3 | 0.695 | `quy-che-dao-tao-tin-chi` | 23 | ❌ |

Mở rộng lên `top_k=5` vẫn không có: hạng 4 là `huong-dan-dang-ky-hoc-phan` chunk 3 (0.690), hạng 5 là chunk 0 (0.659). **Chunk chứa URL là chunk 1 — không lọt top-5.** Cả `Sentence` và `Recursive` cũng trượt câu này.

**Nguyên nhân:** tài liệu gốc viết URL ở một câu riêng ("Sinh viên đăng ký các học phần qua Website của Trường https://dkhp.iuh.edu.vn/"), còn phần "Lưu ý" hướng dẫn thao tác nằm ngay sau. Câu hỏi có hai vế — "website nào" *và* "lưu ý gì" — nhưng vế thứ hai dài hơn, nhiều từ khóa hơn, nên **chunk hướng dẫn thao tác thắng áp đảo** chunk chứa URL. Cosine đo độ giống chủ đề, không đo mật độ thông tin trả lời được: chunk 2 giống câu hỏi *về mặt chủ đề* hơn, dù chunk 1 mới chứa dữ kiện được hỏi.

**Đề xuất sửa (3 hướng, theo thứ tự ưu tiên):**
1. **Chunk theo heading/mục** (gợi ý K3 trong `K3_VARIANT.md`) — gom trọn một quy trình gồm cả URL lẫn các bước vào một chunk. Đây là hướng nhóm sẽ thử tiếp.
2. **Tăng overlap** lên ~150–200 ký tự để URL và phần "Lưu ý" cùng nằm trong ít nhất một chunk.
3. **Tách câu hỏi hai vế thành hai truy vấn** rồi gộp kết quả — sửa ở tầng truy vấn thay vì tầng dữ liệu.

**Một lỗi grounding khác đáng nêu:** ở Q2, chuỗi `sv.iuh.edu.vn` xuất hiện ở hạng 3 nhưng thuộc **tài liệu khác** (`chinh-sach-mien-giam-hoc-phi`, không phải tài liệu học phí). Agent vẫn trả lời đúng nhưng **dẫn nguồn sai tài liệu** — đúng loại lỗi mà tiêu chí *Source Traceability* trong `docs/EVALUATION.md` muốn phát hiện, và là lý do `KnowledgeBaseAgent` của nhóm in kèm `source` cho từng chunk trong ngữ cảnh.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus, cùng 5 câu hỏi, chỉ khác cách cắt chunk mà điểm chênh từ **6/10 đến 9/10** — chiến lược chunking ảnh hưởng tới chất lượng truy xuất mạnh hơn nhóm dự đoán ban đầu. Đáng chú ý hơn: chiến lược **thắng về điểm** (FixedSize, 9/10) không phải chiến lược **đáng tin nhất** (Sentence, 8/10 nhưng là chiến lược duy nhất không chênh giữa hai cách chấm — hễ lấy đúng tài liệu thì cũng lấy đúng đáp án). Chọn chiến lược nào tùy vào việc ưu tiên trả lời được nhiều hay ưu tiên không trả lời sai.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Thứ nhất, **cân lại độ dài tài liệu**: `quy-che-dao-tao-tin-chi` chiếm 2/3 corpus (39.962/60.044 ký tự) và lấn át 8 tài liệu còn lại ở mọi chiến lược — nên tách nó theo từng Điều thành các tài liệu nhỏ có `category` riêng, thay vì để nguyên một khối.
> Thứ hai, **thêm trường metadata `has_url`/`section`** để lọc được đúng phần thủ tục khi câu hỏi hỏi "ở đâu / link nào".
> Thứ ba, ngay từ khâu thu thập nên **giữ lại cấu trúc heading** của trang gốc thay vì làm phẳng thành văn bản thuần — nhóm đã mất thông tin heading khi làm sạch HTML, khiến hướng "chunk theo mục" phải dựng lại từ đầu.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 — 9 tài liệu công khai cùng một trường, metadata đầy đủ, nguồn tái lập được qua `data/urls.csv` |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 — so sánh 3 chiến lược có số liệu hai chiều; trừ điểm vì thành viên 3 chưa xác nhận bằng code của mình |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 — chiến lược tốt nhất đạt 9/10 ở mức chunk (Q1 thất bại ở cả 3 chiến lược) |
| Thuyết trình (Demo) | / 5 — *chờ buổi demo* |
| **Tổng phần nhóm** | **32 / 40** *(chưa tính demo)* |
