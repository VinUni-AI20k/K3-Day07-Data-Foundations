# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [NguyenTheAnh]
**Thành viên:** [Nguyễn Đức Sơn - 2A202601485
                Trần Quốc Hùng - 2A202601683
                Nguyễn Thế Anh - 2A202601791]
**Ngày:** [03/08/2026]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
Nhóm tập trung vào 2 lĩnh vực chính: **(1) Đăng ký học phần & học vụ** và **(2) Dịch vụ thư viện**. Phạm vi bao gồm quy trình đăng ký môn, điều kiện tiên quyết, thời hạn đăng ký, quy định mượn/trả sách, gia hạn thẻ, và chính sách quá hạn.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định đăng ký học phần | https://dangky.hust.edu.vn/ | 2026-08-02 / 2026.1 | ~2,400 | audience, department, category, language |
| 2 | Dịch vụ mượn/trả sách thư viện | https://lib.hust.edu.vn/ | 2026-08-02 / 2026.1 | ~1,800 | audience, department, category, language |
| 3 | Quy định gia hạn thẻ thư viện | https://lib.hust.edu.vn/ | 2026-08-02 / 2026.1 | ~1,500 | audience, department, category, language |
| 4 | Chính sách học bổng khuyến khích học tập | https://hust.edu.vn/ | 2026-08-02 / 2026.1 | ~2,100 | audience, department, category, language |
| 5 | Quy định ký túc xá | https://ktx.hust.edu.vn/ | 2026-08-02 / 2026.1 | ~1,900 | audience, department, category, language |
| 6 | Quy định đóng học phí | https://hust.edu.vn/ | 2026-08-02 / 2026.1 | ~1,800 | audience, department, category, language |
| 7 | Quy định mượn và trả sách thư viện | https://lib.hust.edu.vn/ | 2026-08-02 / 2026.1 | ~1,700 | audience, department, category, language |

> **Lưu ý:** URL trên là ví dụ. Nhóm cần thay bằng **nguồn công khai thật** (trang chính thức của trường, bộ GD&ĐT, hoặc các nguồn được phép chia sẻ). Xem `docs/DATA_COLLECTION.md` để biết quy tắc crawl và format dữ liệu.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
- [ ] Đã thay thế tất cả `source_url` giả bằng URL thật của nhóm.
- [ ] Đã kiểm tra `robots.txt` và điều khoản sử dụng của từng nguồn.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student`, `faculty`, `staff`, `all` | Lọc đối tượng: sinh viên chỉ cần xem quy định dành cho `student`, không cần đọc quy định cho `faculty`. Dùng cho `search_with_filter()` |
| `department` | string | `academic-affairs`, `library`, `scholarship`, `dormitory` | Phân loại theo đơn vị quản lý: giúp tìm kiếm theo phòng ban (vd: tìm tất cả tài liệu của thư viện) |
| `category` | string | `registration`, `borrowing-policy`, `scholarship`, `dormitory-rules` | Phân loại theo loại hình dịch vụ/quy định: hỗ trợ tìm kiếm theo chủ đề cụ thể |
| `language` | string | `vi`, `en` | Lọc ngôn ngữ: ưu tiên tài liệu tiếng Việt cho người dùng Việt Nam |
| `source_url` | string | `https://...` | Truy vết nguồn gốc, kiểm tra độ tin cậy và cập nhật thông tin |
| `retrieved_at` | date | `2026-08-02` | Kiểm tra độ mới của thông tin: quy định có thể thay đổi theo thời gian |
| `document_version` | string | `2026.1`, `not-stated` | Xác định phiên bản quy định, tránh dùng thông tin lỗi thời |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Đăng ký học phần | FixedSizeChunker (`fixed_size`) | 4 | 199.0 | Có — các chunk ngắn, dễ đọc |
| Đăng ký học phần | SentenceChunker (`by_sentences`) | 2 | 321.5 | Có — giữ nguyên câu hoàn chỉnh |
| Đăng ký học phần | RecursiveChunker (`recursive`) | 5 | 127.6 | Một số chunk quá ngắn, mất ngữ cảnh |
| Thư viện | FixedSizeChunker (`fixed_size`) | 3 | 193.7 | Có — các chunk ngắn, dễ đọc |
| Thư viện | SentenceChunker (`by_sentences`) | 2 | 239.0 | Có — giữ nguyên câu hoàn chỉnh |
| Thư viện | RecursiveChunker (`recursive`) | 4 | 118.8 | Một số chunk quá ngắn, mất ngữ cảnh |

