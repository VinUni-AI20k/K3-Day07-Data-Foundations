# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** B301
**Thành viên:** Đỗ Thanh Tùng · Nguyễn Thành Long · Hoàng Hải Dương · Trần Hải Quân · Nguyễn Minh Phương
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

**Phân công:** 4 thành viên mỗi người thử một chiến lược chunking khác nhau trên cùng corpus và cùng bộ câu hỏi; 1 thành viên phụ trách thu thập, làm sạch và chuẩn hóa dữ liệu.

| Thành viên | Vai trò | Sản phẩm |
|---|---|---|
| Đỗ Thanh Tùng | Chiến lược `HeadingChunker` (tùy chỉnh) | `src/chunking.py`, `scripts/benchmark.py`, `scripts/demo_server.py` |
| Trần Hải Quân | Chiến lược `FixedSizeChunker` (baseline, tinh chỉnh tham số) | Cấu hình + kết quả benchmark |
| Hoàng Hải Dương | Chiến lược `SentenceChunker` | Cấu hình + kết quả benchmark |
| Nguyễn Thành Long | Chiến lược `RecursiveChunker` | Cấu hình + kết quả benchmark |
| Nguyễn Minh Phương | Thu thập & chuẩn hóa dữ liệu | `data/hust/*.md`, `data/hust/sources.csv` |

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy định học vụ và kế hoạch đăng ký học phần của Đại học Bách khoa Hà Nội (HUST) — gồm quy chế đào tạo, chuẩn ngoại ngữ đầu ra, và các thông báo đăng ký lớp/đăng ký học tích hợp kỹ sư chuyên sâu.

Toàn bộ tài liệu lấy từ Cổng thông tin đào tạo công khai `ctt.hust.edu.vn`. Các văn bản PDF được chuyển sang Markdown và làm sạch (bỏ header/footer lặp, giữ nguyên cấu trúc Chương/Điều/khoản) trước khi đưa vào `data/hust/`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy chế đào tạo HUST năm 2025 | `ctt.hust.edu.vn/.../QCDT_2025_5445_QD-DHBK.pdf` | 2026-08-03 / 2025-05-28 | 71.238 | audience=all, department=academic-affairs, category=academic-regulations, language=vi, source_format=pdf, source_pages=34 |
| 2 | Quy định ngoại ngữ đối với sinh viên chính quy từ khóa K70 | `ctt.hust.edu.vn/.../06_ Quy định ngoại ngữ từ K70_chính quy_final.pdf` | 2026-08-03 / 2025-09-26 | 27.993 | audience=student, department=academic-affairs, category=foreign-language-requirements, language=vi, source_format=pdf, source_pages=20 |
| 3 | Các điểm cập nhật của Quy chế đào tạo HUST năm 2025 | `ctt.hust.edu.vn/.../Diem moi cua QCDT 2025.pdf` | 2026-08-03 / 2025-05-28 | 18.355 | audience=all, department=academic-affairs, category=academic-regulations-update, language=vi, source_format=pdf, source_pages=11 |
| 4 | Quy định đào tạo kỹ sư chuyên sâu 180 tín chỉ | `ctt.hust.edu.vn/.../03_ Quy định đào tạo KS 180 TC_signed.pdf` | 2026-08-03 / 2024-07-29 | 8.464 | audience=all, department=academic-affairs, category=advanced-engineer-program, language=vi, source_format=pdf, source_pages=4 |
| 5 | Kế hoạch đăng ký học tích hợp CT kỹ sư chuyên sâu học kỳ 2025.3 | `ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=30241` | 2026-08-03 / 2026-07-27 | 6.818 | audience=student, department=academic-affairs, category=integrated-engineer-registration, language=vi, semester=2025.3 |
| 6 | Kế hoạch đăng ký lớp học kỳ 1 năm học 2026-2027 | `ctt.hust.edu.vn/DisplayWeb/DisplayBaiViet?baiviet=50623` | 2026-08-03 / 2026-07-20 | 6.343 | audience=student, department=academic-affairs, category=course-registration, language=vi, semester=2026.1 |
| 7 | Hướng dẫn công nhận học phần vào chương trình kỹ sư chuyên sâu | `ctt.hust.edu.vn/.../02_ Hướng dẫn công nhận học phần vào CTĐT KSCS.pdf` | 2026-08-03 / 2025-01-23 | 1.781 | audience=student, department=academic-affairs, category=course-recognition, language=vi, source_format=pdf, source_pages=4 |

