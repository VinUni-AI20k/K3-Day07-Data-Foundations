# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** C11  
**Thành viên:**  
Bùi Duy Hải  - 2A202601878     
Đoàn Nhật Bình  - 2A202602018    
Phan Bá Khánh Linh  - 2A202601989   
Lê Trung Hiếu  - 2A202601917      
Nguyễn Minh Thu  - 2A202601631  
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Sổ tay sinh viên Đại học Phenikaa — 5 quy định vận hành thường gặp nhất với sinh viên: đăng ký học phần, thanh toán học phí, học bổng khuyến khích học tập, ký túc xá, dịch vụ thư viện.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký khối lượng học tập và rút bớt học phần | [sotaysv.phenikaa-uni.edu.vn/.../1.5-dang-ky-khoi-luong-hoc-tap-va-rut-bot-hoc-phan-da-dang-ky](https://sotaysv.phenikaa-uni.edu.vn/home/1.-hoat-dong-dao-tao-tai-truong-dai-hoc-phenikaa/1.5-dang-ky-khoi-luong-hoc-tap-va-rut-bot-hoc-phan-da-dang-ky) | 2026-08-03 / not-stated | 1197 | audience=student, department=academic-affairs, category=course-registration |
| 2 | Dịch vụ Trung tâm Thông tin - Thư viện | [sotaysv.phenikaa-uni.edu.vn/.../4.-trung-tam-thong-tin-thu-vien](https://sotaysv.phenikaa-uni.edu.vn/home/4.-trung-tam-thong-tin-thu-vien) | 2026-08-03 / not-stated | 1153 | audience=all, department=library, category=library-services |
| 3 | Các quy định về thanh toán học phí | [sotaysv.phenikaa-uni.edu.vn/.../5.-cac-quy-dinh-ve-thanh-toan-hoc-phi](https://sotaysv.phenikaa-uni.edu.vn/home/5.-cac-quy-dinh-ve-thanh-toan-hoc-phi) | 2026-08-03 / not-stated | 970 | audience=student, department=finance, category=tuition |
| 4 | Ký túc xá sinh viên | [sotaysv.phenikaa-uni.edu.vn/.../7.-ky-tuc-xa-sinh-vien](https://sotaysv.phenikaa-uni.edu.vn/home/7.-ky-tuc-xa-sinh-vien) | 2026-08-03 / not-stated | 1121 | audience=student, department=dormitory-management, category=dormitory |
| 5 | Học bổng KKHT, rèn luyện, khen thưởng, kỷ luật sinh viên | [sotaysv.phenikaa-uni.edu.vn/.../2.3-hoc-bong-khuyen-khich-hoc-tap...](https://sotaysv.phenikaa-uni.edu.vn/home/2.-hoat-dong-cong-tac-sinh-vien/2.3-hoc-bong-khuyen-khich-hoc-tap-ren-luyen-khen-thuong-ky-luat-sinh-vien) | 2026-08-03 / not-stated | 3869 | audience=student, department=student-affairs, category=scholarship |

> Nguồn `document_version` không nêu rõ trên trang gốc nên ghi `not-stated` theo quy ước trong `docs/DATA_COLLECTION.md`.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng (Sổ tay sinh viên công khai của Đại học Phenikaa) và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string (enum) | `student`, `all` | Bắt buộc theo K3 — lọc để tránh trả lời sai đối tượng (vd. loại tài liệu không dành cho sinh viên khỏi kết quả). |
| `department` | string | `academic-affairs`, `library`, `finance`, `dormitory-management`, `student-affairs` | Cho phép thu hẹp truy xuất theo đơn vị phụ trách khi câu hỏi nêu rõ phòng/ban. |
| `category` | string | `course-registration`, `tuition`, `scholarship`, `dormitory`, `library-services` | Phân loại chủ đề mịn hơn `department`, hữu ích khi một phòng ban quản lý nhiều loại quy định. |
| `language` | string | `vi` | Chuẩn bị cho trường hợp corpus đa ngôn ngữ trong tương lai. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| k3_university (5 docs) | FixedSizeChunker (`fixed_size`) | 21 | ~475 ký tự | Có, nhưng có thể cắt giữa câu |
| k3_university (5 docs) | RecursiveChunker (`recursive`) | 83 | ~130 ký tự | Có, tôn trọng cấu trúc (\n\n, \n, .) |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây.

---

#### Thành viên 1 — Đoàn Nhật Bình (02018)

- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`
- **Mô tả & lý do chọn:**
  
  Tôi sử dụng Fixed Size Chunking với kích thước 500 ký tự và overlap 50 ký tự để cân bằng giữa lượng ngữ cảnh trong mỗi chunk và số lượng chunk sinh ra. Với tài liệu quy định của trường đại học, kích thước này đủ chứa hầu hết một mục hoặc tiểu mục hoàn chỉnh, đồng thời phần overlap giúp hạn chế mất thông tin khi nội dung bị cắt tại ranh giới chunk.

- **Code snippet (nếu custom):**

```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(text)
```

---

#### Thành viên 2 — Bùi Duy Hải (01878)

- **Loại chiến lược:** `FixedSizeChunker(chunk_size=400, overlap=50)`
- **Mô tả & lý do chọn:**

  Thành viên lựa chọn kích thước chunk nhỏ hơn (400 ký tự) để tăng mức độ tập trung của từng chunk vào một chủ đề cụ thể. Overlap 50 ký tự giúp duy trì ngữ cảnh giữa các chunk liên tiếp và giảm nguy cơ bỏ sót thông tin khi truy xuất.

- **Code snippet (nếu custom):**

```python
chunker = FixedSizeChunker(chunk_size=400, overlap=50)
chunks = chunker.chunk(text)
```

---

#### Thành viên 3 — Nguyễn Minh Thu (01631)

- **Loại chiến lược:** `SentenceChunker`
- **Mô tả & lý do chọn:**

  Sentence Chunking chia tài liệu theo ranh giới câu thay vì theo số ký tự cố định, giúp mỗi chunk giữ được ý nghĩa hoàn chỉnh của câu. Chiến lược này phù hợp với các tài liệu quy định vì hạn chế việc cắt ngang câu, từ đó giúp embedding biểu diễn ngữ nghĩa chính xác hơn.

- **Code snippet (nếu custom):**

```python
chunker = SentenceChunker()
chunks = chunker.chunk(text)
```

---

#### Thành viên 4 — Phan Bá Khánh Linh (01989)

- **Loại chiến lược:** `RecursiveChunker`
- **Mô tả & lý do chọn:**

  Recursive Chunking ưu tiên chia tài liệu theo các dấu phân tách tự nhiên như đoạn văn, dòng trống hoặc câu trước khi mới cắt theo số ký tự. Điều này giúp giữ được cấu trúc của tài liệu, đồng thời tạo các chunk có nội dung mạch lạc và giàu ngữ cảnh hơn so với việc cắt cố định.

- **Code snippet (nếu custom):**

```python
chunker = RecursiveChunker(chunk_size=500)
chunks = chunker.chunk(text)
```

---

#### Thành viên 5 — Lê Trung Hiếu (01917)

- **Loại chiến lược:** `HeadingChunker`

- **Mô tả & lý do chọn:**

  Tôi chọn Heading Chunking vì tài liệu quy định đại học được tổ chức rõ theo tiêu đề và từng mục. Cách này giúp mỗi chunk giữ đúng chủ đề, hạn chế cắt ngang nội dung và cải thiện khả năng truy xuất thông tin liên quan.

- **Code snippet (nếu custom):**

```python
class HeadingChunker:
    """Chia Markdown theo heading và giữ lại ngữ cảnh heading cha."""

    HEADING_PATTERN = re.compile(
        r"^(#{1,6})[ \t]+(.+?)[ \t]*$",
        re.MULTILINE,
    )

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = max(1, chunk_size)
        self._fallback = RecursiveChunker(chunk_size=self.chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        text = text.strip()
        matches = list(self.HEADING_PATTERN.finditer(text))

        # Không có heading thì dùng RecursiveChunker.
        if not matches:
            return self._fallback.chunk(text)

        chunks: list[str] = []
        heading_stack: dict[int, str] = {}

        for index, match in enumerate(matches):
            heading_level = len(match.group(1))

            # Bỏ các heading cùng cấp hoặc cấp con đã kết thúc.
            heading_stack = {
                level: heading
                for level, heading in heading_stack.items()
                if level < heading_level
            }
            heading_stack[heading_level] = match.group(0).strip()

            section_end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )
            section_body = text[match.end():section_end].strip()

            if not section_body:
                continue

            heading_context = "\n\n".join(
                heading_stack[level]
                for level in sorted(heading_stack)
            )

            chunks.extend(
                self._chunk_section(heading_context, section_body)
            )

        return [chunk.strip() for chunk in chunks if chunk.strip()]

    def _chunk_section(
        self,
        heading_context: str,
        section_body: str,
    ) -> list[str]:
        section = f"{heading_context}\n\n{section_body}".strip()

        if len(section) <= self.chunk_size:
            return [section]

        prefix = f"{heading_context}\n\n"
        available_size = self.chunk_size - len(prefix)

        if available_size <= 0:
            return self._fallback.chunk(section)

        body_chunker = RecursiveChunker(chunk_size=available_size)
        body_chunks = body_chunker.chunk(section_body)

        # Lặp lại heading context trên mọi phần của section dài.
        return [
            f"{prefix}{body_chunk}".strip()
            for body_chunk in body_chunks
        ]
```

### So sánh giữa các thành viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|------------|-----------------------|----------------------|-----------|-----------|
| Đoàn Nhật Bình | `FixedSizeChunker(chunk_size=500, overlap=50)` | **10/10 (5/5 câu)** | Chunk đủ lớn để giữ trọn ngữ cảnh của hầu hết các mục quy định; overlap giúp hạn chế mất thông tin ở ranh giới; số lượng chunk vừa phải nên chi phí embedding hợp lý. | Có thể cắt ngang câu hoặc tiểu mục nếu ranh giới nội dung không trùng với kích thước chunk. |
| Bùi Duy Hải | `FixedSizeChunker(chunk_size=400, overlap=50)` | **10/10 (5/5 câu)** | Chunk nhỏ hơn nên nội dung tập trung hơn, phù hợp với các câu hỏi yêu cầu thông tin cụ thể; overlap giúp duy trì ngữ cảnh. | Sinh nhiều chunk hơn, làm tăng chi phí embedding và đôi khi tách rời các quy định dài. |
| Nguyễn Minh Thu | `SentenceChunker` | **10/10 (5/5 câu)** | Chia theo ranh giới câu nên giữ được ý nghĩa hoàn chỉnh của từng câu, giúp embedding biểu diễn ngữ nghĩa tốt hơn. | Nếu thông tin trải dài trên nhiều câu liên tiếp thì một chunk có thể thiếu ngữ cảnh. |
| Phan Bá Khánh Linh | `RecursiveChunker` | **10/10 (5/5 câu)** | Ưu tiên chia theo các ranh giới tự nhiên như đoạn văn, dòng và câu, giúp các chunk mạch lạc và giàu ngữ cảnh. | Kích thước chunk không đồng đều và thuật toán phức tạp hơn Fixed Size Chunking. |
| Lê Trung Hiếu | `HeadingChunker` | **8/10 (4/5 câu)** | Giữ nguyên cấu trúc theo heading và lặp lại ngữ cảnh heading cha, rất phù hợp với tài liệu Markdown về quy định đại học. | Phụ thuộc vào việc tài liệu được định dạng heading đầy đủ; nếu không có heading thì phải dùng chiến lược dự phòng. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> Cả năm chiến lược đều đạt điểm truy xuất **10/10**, cho thấy chúng đều đáp ứng tốt bộ câu hỏi đánh giá của nhóm. Tuy nhiên, với tài liệu quy định đại học được tổ chức rõ theo các tiêu đề và tiểu mục, **HeadingChunker** là chiến lược phù hợp nhất vì mỗi chunk giữ được đúng chủ đề và ngữ cảnh của từng mục. Đối với các loại tài liệu không có cấu trúc heading rõ ràng, **RecursiveChunker** hoặc **FixedSizeChunker** sẽ là những lựa chọn tổng quát và linh hoạt hơn.


## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy. Vị trí "Chunk nào chứa thông tin" được xác định bằng chiến lược `FixedSizeChunker(chunk_size=500, overlap=50)` (Người 1). Các thành viên sử dụng chiến lược chunking khác có thể tạo ra chunk khác nhau, nhưng đều truy xuất từ cùng một tập tài liệu.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-----------------|---------------------------------|---------------------------|
| 1 | Mỗi học kỳ, sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ? | Tối thiểu **08 tín chỉ**, tối đa **16 tín chỉ** mỗi học kỳ. | `k3-course-registration::chunk_1` |
| 2 | Nếu sinh viên còn nợ học phí của học kỳ trước thì điều gì xảy ra khi đăng ký học kỳ tiếp theo? | Sinh viên còn nợ học phí sẽ **không được đăng ký học phần** của học kỳ tiếp theo. | `k3-tuition-payment::chunk_2` |
| 3 | *(cần `metadata_filter={"audience":"student"}`)* Sinh viên đạt học bổng khuyến khích học tập Loại A được nhận mức học bổng bằng bao nhiêu phần trăm số học phí đã nộp? | Loại A bằng **50%** số học phí sinh viên đã nộp trong năm học. | `k3-scholarship-policy::chunk_2` |
| 4 | Chi phí ở ký túc xá phòng 8 sinh viên là bao nhiêu mỗi tháng? | **350.000 VNĐ/sinh viên/tháng.** | `k3-dormitory-policy::chunk_0` |
| 5 | Khu tự học ở tầng 6 của thư viện mở cửa vào những khung giờ nào? | **Thứ 2 đến Chủ nhật, từ 6h30 đến 22h.** | `k3-library-services::chunk_2` |

**Vì sao câu 3 cần `metadata_filter={"audience":"student"}`?**

> Câu hỏi chỉ áp dụng cho **đối tượng sinh viên**, trong khi bộ dữ liệu chứa nhiều tài liệu dành cho nhiều nhóm đối tượng khác nhau. Việc lọc theo `audience="student"` giúp thu hẹp không gian tìm kiếm, loại bỏ các tài liệu không liên quan trước khi tính điểm tương đồng, từ đó tăng khả năng đưa đúng chunk học bổng vào top-k.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — Top-3 chứa chunk liên quan và Agent trả lời đúng (2 điểm), Top-3 có chunk liên quan nhưng Agent trả lời chưa đầy đủ (1 điểm), không có chunk liên quan trong Top-3 (0 điểm).

| # | Câu hỏi | Chiến lược nổi bật | Có chunk liên quan trong Top-3? | Ghi chú |
|---|---------|--------------------|-------------------------------|---------|
| 1 | Mỗi học kỳ đăng ký tối thiểu và tối đa bao nhiêu tín chỉ? | FixedSize (500), Sentence, Heading | Có | Tất cả chiến lược đều truy xuất đúng và Agent trả lời chính xác. |
| 2 | Sinh viên nợ học phí kỳ trước thì sao? | FixedSize (500), Recursive | Có | Các chiến lược đều tìm đúng quy định trong Top-1 hoặc Top-3. |
| 3 | Học bổng Loại A bằng bao nhiêu phần trăm? | HeadingChunker + Metadata Filter | Có | Metadata filtering giúp thu hẹp phạm vi truy xuất đến đúng tài liệu học bổng dành cho sinh viên. |
| 4 | Chi phí phòng 8 sinh viên ký túc xá? | Recursive, FixedSize (400) | Có | Các chunk đều chứa đúng bảng mức phí nên Agent trả lời chính xác. |
| 5 | Khu tự học tầng 6 mở cửa khi nào? | Heading, Recursive | Có | Thông tin nằm trong mục "Giờ mở cửa", các chiến lược đều truy xuất thành công. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Có. Câu hỏi số **3** là trường hợp điển hình vì chỉ liên quan đến **chính sách học bổng dành cho sinh viên**. Metadata filtering giúp loại bỏ các tài liệu không cùng đối tượng trước khi tính độ tương đồng, nhờ đó kết quả truy xuất ổn định và chính xác hơn.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

### Những phân tích (insights) hay nhất nhóm sẽ trình bày

1. **Chiến lược chunking ảnh hưởng đến chất lượng truy xuất.** Fixed Size, Sentence, Recursive và Heading đều có ưu điểm riêng; lựa chọn phù hợp phụ thuộc vào cấu trúc của tài liệu.
2. **HeadingChunker phù hợp với tài liệu quy định dạng Markdown.** Việc giữ nguyên cấu trúc tiêu đề giúp mỗi chunk có chủ đề rõ ràng, cải thiện khả năng truy xuất khi câu hỏi gắn với từng mục cụ thể.
3. **Metadata filtering giúp tăng độ chính xác.** Với các câu hỏi chỉ áp dụng cho một nhóm đối tượng (ví dụ: sinh viên), việc lọc metadata trước khi tìm kiếm giúp giảm nhiễu và nâng cao chất lượng kết quả.

### Bài học rút ra khi so sánh trong nhóm

> Mặc dù cả năm chiến lược đều đạt **10/10** trên bộ câu hỏi đánh giá, mỗi chiến lược vẫn có những ưu và nhược điểm riêng. Fixed Size Chunking đơn giản và hiệu quả, Sentence Chunking giữ trọn ngữ nghĩa câu, Recursive Chunking bảo toàn cấu trúc tự nhiên của văn bản, còn HeadingChunker phát huy lợi thế trên tài liệu Markdown có nhiều tiêu đề. Điều này cho thấy việc lựa chọn chiến lược nên dựa trên đặc điểm của dữ liệu thay vì chỉ dựa trên điểm số.

### Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?

1. Thiết kế bộ câu hỏi đánh giá đa dạng hơn, bao gồm các câu hỏi cần tổng hợp thông tin từ nhiều chunk để phân biệt rõ hơn giữa các chiến lược.
2. Bổ sung thêm metadata (ví dụ: loại tài liệu, chương, mục, đối tượng áp dụng) để hỗ trợ retrieval và filtering hiệu quả hơn.
3. Thử nghiệm thêm các giá trị `chunk_size` và `overlap` khác nhau, đồng thời đánh giá trên nhiều bộ dữ liệu để tìm ra cấu hình phù hợp nhất cho từng loại tài liệu.


## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 0 / 5 |
| **Tổng phần nhóm** | **34 / 40** |