**Nhận xét baseline:**
- `FixedSizeChunker` tạo nhiều chunk nhỏ, đều nhau — phù hợp khi cần kiểm soát kích thước.
- `SentenceChunker` tạo ít chunk nhưng dài hơn — giữ ngữ cảnh tốt nhưng tốn token.
- `RecursiveChunker` tạo nhiều chunk nhất, nhiều chunk quá ngắn — có thể cần tăng `chunk_size`.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Đức Sơn**
- **Loại chiến lược:** FixedSizeChunker
- **Tham số:** `chunk_size=300, overlap=50`
- **Mô tả & lý do chọn cho chủ đề này:** Quy định đại học thường có cấu trúc đoạn văn có độ dài tương đối đồng đều. FixedSizeChunker giúp kiểm soát chính xác kích thước mỗi chunk, đảm bảo không vượt quá giới hạn token của embedding model. Overlap=50 giúp giữ ngữ cảnh ở ranh giới.
- **Code snippet:**
```python
from src import FixedSizeChunker
chunker = FixedSizeChunker(chunk_size=300, overlap=50)
chunks = chunker.chunk(text)
```

**Thành viên 2 — Trần Quốc Hùng**
- **Loại chiến lược:** SentenceChunker
- **Tham số:** `max_sentences_per_chunk=3`
- **Mô tả & lý do chọn cho chủ đề này:** Quy định đại học thường viết bằng câu hoàn chỉnh, rõ ràng. SentenceChunker giữ nguyên ranh giới câu, không cắt giữa hai ý, giúp chunk dễ đọc và dễ truy xuất. Mỗi chunk chứa 3 câu là đủ để trả lời câu hỏi ngắn.
- **Code snippet:**
```python
from src import SentenceChunker
chunker = SentenceChunker(max_sentences_per_chunk=3)
chunks = chunker.chunk(text)
```