Tổng: **7 tài liệu / 140.992 ký tự** (yêu cầu 5–10 tài liệu). URL đầy đủ ghi trong `data/hust/sources.csv`.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. Toàn bộ là văn bản công bố trên cổng thông tin công khai, `license_or_permission` ghi `public-page` / `public-document`.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. Đã kiểm tra bằng script: 7/7 dòng `sources.csv` trỏ tới file có thật, không thiếu, không thừa, không trùng `doc_id`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | chuỗi | `student`, `all` | **Trường quyết định** — tách văn bản dành riêng cho sinh viên khỏi quy chế chung của Đại học. Xem Q5 ở Phần 3: không lọc thì truy vấn bị quy định chung chiếm hết top-3. |
| `category` | chuỗi | `course-registration`, `foreign-language-requirements` | Khoanh vùng theo loại thủ tục, hữu ích khi corpus mở rộng thêm học phí/ký túc xá. |
| `document_version` | ngày | `2025-05-28` | Quy chế có nhiều phiên bản (2023 và 2025 cùng tồn tại trong corpus); dùng để ưu tiên bản mới và kiểm tra độ cũ của câu trả lời. |
| `semester` | chuỗi | `2026.1`, `2025.3` | Thông báo đăng ký lặp lại mỗi kỳ với nội dung gần giống nhau; thiếu trường này thì không phân biệt được kỳ nào. |
| `source_url` | URL | `https://ctt.hust.edu.vn/...` | Truy vết nguồn cho từng câu trả lời của agent (`KnowledgeBaseAgent` đưa thẳng vào prompt). |
| `retrieved_at` | ngày | `2026-08-03` | Ghi nhận thời điểm crawl để biết dữ liệu đã cũ bao lâu. |
| `doc_id`, `chunk_index` | chuỗi/số | `hust-academic-regulations-2025`, `12` | Do `ingest.py` gắn tự động lên từng chunk; cần cho `delete_document()` và cho việc chấm hit@k. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

**Cấu hình chung:** embedder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`EMBEDDING_PROVIDER=local`), corpus `data/hust`, top-k = 3. Mock embedder chỉ dùng để chạy unit test, không dùng cho mọi con số trong báo cáo này.

### Phân tích đường cơ sở (Baseline Analysis)

`ChunkingStrategyComparator().compare(text, chunk_size=500)` trên 3 tài liệu có kích thước rất khác nhau:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Kế hoạch đăng ký 2026.1 (6.343 ký tự) | FixedSizeChunker (`fixed_size`) | 14 | 499,5 | Không — cắt giữa câu, một mốc thời gian có thể bị tách khỏi ngày |
| | SentenceChunker (`by_sentences`) | 19 | 330,9 | Có — trọn câu, nhưng mất liên kết giữa mục và nội dung |
| | RecursiveChunker (`recursive`) | 16 | 394,6 | Khá — ưu tiên ranh giới đoạn trước |
| Hướng dẫn công nhận học phần (1.781 ký tự) | FixedSizeChunker | 4 | 482,8 | Không |
| | SentenceChunker | 6 | 295,3 | Có |
| | RecursiveChunker | 5 | 354,8 | Khá |
| Quy chế đào tạo 2025 (71.238 ký tự) | FixedSizeChunker | 159 | 497,7 | Không — cắt ngang khoản, mất số Điều |
| | SentenceChunker | 210 | 337,9 | Có ở mức câu, nhưng chunk ngắn nên loãng ngữ cảnh |
| | RecursiveChunker | 187 | 379,6 | Khá |

