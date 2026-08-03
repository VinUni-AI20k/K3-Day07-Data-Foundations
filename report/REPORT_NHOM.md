# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** B2
**Thành viên:**

| Họ tên | MSSV | Chiến lược phụ trách |
|---|---|---|
| Nguyễn Duy Hải Bằng | 2A202601225 | `RecursiveChunker(500)` |
| Trần Thị Thanh Tâm | 2A202601267 | `FixedSizeChunker(500, 50)` |
| Huỳnh Hoàng Việt | 2A202601105 | `HeadingChunker(900)` — custom |
| Nguyễn Văn Tiến | 2A202601433 | `SentenceChunker(3)` |
| Tạ Thị Nga | 2A202601125 | `HeadingChunker(500, min=200)` — custom, biến thể tham số |

**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

> **Cấu hình chạy toàn bộ báo cáo:** embedder `text-embedding-3-small` (`EMBEDDING_PROVIDER=openai`), vector 1536 chiều đã chuẩn hóa; `llm_fn` của `KnowledgeBaseAgent` gọi `gpt-4o-mini` (nhiệt độ 0); nạp dữ liệu bằng `build_knowledge_base()` trong `ingest.py`; `top_k=3`. Mọi con số dưới đây là kết quả chạy thật trên corpus mô tả ở Phần 1.

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học.

**Phạm vi cụ thể nhóm tập trung:**
> Quy định và quy trình dành cho sinh viên trên **5 mảng dịch vụ**: đăng ký học phần, đóng học phí, học bổng khuyến khích học tập, mượn trả tài liệu thư viện, và nội quy ký túc xá — thu thập từ trang công khai của 6 trường đại học Việt Nam.

### Danh sách tài liệu (Data Inventory)

Thu thập bằng `scripts/fetch_public_pages.py` (kiểm tra `robots.txt`, chờ 1,5 giây giữa các request, chỉ nhận trang HTML/text công khai), sau đó làm sạch menu/footer/CSS. Kiểm kê đầy đủ trong `data/k3_university/sources.csv`; danh sách URL đầu vào trong `data/urls.csv`.

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định đăng ký và hủy học phần đã đăng ký (UEH) | `daotao.ueh.edu.vn/quy-dinh-dang-ky-va-huy-hoc-phan-…` | 2026-08-03 / **2517/QyĐ-ĐHKT-QLĐT ngày 22/12/2015** | 8.664 | `audience=student`, `department=academic-affairs`, `category=course-registration`, `language=vi` |
| 2 | Quy trình đóng học phí (CTU) | `dfa.ctu.edu.vn/quy-trinh-thu-tuc/quy-trinh-dong-hoc-phi.html` | 2026-08-03 / not-stated | 8.078 | `audience=student`, `department=finance`, `category=tuition`, `language=vi` |
| 3 | Quy định về thu nộp học phí đối với sinh viên (FTU) | `khoadaotaotructuyen.ftu.edu.vn/van-ban-bieu-mau/quy-dinh-ve-thu-nop-hoc-phi-…` | 2026-08-03 / not-stated | 3.295 | `audience=student`, `department=finance`, `category=tuition`, `language=vi` |
| 4 | Quy định xét cấp học bổng khuyến khích học tập (UEH) | `daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-…` | 2026-08-03 / **1321/QĐ-ĐHKT-QLĐT-CTSV ngày 12/4/2013** | 4.992 | `audience=student`, `department=student-affairs`, `category=scholarship`, `language=vi` |
| 5 | Mượn trả tài liệu thư viện (HANU) | `lib.hanu.edu.vn/contentbrowser.aspx?mnuid=133&contentid=3305` | 2026-08-03 / not-stated | 1.016 | `audience=all`, `department=library`, `category=borrowing-policy`, `language=vi` |
| 6 | Nội quy ký túc xá (IUBH) | `iubh.edu.vn/noi-quy-ky-tuc-xa` | 2026-08-03 / not-stated | 9.374 | `audience=student`, `department=dormitory`, `category=dormitory-rules`, `language=vi` |
| 7 | Quy định sinh hoạt, học tập, ứng xử nội trú ký túc xá (TDTU) | `baoloc.tdtu.edu.vn/quy-dinh-sinh-hoat-hoc-tap-ung-xu-noi-tru-ky-tuc-xa` | 2026-08-03 / not-stated | 5.822 | `audience=student`, `department=dormitory`, `category=dormitory-rules`, `language=vi` |

**Tổng: 7 tài liệu / 41.241 ký tự** — nằm trong khoảng 5–10 tài liệu Lab yêu cầu.