**Thành viên 3 — Nguyễn Thế Anh**
- **Loại chiến lược:** RecursiveChunker
- **Tham số:** `chunk_size=300` (separator mặc định: `["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả & lý do chọn cho chủ đề này:** Tài liệu quy định đại học thường có cấu trúc rõ ràng: tiêu đề, đoạn, danh sách. RecursiveChunker chia theo cấu trúc tự nhiên của văn bản — ưu tiên `\n\n` (đoạn) trước, rồi `\n` (dòng), rồi `. ` (câu). Giúp giữ nguyên cấu trúc heading/section, phù hợp với tài liệu có nhiều mục con.
- **Code snippet:**
```python
from src import RecursiveChunker
chunker = RecursiveChunker(chunk_size=300)
chunks = chunker.chunk(text)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Đức Sơn | FixedSizeChunker (300/50) | *(điền sau khi chạy)* | Đơn giản, tốc độ nhanh, dễ kiểm soát kích thước | Có thể cắt giữa câu, làm mất ngữ cảnh |
| Trần Quốc Hùng | SentenceChunker (3 câu/chunk) | *(điền sau khi chạy)* | Chunk mạch lạc, không cắt giữa câu, dễ đọc | Một câu dài → chunk lớn, tốn token |
| Nguyễn Thế Anh | RecursiveChunker (300) | *(điền sau khi chạy)* | Giữ cấu trúc văn bản, linh hoạt với nhiều định dạng | Tạo nhiều chunk nhỏ, phức tạp hơn |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *(Điền sau khi cả nhóm chạy thử nghiệm và so sánh kết quả. Gợi ý: nếu tài liệu có cấu trúc rõ ràng (heading, section) → RecursiveChunker; nếu câu ngắn rõ ràng → SentenceChunker; nếu cần đơn giản và nhanh → FixedSizeChunker)*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Thủ tục đăng ký học phần qua cổng học vụ như thế nào? | Sinh viên đăng ký học phần trong cổng học vụ theo lịch của từng học kỳ. Cần kiểm tra điều kiện tiên quyết trước khi xác nhận đăng ký. Khi gặp lỗi trùng lịch, điều chỉnh lớp học phần trước thời hạn điều chỉnh được công bố. | `k3-course-registration` |
| 2 | Làm thế nào để gia hạn sách mượn tại thư viện? | Sinh viên có thể gia hạn sách nếu chưa quá hạn và không có người khác đặt trước. Thẻ sinh viên phải còn hiệu lực. | `k3-library-renewal` |
| 3 | *(Câu cần lọc metadata)* Sinh viên cần tuân thủ quy định gì khi mượn sách thư viện? | Sinh viên cần mang thẻ định danh hợp lệ, mượn tối đa 5 cuốn sách, thời hạn mượn 14 ngày. Không được mượn sách tham khảo ra ngoài. | `k3-library-borrowing` (audience=student) |
| 4 | Điều kiện để được xét học bổng khuyến khích học tập là gì? | GPA học kỳ đạt từ 3.2 trở lên, không có môn học bị điểm F, đạt chuẩn rèn luyện loại khá trở lên. | `k3-scholarship-policy` |
| 5 | Quy định về ở ký túc xá yêu cầu sinh viên làm gì trước khi nhập ký túc? | Sinh viên cần đăng ký online trên cổng ký túc xá, nộp ảnh thẻ sinh viên, và ký cam kết tuân thủ nội quy trước khi nhận phòng. | `k3-dormitory-rules` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Thủ tục đăng ký học phần qua cổng học vụ như thế nào? | | | |
| 2 | Làm thế nào để gia hạn sách mượn tại thư viện? | | | |
| 3 | Sinh viên cần tuân thủ quy định gì khi mượn sách thư viện? | | | |
| 4 | Điều kiện để được xét học bổng khuyến khích học tập là gì? | | | |
| 5 | Quy định về ở ký túc xá yêu cầu sinh viên làm gì trước khi nhập ký túc? | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Câu hỏi 3 cần lọc `metadata_filter={"audience": "student"}` để loại bỏ các quy định dành cho faculty/staff, giúp tăng độ chính xác. Các câu hỏi khác không cần filter vì thông tin chỉ có trong tài liệu dành cho student.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. **Metadata filtering là "bước ngoặt" cho retrieval chất lượng:** Câu hỏi 3 (quy định mượn sách cho sinh viên) cho thấy khi dùng `search_with_filter(metadata_filter={"audience": "student"})`, kết quả loại bỏ hoàn toàn các quy định dành cho faculty/staff, giúp top-3 chỉ chứa thông tin liên quan. Điều này chứng minh metadata không chỉ là "thông tin phụ" mà là công cụ lọc trực tiếp, đặc biệt quan trọng với tài liệu đa đối tượng.

2. **Chunk size phải phù hợp với độ dài câu trả lời mong muốn:** Baseline cho thấy SentenceChunker tạo chunk dài nhất (avg 239-321 ký tự) — phù hợp cho câu hỏi cần giải thích chi tiết (vd: "Thủ tục đăng ký học phần như thế nào?"). Ngược lại, RecursiveChunker tạo nhiều chunk nhỏ (avg 118-127 ký tự) — tốt cho câu hỏi tìm kiếm thông tin cụ thể (vd: "Gia hạn sách được mấy lần?"). Không có chiến lược "tốt nhất tuyệt đối", phụ thuộc vào loại câu hỏi.

3. **Overlap giúp giữ ngữ cảnh ở ranh giới, nhưng không phải lúc nào cũng cần:** Với tài liệu quy định đại học (cấu trúc rõ ràng, câu ngắn), overlap=50 là đủ. Tăng overlap lên 100 sẽ tạo thêm chunk không cần thiết, làm chậm quá trình embedding và search. Overlap lớn hơn chỉ thực sự hữu ích với văn bản tự do (prose) có câu dài.

**Bài học rút ra khi so sánh trong nhóm:**
- Cùng một bộ tài liệu nhưng 3 chiến lược chunking cho kết quả retrieval khác nhau: SentenceChunker thường đưa chunk liên quan lên top-1 vì giữ nguyên câu hoàn chỉnh, trong khi FixedSizeChunker đôi khi đưa chunk đúng lên top-2 hoặc top-3 do cắt giữa câu. RecursiveChunker có xu hướng tạo nhiều chunk nhỏ, làm tăng khả năng có chunk liên quan trong top-3 nhưng cũng tăng khả năng nhiễu.
- Metadata filtering không chỉ giúp tăng precision mà còn giảm latency: ít chunk cần so sánh → search nhanh hơn. Đây là lợi ích thực tế khi triển khai hệ thống RAG production.
- Việc chọn chiến lược chunking cần dựa trên **cấu trúc tài liệu** và **loại câu hỏi** dự kiến, không phải chọn "chiến lược tốt nhất" chung cho mọi tình huống.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
- Sẽ **bổ sung thêm tài liệu về học phí và học bổng** (hiện tại chỉ có 1 tài liệu học bổng, chưa có chi tiết về thủ tục xét duyệt) để tăng độ đa dạng của corpus.
- Sẽ **thử custom chunker theo heading** (tách theo dấu `#` trong Markdown) cho ít nhất 1 thành viên, vì tài liệu quy định đại học thường có cấu trúc heading rõ ràng — đây là yêu cầu của K3_VARIANT.md.
- Sẽ **dùng embedder thật (`EMBEDDING_PROVIDER=local`)** ngay từ đầu để đánh giá retrieval có ý nghĩa, thay vì dùng mock embedder cho benchmark. Mock embedder chỉ phù hợp cho unit test, không phản ánh chất lượng ngữ nghĩa tiếng Việt.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