**Nhận xét baseline:** `fixed_size` cho độ dài đều nhất (~498) nhưng đó chính là điểm yếu — nó đều vì không quan tâm nội dung. `by_sentences` tạo nhiều chunk nhất và ngắn nhất, nên mỗi chunk mang ít thông tin. Cả ba đều **không giữ được số Điều/Chương**, vốn là cấu trúc quan trọng nhất của văn bản quy định.

### Chiến lược của từng thành viên

**Thành viên 1 — Đỗ Thanh Tùng**
- **Loại chiến lược:** custom — `HeadingChunker(max_chunk_size=800)`
- **Mô tả & lý do chọn cho chủ đề này:** Corpus là văn bản quy định có cấu trúc 3 tầng `Chương → Điều → khoản` (riêng Quy chế 2025 có 57 tiêu đề Markdown). Chunker cắt theo ranh giới tiêu đề, và **gắn breadcrumb tiêu đề cha lên đầu mỗi chunk** để embedding mang theo số Điều — thứ mà cắt theo ký tự làm mất hoàn toàn. Mục dài quá `max_chunk_size` được chia tiếp bằng `RecursiveChunker` nhưng breadcrumb được lặp lại trên từng mảnh, nên không mảnh nào mất số Điều. Đây cũng là yêu cầu bắt buộc của lớp K3 (`K3_VARIANT.md`: ít nhất một thành viên chunk theo tiêu đề/mục).
- **Code snippet:**
```python
class HeadingChunker:
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(\S.*?)\s*$")

    def chunk(self, text: str) -> list[str]:
        preamble, sections = self._parse_sections(text)
        if not sections:                       # văn bản không có tiêu đề
            return RecursiveChunker(chunk_size=self.max_chunk_size).chunk(text)

        chunks, stack = [], []
        if preamble:
            chunks.extend(self._emit(preamble, ""))
        for index, (level, title, body) in enumerate(sections):
            while stack and stack[-1][0] >= level:
                stack.pop()
            has_subsections = index + 1 < len(sections) and sections[index + 1][0] > level
            if body and len(body) < self.min_body_chars and has_subsections:
                title = f"{title} {' '.join(body.split())}"   # tiêu đề nhóm -> gộp vào breadcrumb
                body = ""
            stack.append([level, title])
            if body:
                breadcrumb = self.breadcrumb_separator.join(entry[1] for entry in stack)
                chunks.extend(self._emit(body, breadcrumb))   # breadcrumb lặp lại trên mọi mảnh
        return chunks
```
Ví dụ chunk sinh ra:
```text
Quy chế đào tạo của Đại học Bách khoa Hà Nội năm 2025 > CHƯƠNG I NHỮNG QUY ĐỊNH CHUNG > Điều 9. Học phí
- 1. Người học có nghĩa vụ nộp học phí đầy đủ và đúng thời hạn theo quy định.
- 2. Người học không nộp đủ học phí sau thời gian quy định tại khoản 1 Điều này sẽ bị
đình chỉ đăng ký học tập một học kỳ kế tiếp.
```

**Thành viên 2 — Trần Hải Quân**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)` — đường cơ sở của nhóm
- **Mô tả & lý do chọn:** Giữ làm mốc so sánh cho mọi chiến lược khác. Overlap 50 ký tự nhằm giảm rủi ro một mốc thời gian hoặc một điều kiện bị cắt đôi ở ranh giới chunk. Đây là chiến lược đơn giản nhất, không dùng bất kỳ giả định nào về cấu trúc tài liệu, nên là chuẩn tham chiếu công bằng.

**Thành viên 3 — Hoàng Hải Dương**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`
- **Mô tả & lý do chọn:** Mỗi chunk trọn 3 câu nên không bao giờ cắt giữa câu, hợp với các đoạn văn xuôi trong quy chế. Điểm cần lưu ý khi trình bày: regex tách câu theo `.`/`!`/`?` bị nhiễu bởi văn phong hành chính tiếng Việt (`TS.`, `Điều 9.`, `2025.3`, `115 TC.`), nên số chunk thực tế cao hơn số câu thật.