**Ghi chú quy trình thu thập (minh bạch để chấm được):**
- Danh sách ban đầu là 10 URL. **2 URL bị bỏ** (UIT, HCMUE) vì script không xác minh được `robots.txt` do lỗi chứng chỉ SSL ở máy chạy — nhóm không vòng qua kiểm tra này. **1 URL bị loại** (UED) vì trang trả về màn hình xác minh trình duyệt của tường lửa (WAF) thay vì nội dung; nhóm xóa file thay vì giữ lại nội dung rác.
- Hai tài liệu khởi động do repo cung cấp (`course-registration.md`, `library-services.md`) dùng URL giả `example.edu` nên **đã được chuyển sang `data/k3_university_seed/`**, không tính vào corpus benchmark. Đây là bước "thay bằng nguồn thật" mà `K3_VARIANT.md` yêu cầu.
- Làm sạch: bỏ menu điều hướng, danh sách "tin liên quan", footer, mã CSS; **không thêm bất kỳ câu nào không có trong nguồn**. Tỉ lệ giữ lại 56–97% tùy trang.
- `document_version` chỉ điền khi **chính văn bản nguồn nêu số hiệu** (2 tài liệu UEH); 5 tài liệu còn lại ghi `not-stated` đúng theo hướng dẫn, không suy đoán.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Corpus chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc `not-stated`) trong metadata; `sources.csv` khớp một-một với file.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | enum | `student`, `all` | **Bắt buộc theo K3.** Tách tài liệu dành riêng sinh viên khỏi tài liệu dùng chung; xem bằng chứng ở Phần 3 — không có nó, câu hỏi về thẻ sinh viên lấy nhầm toàn bộ tài liệu tài chính. |
| `department` | enum | `library`, `finance`, `dormitory`, `academic-affairs`, `student-affairs` | Khoanh vùng theo đơn vị phụ trách. Hữu ích nhất khi cùng một khái niệm (thẻ sinh viên, thời hạn) xuất hiện ở nhiều dịch vụ khác nhau. |
| `category` | enum | `tuition`, `scholarship`, `dormitory-rules` | Mịn hơn `department`; phân biệt hai loại quy định trong cùng một phòng ban. |
| `document_version` | string | `2517/QyĐ-ĐHKT-QLĐT ngày 22/12/2015` | Kiểm tra độ mới. Quy định 2013/2015 có thể đã lỗi thời — người đọc cần thấy điều đó. |
| `source_url` + `retrieved_at` | string | `2026-08-03` | Truy vết câu trả lời về đúng trang gốc; `KnowledgeBaseAgent` in `source_url` kèm mỗi đoạn ngữ cảnh. |
| `doc_id` + `chunk_index` | string / int | `ueh-hoc-bong-khuyen-khich`, `7` | Do `ingest.chunk_document()` gắn tự động; cần cho `delete_document()` và cho việc chỉ đích danh chunk nào nuôi câu trả lời. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

`ChunkingStrategyComparator().compare(text, chunk_size=500)` trên 3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| CTU — quy trình đóng học phí (8.078 ký tự) | `fixed_size` | 18 | 496,0 | Kém — cắt giữa danh sách các bước thanh toán |
| | `by_sentences` | 13 | 618,5 | Trung bình — giữ trọn câu nhưng chunk phình to, trộn nhiều ngân hàng vào một chunk |
| | `recursive` | 18 | 446,9 | Khá — tôn trọng ranh giới đoạn |
| FTU — quy định thu nộp học phí (3.295 ký tự) | `fixed_size` | 8 | 455,6 | Trung bình |
| | `by_sentences` | 5 | 656,0 | Kém cho dữ liệu này — các mốc "+ Học kỳ I…/+ Học kỳ II…" không kết thúc bằng dấu chấm nên bị dồn thành khối lớn |
| | `recursive` | 9 | 364,3 | Khá |
| HANU — mượn trả tài liệu (1.016 ký tự) | `fixed_size` | 3 | 372,0 | Khá |
| | `by_sentences` | 5 | 201,2 | Kém — mỗi bước quy trình bị tách rời khỏi tiêu đề "MƯỢN TÀI LIỆU" |
| | `recursive` | 3 | 337,3 | Khá |

**Nhận xét đường cơ sở:** `by_sentences` yếu nhất trên corpus này vì văn bản hành chính dùng nhiều dòng gạch đầu dòng và mục đánh số **không kết thúc bằng dấu chấm câu** — bộ tách câu không thấy ranh giới nên hoặc dồn cục, hoặc cắt vụn. Đây là lý do nhóm không chọn nó làm chiến lược chính của bất kỳ thành viên nào.