**Thành viên 4 — Nguyễn Thành Long**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=500)`
- **Mô tả & lý do chọn:** Thử lần lượt các dấu phân cách `["\n\n", "\n", ". ", " ", ""]`, nên ưu tiên giữ trọn đoạn trước, chỉ khi đoạn quá dài mới hạ xuống mức câu rồi mức từ. Đây là dung hòa giữa "đều đặn" của FixedSize và "trọn ý" của Sentence.

**Thành viên 5 — Nguyễn Minh Phương (thu thập dữ liệu)**
- **Không chạy chiến lược chunking.** Phụ trách: chọn 7 nguồn công khai trên `ctt.hust.edu.vn`, chuyển PDF → Markdown, làm sạch header/footer lặp, viết YAML front matter cho từng file, lập `sources.csv` và kiểm tra khớp 1-1 với file trên đĩa.
- Quyết định dữ liệu quan trọng: **loại `data/k3_university/` (dữ liệu khởi động mẫu, `source_url` là `example.edu`) khỏi corpus benchmark** để tránh chunk nội dung bịa lẫn vào kết quả; mọi pipeline chỉ trỏ vào `data/hust`.

### So Sánh Giữa Các Thành Viên

Cùng corpus, cùng 5 câu hỏi, top-k = 3. Cách chấm theo `docs/SCORING.md`: 2 điểm nếu tài liệu đúng ở hạng 1 **và** chunk truy xuất được chứa đúng dữ kiện của gold answer; 1 điểm nếu tài liệu đúng có trong top-3 nhưng dữ kiện không nằm trong chunk hoặc không ở hạng 1; 0 điểm nếu tài liệu đúng không lọt top-3.

| Thành viên | Chiến lược (Strategy) | Số chunk | hit@1 | hit@3 | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|---:|---:|---:|----------------------|-----------|----------|
| Trần Hải Quân | FixedSize(500/50) | 316 | 3/5 | 4/5 | **5** | Đơn giản, độ dài đều, không phụ thuộc định dạng | Cắt giữa câu — top-1 của Q2 mở đầu bằng `"Kế hoạch năm học thì chế độ nghỉ tạm thời..."`, cụt đầu và lệch chủ đề |
| Hoàng Hải Dương | Sentence(3) | 345 | 4/5 | 4/5 | **6** | Không bao giờ cắt giữa câu; tốt nhất ở Q5 | Chunk ngắn, loãng ngữ cảnh; regex câu nhiễu với `Điều 9.` |
| Nguyễn Thành Long | Recursive(500) | 368 | 4/5 | 4/5 | **6** | Cân bằng nhất; ổn định trên cả 5 câu | Vẫn không giữ được số Điều |
| Đỗ Thanh Tùng | Heading(800) | 290 | 4/5 | 4/5 | **5** | **Chiến lược duy nhất truy xuất được Q3**; ít chunk nhất mà vẫn phủ đủ; mỗi chunk tự mô tả được vị trí trong văn bản | Trượt Q5 khi không lọc metadata; breadcrumb làm các chunk cùng tài liệu giống nhau hơn |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Không có chiến lược nào thắng tuyệt đối, và đó là kết luận chính của nhóm. Xét tổng điểm, `Sentence(3)` và `Recursive(500)` cùng đạt 6/10 — cao nhất, nhờ ổn định đều trên các câu hỏi có đáp án nằm trong văn xuôi. Nhưng `Heading(800)` là chiến lược **duy nhất** truy xuất được Q3 (ba chiến lược kia trượt hoàn toàn khỏi top-3), đồng thời tạo ít chunk nhất (290 so với 316–368) mà vẫn phủ đủ nội dung, nghĩa là mỗi chunk mang nhiều thông tin hơn. Với câu hỏi trích dẫn trực tiếp số Điều, breadcrumb giúp truy xuất đúng mục và giúp người đọc kiểm chứng ngay câu trả lời nằm ở Điều nào — giá trị này không thể hiện hết trên điểm số. Nếu triển khai thật, nhóm sẽ **kết hợp**: chunk theo tiêu đề để giữ cấu trúc, đồng thời hạ `max_chunk_size` để mỗi Điều dài được tách theo khoản.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy, khai báo trong `scripts/benchmark.py`.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Hạn cuối đóng hệ thống đăng ký trực tuyến học kỳ 2026.1 là ngày nào? | 22/08/2026 đóng hệ thống đăng ký trực tuyến; 28/08/2026 kết thúc toàn bộ công tác đăng ký. | `hust-course-registration-20261` → mục *3. Các mốc thời gian quan trọng cần lưu ý* |
| 2 | Sinh viên không nộp học phí đúng hạn thì bị xử lý như thế nào? | Bị đình chỉ đăng ký học tập một học kỳ kế tiếp. | `hust-academic-regulations-2025` → *CHƯƠNG I > Điều 9. Học phí*, khoản 2 |
| 3 | Học viên được công nhận tối đa bao nhiêu tín chỉ học trước vào bảng điểm kỹ sư chuyên sâu? | Tối đa 15 tín chỉ học trước; ngoài ra tối đa 12 tín chỉ từ CTĐT cử nhân. | `hust-engineer-course-recognition-guide` → mục *II. Mục đích* |
| 4 | Chuẩn ngoại ngữ đầu ra khi xét tốt nghiệp của chương trình chuẩn là bậc mấy? | Đạt chứng chỉ trình độ tối thiểu **Bậc 3** (Bảng 3.2, theo Bảng 2.1 của Phụ lục). | `hust-foreign-language-regulations-k70` → *Bảng 3.2* |
| 5 | Điều kiện để được đăng ký học tích hợp chương trình kỹ sư chuyên sâu là gì? **(cần lọc metadata)** | Tổng tín chỉ tích lũy đạt từ 115 TC trở lên và đã hoặc đang làm ĐATN cử nhân thì đăng ký Form online trên QLDT; học tích lũy trước tối đa 15 TC cũng cần {tích lũy + đang học} ≥ 115 TC. | `hust-integrated-engineer-registration-20253` → mục *2. Lộ trình và điều kiện đăng ký* |

Bộ câu hỏi đa dạng về dạng: mốc thời gian (Q1), chế tài (Q2), con số định lượng (Q3), mức chuẩn (Q4), điều kiện thủ tục (Q5).

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Hạn cuối đóng hệ thống đăng ký 2026.1 | FixedSize / Sentence / Recursive (2đ) | Có — cả 4 chiến lược | Heading chỉ được 1đ: cả 3 chunk đều đúng tài liệu nhưng rơi vào mục *Thời khóa biểu*, *Hình thức đăng ký*, *Lưu ý quan trọng* — **không** chứa mốc 22/08/2026 |
| 2 | Không nộp học phí bị xử lý thế nào | Sentence / Recursive / Heading (2đ) | Có — cả 4 chiến lược | FixedSize chỉ 1đ: cả 3 chunk đều đúng tài liệu nhưng nói về nghỉ học tạm thời và hoàn 50% học phí, **không chunk nào chứa** chế tài "đình chỉ đăng ký học tập" |
| 3 | Tối đa bao nhiêu tín chỉ được công nhận | **Heading (1đ) — duy nhất** | **Không** với FixedSize / Sentence / Recursive | Ba chiến lược kia không có chunk nào của tài liệu đúng lọt top-3; Heading lấy đúng tài liệu nhưng con số 15 TC nằm ở mảnh khác của cùng mục |
| 4 | Chuẩn ngoại ngữ đầu ra bậc mấy | Không chiến lược nào đạt 2đ | Có — cả 4 chiến lược (1đ) | **Cả 4 đều trả về "Bậc 4" thay vì "Bậc 3"** — xem phân tích lỗi ở Phần 4 |
| 5 | Điều kiện đăng ký học tích hợp | Sentence / Recursive (1đ) | Có với FixedSize/Sentence/Recursive; **không** với Heading | Cần lọc `audience=student` mới đúng — xem dưới |

**Tổng điểm truy xuất theo chiến lược:** FixedSize 5/10 · Sentence 6/10 · Recursive 6/10 · Heading 5/10.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, và Q5 là bằng chứng rõ nhất. Khi **không lọc**, top-3 bị `hust-advanced-engineer-program-regulations` (`audience=all`, quy định chung về chương trình 180 tín chỉ) chiếm sạch với score rất cao — 0,799 / 0,788 / 0,788 — đúng chủ đề nhưng **sai loại tài liệu**: đó là quy định khung, không phải điều kiện đăng ký cụ thể mà sinh viên cần. Khi lọc `metadata_filter={"audience": "student"}`, cả 3 kết quả đều là `hust-integrated-engineer-registration-20253` với score **thấp hơn** (0,739 / 0,727 / 0,710) nhưng **đúng tài liệu**. Bài học: điểm similarity cao không đồng nghĩa kết quả đúng, và metadata là công cụ duy nhất phân biệt được hai tài liệu cùng chủ đề nhưng khác đối tượng áp dụng.
>
> Mặt trái đã kiểm chứng: với các câu hỏi mà đáp án thật sự nằm trong quy chế chung (`audience=all`) như *"Sinh viên bị cảnh báo học tập trong trường hợp nào?"*, bật cùng bộ lọc đó lại **đẩy tài liệu đúng ra khỏi kết quả** (score tụt từ 0,784 xuống 0,590 và trả về tài liệu sai). Lọc metadata phải gắn với ý định của câu hỏi, không bật mặc định.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Score cao ≠ câu trả lời đúng.** Demo trực tiếp Q5 trên giao diện: không lọc cho score 0,799 nhưng sai tài liệu; lọc `audience=student` cho score thấp hơn 0,739 mà đúng. Đây là phản trực giác mạnh nhất nhóm thu được.
> 2. **Không có chiến lược chunking thắng tuyệt đối.** Q3 chỉ `Heading` lấy được, Q5 thì `Heading` lại trượt còn `Sentence`/`Recursive` đạt hạng 1. Chọn chiến lược phải theo dạng câu hỏi, không theo một điểm tổng.
> 3. **Chất lượng chuyển đổi PDF quyết định chất lượng chunking.** Xem phân tích lỗi Q4 bên dưới — một lỗi ở khâu PDF → Markdown làm hỏng chiến lược chunk theo tiêu đề, và không có tham số nào cứu được.

**Phân tích lỗi (Failure Analysis) — Bài tập 3.5**

**Câu hỏi thất bại:** Q4 — *"Chuẩn ngoại ngữ đầu ra khi xét tốt nghiệp của chương trình chuẩn là bậc mấy?"*

**Hiện tượng:** Cả 4 chiến lược đều truy xuất đúng tài liệu `hust-foreign-language-regulations-k70` với score rất cao (0,803 / 0,802 / 0,785 với `Heading`), nhưng chunk hạng 1 chứa *"Chuẩn đầu ra khi xét tốt nghiệp Đạt chứng chỉ trình độ tối thiểu **Bậc 4** (theo Bảng 2.1 của Phụ lục II)"*. Gold answer là **Bậc 3** (Bảng 3.2, chương trình chuẩn); Bậc 4 là mức của Bảng 4.2 dành cho chương trình khác. Agent sẽ trả lời **sai một cách rất tự tin**, vì câu văn được truy xuất có cấu trúc gần như y hệt câu đúng.

**Tại sao?** Ba nguyên nhân cộng dồn:
1. **Lỗi từ khâu chuyển đổi PDF.** Trong file Markdown, các bảng chuẩn ngoại ngữ (Bảng 3.2, 4.2, 5.2…) bị đặt **sau** tiêu đề `### Điều 7. Hiệu lực thi hành`, tức mất liên kết với đúng phụ lục của nó. `HeadingChunker` gắn breadcrumb theo tiêu đề gần nhất nên sinh ra chunk mang nhãn *"Điều 7. Hiệu lực thi hành"* nhưng nội dung lại là bảng chuẩn ngoại ngữ — **breadcrumb sai còn nguy hiểm hơn không có breadcrumb**.
2. **Câu hỏi thiếu định danh chương trình.** "Chương trình chuẩn" không xuất hiện nguyên văn trong tài liệu; tài liệu dùng mã CTĐT và số hiệu bảng. Embedding không có cách nào phân biệt Bảng 3.2 với Bảng 4.2 vì hai dòng gần như trùng chữ.
3. **Bảng bị làm phẳng thành văn xuôi.** Sau khi chuyển đổi, quan hệ hàng–cột biến mất, nên chunk mất luôn thông tin "bảng này thuộc chương trình nào".