### Chiến lược của từng thành viên

> Cả 5 thành viên chạy **năm chiến lược khác nhau** trên cùng corpus 7 tài liệu và cùng 5 câu hỏi ở Phần 3.

**Thành viên 1 — Nguyễn Duy Hải Bằng (2A202601225)**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=500)` — 100 chunks
- **Mô tả & lý do chọn cho chủ đề này:** Đệ quy theo thứ tự `["\n\n", "\n", ". ", " ", ""]`, luôn thử giữ ranh giới ngữ nghĩa lớn nhất trước rồi mới cắt nhỏ dần. Lý do chọn: quy định đại học được trình bày theo đoạn, nên cắt theo `\n\n` được kỳ vọng giữ trọn mỗi khoản. Kết quả thực tế lại thấp nhất nhóm — phân tích ở dưới.

**Thành viên 2 — Trần Thị Thanh Tâm (2A202601267)**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)` — 94 chunks
- **Mô tả & lý do chọn:** Đường cơ sở có chồng lấn 50 ký tự. Chọn để kiểm chứng giả thuyết "cắt cứng nhưng có overlap vẫn đủ tốt", và để làm mốc so sánh trung thực cho các chiến lược còn lại.

**Thành viên 3 — Huỳnh Hoàng Việt (2A202601105)**
- **Loại chiến lược:** `HeadingChunker(chunk_size=900)` — custom, 86 chunks — **đáp ứng yêu cầu riêng của K3** ("ít nhất một thành viên thử chia nhỏ theo tiêu đề/mục của sổ tay hoặc quy định học vụ")
- **Mô tả & lý do chọn:** Corpus K3 gần như luôn đánh số theo `Chương … / Điều N. … / I) … / 1.1 …`. Một điều khoản là một đơn vị ngữ nghĩa trọn vẹn (điều kiện + hệ quả), nên cắt tại ranh giới tiêu đề sẽ cho chunk trả lời được trọn một câu hỏi. Ba bước: (1) cắt tại mỗi dòng tiêu đề, tiêu đề đi kèm thân bên dưới; (2) gộp mục quá ngắn để không có chunk chỉ có tiêu đề; (3) mục quá dài thì cắt tiếp theo dòng **và lặp lại tiêu đề** ở mỗi phần để không mất ngữ cảnh khi nhúng.

**Thành viên 4 — Nguyễn Văn Tiến (2A202601433)**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)` — 88 chunks
- **Mô tả & lý do chọn:** Đường cơ sở cho thấy `by_sentences` yếu trên văn bản hành chính (mục đánh số không kết thúc bằng dấu chấm). Chọn chạy chính chiến lược này để **kiểm chứng nhận định đó bằng số liệu benchmark** thay vì chỉ dựa vào thống kê chunk. Kết quả bất ngờ: vẫn đạt 6/10, ngang các chiến lược còn lại.

**Thành viên 5 — Tạ Thị Nga (2A202601125)**
- **Loại chiến lược:** `HeadingChunker(chunk_size=500, min_chunk_size=200)` — custom, biến thể tham số, 119 chunks
- **Mô tả & lý do chọn:** Cùng thuật toán với thành viên 3 nhưng ép chunk ngắn hơn, để tách bạch câu hỏi *"lợi thế đến từ việc cắt theo tiêu đề, hay chỉ đến từ việc chunk dài hơn?"*. Đây là biến thử nghiệm có kiểm soát của nhóm.

**Code snippet của chiến lược custom** (đầy đủ trong `src/custom_chunkers.py`), dùng chung cho thành viên 3 và 5:

```python
class HeadingChunker:
    HEADING = re.compile(
        r"^\s*("
        r"Điều\s+\d+|CHƯƠNG\s+[IVXLC\d]+|Chương\s+[IVXLC\d]+|"
        r"Mục\s+\d+|MỤC\s+\d+|Phần\s+\d+|"
        r"[IVX]+\)|[IVX]+\.\s|"
        r"\d+(\.\d+)*[.)]\s|"
        r"#{1,6}\s"
        r")"
    )

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections = self._merge_short(self._split_on_headings(text))
        chunks = []
        for section in sections:
            chunks.extend(self._split_long(section))   # cắt dài, giữ lại tiêu đề ở mọi phần
        return chunks