**Đề xuất cải thiện:**
- **Sửa ở tầng dữ liệu, không phải tầng chunker:** làm sạch lại file nguồn để mỗi bảng nằm dưới đúng tiêu đề phụ lục của nó (`#### Bảng 3.2 — CTĐT chuẩn`). Đây là cách rẻ nhất và hiệu quả nhất.
- Bổ sung metadata `program_type` (`standard` / `elitech`) để lọc như đã làm với `audience` ở Q5.
- Viết lại câu hỏi đánh giá cho khớp từ vựng của tài liệu, hoặc chấp nhận rằng câu hỏi mơ hồ thì không hệ thống RAG nào trả lời đúng được.
- Khi hiển thị cho người dùng, luôn kèm breadcrumb + `source_url` để người đọc tự phát hiện "Điều 7. Hiệu lực thi hành" là ngữ cảnh vô lý cho câu hỏi về chuẩn ngoại ngữ.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một corpus và cùng 5 câu hỏi, bốn chiến lược cho tổng điểm chênh nhau rất ít (5–6/10) nhưng **thất bại ở những câu khác nhau** — nghĩa là điểm tổng che giấu sự khác biệt thật. Chỉ khi mổ từng câu mới thấy `Heading` mạnh ở câu trích dẫn cấu trúc còn `Sentence`/`Recursive` mạnh ở câu hỏi văn xuôi. Bài học thứ hai: phần lớn lỗi nhóm gặp **không nằm ở thuật toán chunking mà nằm ở chất lượng dữ liệu đầu vào** (bảng bị đặt sai tiêu đề, PDF làm phẳng cấu trúc). Tối ưu tham số chunk_size không cứu được lỗi dữ liệu.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Thứ nhất, dành nhiều thời gian hơn cho khâu làm sạch Markdown, đặc biệt là các bảng — kiểm tra thủ công rằng mỗi bảng nằm đúng dưới tiêu đề của nó trước khi ingest. Thứ hai, thiết kế metadata giàu hơn ngay từ đầu (`program_type`, `applies_to_cohort`) thay vì chỉ `audience`, vì corpus quy định có rất nhiều văn bản cùng chủ đề nhưng khác đối tượng áp dụng. Thứ ba, cân bằng kích thước corpus: hiện Quy chế 2025 chiếm 71/141 nghìn ký tự (một nửa corpus) nên nó áp đảo kết quả tìm kiếm ở nhiều truy vấn không liên quan; nên tách nó thành các file nhỏ theo chương.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 6 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **34 / 40** |

**Căn cứ tự đánh giá:** Chất lượng truy xuất chấm đúng 6/10 theo điểm cao nhất trong nhóm (`Sentence`/`Recursive`), không làm tròn lên — nhóm chọn báo cáo trung thực số đo được kèm phân tích nguyên nhân, vì `docs/SCORING.md` nêu rõ *"Chiến lược > Hiệu suất"*. Lựa chọn tài liệu trừ 1 điểm do lỗi bảng bị đặt sai tiêu đề trong file ngoại ngữ (phát hiện qua Q4) chưa được sửa lại ở bản nộp.

---

## Phụ lục — Cách tái lập kết quả

```bash
pip install -r requirements.txt -r requirements-local.txt
# .env: EMBEDDING_PROVIDER=local

python3 scripts/benchmark.py            # sinh report/benchmark_results.md (bảng hit@k + chi tiết top-3)
python3 scripts/demo_server.py          # giao diện demo tại http://127.0.0.1:8000
```

Thêm chiến lược mới: khai báo một dòng vào `STRATEGIES` trong `scripts/benchmark.py`, script tự chạy và chấm cùng bộ 5 câu hỏi.