```

### So Sánh Giữa Các Thành Viên

Cùng corpus, cùng 5 câu hỏi, cùng `top_k=3`, cùng agent `gpt-4o-mini`. Chấm **đúng theo `docs/SCORING.md`**: 2đ khi chunk chứa câu trả lời chuẩn ở **hạng 1 và agent trả lời đúng**; 1đ khi chunk liên quan có trong top-3 nhưng không ở hạng 1, hoặc ở hạng 1 mà agent trả lời thiếu/sai; 0đ khi vắng mặt trong top-3.

| Thành viên | Chiến lược (Strategy) | Số chunk | Điểm (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|---|------|-----------|----------|
| Bằng | `RecursiveChunker(500)` | 100 | **4** | Chunk gọn (~450 ký tự), rẻ khi nhúng | Cắt vụn danh sách điều kiện: Q5 chunk đáp án tụt **hạng 7/100** |
| Tâm | `FixedSizeChunker(500, 50)` | 94 | **6** | Overlap 50 ký tự cứu câu bị cắt ngang; ổn định trên câu hỏi có mốc số | Chunk không mang tiêu đề; Q5 lấy đúng chunk nhưng agent tóm sai điều kiện |
| Việt | `HeadingChunker(900)` | 86 | **6** | Chunk mang tiêu đề điều khoản; **ít chunk nhất** mà vẫn top điểm; thắng rõ Q5 | Chunk dài (~860 ký tự) làm loãng mốc số: Q2 tụt hạng 3 |
| Tiến | `SentenceChunker(3)` | 88 | **6** | Câu duy nhất cả nhóm ghi điểm ở Q1; agent biết từ chối khi thiếu căn cứ | Chunk ngắn, thiếu ngữ cảnh tiêu đề; Q2 và Q5 chỉ đạt 1đ |
| Nga | `HeadingChunker(500, min=200)` | 119 | **6** | Giữ lợi thế tiêu đề mà vẫn bắt được mốc số (Q2 hạng 1) | Nhiều chunk nhất (119) → chi phí nhúng cao nhất; Q3 tụt hạng 2 |

Chi tiết từng câu (điểm/câu):

| Câu | Bằng<br>Recursive | Tâm<br>FixedSize | Việt<br>Heading900 | Tiến<br>Sentence | Nga<br>Heading500 |
|---|:-:|:-:|:-:|:-:|:-:|
| Q1 — đăng ký học phần + xử lý chưa đóng học phí | 0 | 0 | 0 | **1** | 0 |
| Q2 — hạn nộp học phí HK I / HK II | **2** | **2** | 1 | 1 | **2** |
| Q3 — bước đầu tiên khi mượn tài liệu | 1 | **2** | **2** | **2** | 1 |
| Q4 — giờ đóng cửa / tắt đèn ký túc xá | 1 | 1 | 1 | 1 | 1 |
| Q5 — điều kiện xét học bổng | 0 | 1 | **2** | 1 | **2** |
| **Tổng** | **4/10** | **6/10** | **6/10** | **6/10** | **6/10** |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Bốn chiến lược cùng đạt 6/10 nhưng **thắng ở những câu khác nhau**, và nhóm cho rằng `HeadingChunker` là lựa chọn đúng nhất cho chủ đề K3. Điểm bằng nhau che giấu khác biệt về chất: FixedSize và Heading500 thắng ở câu hỏi có **mốc số cụ thể** (Q2 — ngày 30/11, 31/05) vì chunk ngắn làm con số chiếm tỉ trọng lớn trong vector; còn Heading900 thắng ở câu hỏi **tra cứu điều khoản** (Q5) vì chunk mang theo dòng tiêu đề nên vector biết đây là điều khoản về điều kiện xét học bổng chứ không phải một đoạn văn bất kỳ. Với corpus quy định, dạng câu hỏi thứ hai phổ biến hơn.
>
> Bằng chứng mạnh nhất là **Q5**: điều kiện xét học bổng nằm trong danh sách gạch đầu dòng dưới tiêu đề "2.2 Điều kiện để sinh viên tham gia xét học bổng". `Recursive` cắt tại `\n\n` nên **tách rời tiêu đề khỏi danh sách**, đẩy chunk đáp án xuống hạng **7/100** (0đ); cả hai biến thể `Heading` giữ nguyên khối nên chunk đó ở **hạng 1** (2đ). Cùng dữ liệu, cùng embedder, cùng câu hỏi — khác biệt hoàn toàn do ranh giới chunk.
>
> **Thí nghiệm có kiểm soát của thành viên 5 trả lời được câu hỏi "do tiêu đề hay do chunk dài?"**: `Heading500` chunk ngắn hơn hẳn `Heading900` (119 chunk so với 86) nhưng **vẫn đạt 6/10 và vẫn thắng Q5**. Vậy lợi thế đến từ **việc giữ tiêu đề dính với nội dung**, không phải từ độ dài chunk. Đây là kết luận mà nếu chỉ có ba chiến lược như dự kiến ban đầu thì nhóm không tách bạch được.
>
> **Kết quả bất ngờ ở thành viên 4:** `SentenceChunker` bị đường cơ sở dự đoán là yếu nhất (dồn cục hoặc cắt vụn trên văn bản đánh số), nhưng vẫn đạt 6/10 và là chiến lược **duy nhất ghi được điểm ở Q1**. Bài học: thống kê chunk (count, avg_length) **không dự đoán được** chất lượng truy xuất; phải chạy benchmark thật.
>
> Về chi phí: `Heading900` đạt điểm cao nhất **với ít chunk nhất** (86 so với 119 của Heading500 và 100 của Recursive), tức tốt hơn cả về chất lượng lẫn chi phí nhúng — miễn là tài liệu có cấu trúc tiêu đề để khai thác. Trên corpus không đánh số (email, FAQ tự do), lợi thế này sẽ biến mất.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

Cả 5 câu trả lời chuẩn đều **trích được nguyên văn** từ corpus (đã kiểm chứng bằng `grep` trên `data/k3_university/`), không suy đoán quy định của trường.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên đăng ký học phần bằng hình thức nào, và học phần chưa đóng học phí bị xử lý ra sao? | Hình thức: **đăng ký trực tuyến (online) trên website của Trường**. Sinh viên phải đóng học phí trong thời gian quy định; sau thời gian đó **Trường sẽ hủy học phần chưa đóng học phí trong hệ thống**. | `ueh-dang-ky-huy-hoc-phan` — Điều 2 (giải thích từ ngữ) + Điều 4 (quy định đăng ký) |
| 2 | Hạn cuối nộp học phí học kỳ I và học kỳ II là ngày nào? | Học kỳ I: **chậm nhất ngày 30 tháng 11** hàng năm. Học kỳ II: **chậm nhất ngày 31 tháng 05** hàng năm. | `ftu-quy-dinh-thu-nop-hoc-phi` — mục 1.2 thời hạn nộp |
| 3 | Bước đầu tiên khi mượn tài liệu tại máy mượn tự động của thư viện là gì? | **Đưa thẻ thư viện (phần chứa mã vạch) vào vị trí đầu đọc mã vạch**; khi hệ thống nhận diện đúng sẽ hiển thị thông tin bạn đọc. | `hanu-muon-tra-tai-lieu` — mục 2, "MƯỢN TÀI LIỆU — Bước 1" |
| 4 | Ký túc xá đóng cửa lúc mấy giờ và khi nào phải tắt đèn? | TDTU: mở cửa **05:00**, đóng cửa **22:00**, **22:30 tắt đèn** toàn bộ phòng ở. IUBH: mở cửa **6h00**, đóng cửa **23h00**. (Hai trường khác nhau — câu trả lời phải nêu rõ theo tài liệu nào.) | `tdtu-noi-tru-ky-tuc-xa` — Điều 1; `iubh-noi-quy-ky-tuc-xa` — Điều 2 |
| 5 | Điều kiện để sinh viên được xét cấp học bổng khuyến khích học tập là gì? *(chạy kèm `metadata_filter={"audience": "student"}`)* | Đang trong **8 học kỳ chính** của khóa học; kết quả học tập và rèn luyện **từ loại khá trở lên**, không bị kỷ luật từ khiển trách trở lên; **đạt từ 5 điểm trở lên** ở tất cả học phần tính vào điểm trung bình tích lũy xét học bổng. | `ueh-hoc-bong-khuyen-khich` — mục 2.2 |

**Yêu cầu đã đáp ứng:** 5 câu đa dạng về dạng hỏi (quy trình / mốc thời gian / thao tác / tra cứu điều khoản / điều kiện), trải trên 5 tài liệu khác nhau, và Q5 chạy kèm bộ lọc metadata đúng yêu cầu K3.

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Đăng ký học phần + xử lý chưa đóng học phí | Tiến — `SentenceChunker` (hạng 2) | ✗ với 4/5 chiến lược | Lỗi ở **câu hỏi**, không phải ở chunking — xem phân tích bên dưới |
| 2 | Hạn nộp học phí HK I / HK II | Bằng, Tâm, Nga (hạng 1 + agent đúng) | ✓ cả năm | Việt tụt hạng 3: chunk 789 ký tự làm loãng hai con số ngày tháng |
| 3 | Bước đầu tiên khi mượn tài liệu | Tâm, Việt, Tiến (hạng 1 + agent đúng) | ✓ cả năm | Bằng và Nga hạng 2 — "Bước 1" bị cắt rời khỏi tiêu đề "MƯỢN TÀI LIỆU" |
| 4 | Giờ đóng cửa / tắt đèn ký túc xá | *(không ai đạt 2đ)* | ✓ cả năm | **Retrieval đúng nhưng agent sai ở cả 5** — trộn quy định hai trường, xem phân tích |
| 5 | Điều kiện xét học bổng | Việt, Nga — hai biến thể `Heading` (hạng 1 + agent đúng) | ✓ 4/5 — ✗ Bằng | Bằng đẩy chunk đáp án xuống **hạng 7/100** vì tách tiêu đề khỏi danh sách điều kiện |

**Phân tích lỗi (Failure Analysis) — Q1, câu duy nhất cả ba chiến lược cùng trượt**

Vị trí thật của chunk chứa đáp án khi xếp hạng toàn bộ corpus:

| Chiến lược | Q1 (câu gốc, hỏi 2 ý) | Q1 (tách thành 1 ý) |
|---|---|---|
| M1 Recursive | hạng **8**/100 | hạng **4**/100 |
| M2 FixedSize | hạng **6**/94 | hạng 7/94 |
| M3 Heading | hạng **4**/86 | hạng **3**/86 |

**Nguyên nhân:** Q1 hỏi **hai ý trong một câu** — "đăng ký bằng hình thức nào" *và* "chưa đóng học phí bị xử lý ra sao". Vector của câu hỏi trở thành trung bình của hai chủ đề, nên nó khớp mạnh nhất với các chunk nói *chung chung* về đăng ký học phần (top-1 của M1 đạt 0,7253) thay vì chunk nói riêng về việc hủy học phần do chưa đóng tiền. Không phải lỗi chunking: chunk đáp án tồn tại, được xếp hạng 4–8, chỉ nằm ngoài `top_k=3`.

**Phân tích lỗi (Failure Analysis) — Q4, câu mà retrieval đúng nhưng agent vẫn sai ở cả 5 chiến lược**

Đây là phát hiện quan trọng nhất sau khi nhóm nối LLM thật (`gpt-4o-mini`) vào `llm_fn` thay cho hàm demo. Cả 5 chiến lược đều đưa được chunk chứa giờ giấc ký túc xá vào top-3 — nhưng **không ai đạt 2 điểm**, vì câu trả lời của agent đều sai.

Câu trả lời thực tế của agent (chiến lược của Bằng): *"Ký túc xá đóng cửa lúc 23:00 (context [2]) và phải tắt đèn lúc 22:30 (context [1])."*

Hai con số này đến từ **hai trường khác nhau**: 23h00 là giờ đóng cửa của IUBH, còn 22:30 là giờ tắt đèn của TDTU (trường này đóng cửa lúc 22:00). Agent ghép hai quy định độc lập thành một câu trả lời nghe rất hợp lý nhưng **không đúng với bất kỳ trường nào**. Chiến lược của Tiến trả lời "đóng cửa 22:00 và tắt đèn 22:30" — đúng theo TDTU, nhưng cũng chỉ vì top-1 tình cờ là tài liệu TDTU chứ không phải vì agent phân biệt được nguồn.

**Nguyên nhân gốc:** corpus gom quy định của nhiều trường mà **không có trường metadata phân biệt cơ sở đào tạo**. `KnowledgeBaseAgent` in `source_url` kèm mỗi đoạn ngữ cảnh, nhưng prompt không yêu cầu model kiểm tra xem các đoạn có cùng nguồn hay không.

**Bài học:** chunk đúng nằm trong top-3 **chưa đủ để có câu trả lời đúng**. Đây chính là lý do rubric tách riêng "top-3 có chunk liên quan" và "agent trả lời chính xác" — nhóm chỉ nhìn thấy điều này sau khi thay hàm demo bằng LLM thật.

**Một dạng lỗi thứ hai, tinh vi hơn — Q1:** agent trả lời rằng sinh viên đăng ký bằng cách nộp *"Phiếu đăng ký học phần"*. Nhóm đã kiểm tra: câu này **có thật trong corpus** (`ueh-dang-ky-huy-hoc-phan`, Điều 6), nên agent **không bịa**. Nhưng Điều 6 nói về trường hợp đăng ký đặc biệt, còn hình thức chung là *đăng ký trực tuyến* ở Điều 2. Agent trung thực với ngữ cảnh được đưa vào, ngữ cảnh lại sai điều khoản → câu trả lời sai mà vẫn có căn cứ trích dẫn. Nói cách khác: **grounding tốt không đồng nghĩa với đúng**. Riêng chiến lược của Tiến, agent trả lời *"Context does not contain the answer"* — từ chối đúng lúc, đây là hành vi mong muốn.

**Đề xuất cải thiện, theo thứ tự ưu tiên:**
1. **Tách câu hỏi đa ý** thành hai truy vấn đơn ý rồi hợp kết quả. Bằng chứng: khi tách, M3 lên hạng 3 (lọt top-3) và M1 lên hạng 4 — cải thiện thật nhưng chưa đủ cho mọi chiến lược, cho thấy đây là điều kiện cần chứ chưa đủ.
2. **Tăng `top_k` từ 3 lên 5** — với hạng 4–6, riêng thay đổi này đã cứu được Q1 ở cả M2 và M3 mà không phải sửa dữ liệu.
3. **Chunk theo tiêu đề** thu hẹp khoảng cách (hạng 8 → hạng 4), củng cố kết luận ở Phần 2.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Ở Q5 thì không, nhưng ở dạng câu hỏi khác thì có tính quyết định** — và nhóm thấy sự phân biệt này mới là điều đáng báo cáo.
>
> Với Q5 (`audience=student`), top-3 **không đổi** so với khi không lọc, vì trong corpus chỉ có một tài liệu về học bổng và nó đã áp đảo về điểm tương tự. Bộ lọc ở đây đóng vai trò *bảo hiểm*, không phải *cải thiện thứ hạng*.
>
> Nhóm thử thêm một câu hỏi khác để đo đúng tác dụng của bộ lọc — *"Phải xuất trình thẻ sinh viên khi nào?"*, một khái niệm xuất hiện ở **cả bốn** dịch vụ (thư viện, ký túc xá, học phí, học vụ):
>
> | | Top-3 trả về |
> |---|---|
> | `search()` không lọc | `ctu-quy-trinh-dong-hoc-phi::c2` (0,5575), `::c11` (0,4820), `::c6` (0,4771) — **cả 3 đều là tài liệu học phí, sai dịch vụ** |
> | `search_with_filter(metadata_filter={"audience": "all"})` | `hanu-muon-tra-tai-lieu::c0` (0,4682), `::c1` (0,3370) — **đúng tài liệu thư viện** |
>
> Không có bộ lọc, câu hỏi này trả về 0/3 kết quả đúng dịch vụ. Có bộ lọc, kết quả đúng ngay hạng 1 — dù **điểm tương tự thấp hơn** (0,4682 < 0,5575). Đây là minh chứng trực tiếp cho điều đã nêu ở báo cáo cá nhân: điểm cosine tuyệt đối không đo được mức độ liên quan; metadata mới là thứ áp đặt được ràng buộc "đúng đối tượng".
>
> **Đánh đổi độ thu hồi (recall trade-off):** cũng trong ví dụ trên, bộ lọc chỉ trả về **2** kết quả thay vì 3, vì toàn corpus chỉ có 2 chunk mang `audience=all`. Lọc càng chặt thì càng dễ rơi vào tình trạng không đủ ngữ cảnh cho agent. Với corpus 7 tài liệu, `department` là mức lọc cân bằng hơn `audience`.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Ranh giới chunk quyết định thứ hạng, không phải kích thước chunk.** Cùng câu hỏi Q5, chunk chứa đáp án đứng **hạng 1/86** với `HeadingChunker` nhưng **hạng 7/100** với `RecursiveChunker` — chỉ vì một bên giữ tiêu đề "2.2 Điều kiện…" dính với danh sách điều kiện, bên kia cắt rời nó ra.
2. **Điểm tương tự cao không có nghĩa là đúng.** Câu hỏi về thẻ sinh viên cho top-3 toàn tài liệu học phí với điểm 0,55; kết quả đúng chỉ đạt 0,47 và chỉ xuất hiện khi lọc `audience`. Ngưỡng tuyệt đối là bẫy; metadata là dây an toàn.
3. **Chiến lược tốt nhất lại rẻ nhất.** `HeadingChunker(900)` đạt điểm cao nhất với **ít chunk nhất** (86, so với 88 / 94 / 100 / 119) — chất lượng và chi phí không nhất thiết đánh đổi nhau khi chiến lược khớp với cấu trúc tài liệu.
4. **Một câu hỏi hỏi hai ý là một câu hỏi hỏng.** Q1 trượt 4/5 chiến lược không phải vì dữ liệu thiếu mà vì vector câu hỏi bị pha loãng giữa hai chủ đề.
5. **Retrieval đúng vẫn có thể cho câu trả lời sai.** Ở Q4, cả 5 chiến lược đều lấy đúng chunk nhưng **không ai đạt 2đ**, vì agent ghép giờ đóng cửa của trường này với giờ tắt đèn của trường kia. Đây là phần nhóm muốn trình bày kỹ nhất — nó chỉ lộ ra sau khi thay `llm_fn` demo bằng LLM thật.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng 7 tài liệu, cùng 5 câu hỏi, cùng embedder, cùng agent — điểm vẫn chênh từ 4/10 tới 6/10 **chỉ do cách cắt chunk**. Quan trọng hơn con số tổng: bốn chiến lược cùng đạt 6/10 lại thắng ở những câu hoàn toàn khác nhau (FixedSize và Heading500 thắng câu có mốc số, Heading900 thắng câu tra cứu điều khoản, Sentence là chiến lược duy nhất ghi điểm ở Q1). Nếu nhóm chỉ nhìn tổng điểm thì đã kết luận "bốn cái như nhau" và bỏ lỡ điều đáng học nhất: **dạng câu hỏi quyết định chiến lược nào phù hợp**.
>
> Hai kết quả trái với dự đoán ban đầu của nhóm, và đều đáng giá hơn phần đoán đúng: (1) `SentenceChunker` bị thống kê baseline đánh giá là yếu nhất nhưng vẫn đạt 6/10 — **số liệu chunk không dự đoán được chất lượng truy xuất**; (2) trần điểm của cả nhóm không nằm ở chunking mà ở **khâu sinh câu trả lời** — Q4 chặn tất cả mọi người ở 1đ dù retrieval hoàn hảo.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
1. **Chuẩn hóa phạm vi theo một trường duy nhất.** Corpus hiện gom quy định của 6 trường khác nhau, dẫn tới Q4 có **hai đáp án mâu thuẫn** (TDTU đóng cửa 22:00, IUBH 23:00). Với hệ thống hỏi đáp thật, mâu thuẫn này là lỗi nghiêm trọng; nếu buộc phải gom nhiều trường thì `institution` phải là trường metadata bắt buộc và mọi câu trả lời phải nêu rõ áp dụng cho trường nào.
2. **Cân bằng số chunk giữa các dịch vụ.** Thư viện chỉ có 1.016 ký tự trong khi ký túc xá có 15.196 — chênh 15 lần, khiến câu hỏi về thư viện luôn bị lấn át khi không lọc.
3. **Ưu tiên nguồn nêu rõ số hiệu và ngày hiệu lực.** Chỉ 2/7 tài liệu có `document_version` thật, mà cả hai đều là văn bản 2013 và 2015 — có thể đã hết hiệu lực. Với dữ liệu quy định, "mới" quan trọng ngang "đúng".
4. **Tự động lọc chunk rác ngay trong pipeline nạp dữ liệu**, thay vì làm sạch thủ công như lần này (xem lại `docs/DATA_COLLECTION.md` mục 2.5).

---

## Việc còn phải làm trước khi nộp

- [x] Gán chiến lược cho đủ 5 thành viên và chạy benchmark riêng cho từng người.
- [x] Nối LLM thật (`gpt-4o-mini`) vào `llm_fn` để chấm được vế "agent trả lời đúng" của rubric.
- [x] Báo cáo cá nhân của Nguyễn Duy Hải Bằng đã chạy lại trên corpus 7 tài liệu với đúng 5 câu hỏi ở Phần 3.
- [ ] **Bốn thành viên còn lại** cập nhật `REPORT_CANHAN.md` của mình theo số liệu chiến lược tương ứng ở Phần 2 (mỗi người nộp một bản riêng).
- [ ] Đối chiếu lại nội dung 7 file `.md` với `source_url` gốc một lượt cuối (nội dung do script trích tự động rồi lọc bằng luật, nên cần một lượt đọc của người).
- [ ] Cân nhắc thêm trường metadata `institution` để xử lý lỗi trộn nguồn ở Q4 trước khi demo.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 — 7 tài liệu công khai, metadata đầy đủ, nguồn minh bạch; trừ 1 vì chỉ 2/7 tài liệu nêu được `document_version` thật, và corpus thiếu trường `institution` (gây lỗi Q4) |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 — 5 chiến lược khác nhau cho 5 thành viên, gồm 1 custom theo tiêu đề và 1 biến thể tham số làm thí nghiệm có kiểm soát; có baseline và giải thích nguyên nhân bằng thứ hạng cụ thể |
| Chất lượng truy xuất (Retrieval Quality) | 6 / 10 — chiến lược tốt nhất đạt 6/10; chấm đủ cả vế agent trả lời đúng |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **35 / 40** |
