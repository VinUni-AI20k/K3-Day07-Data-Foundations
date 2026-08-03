# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** C05_03
**Thành viên:** Nguyễn Huy Nghĩa (2A202601943), Phạm Thế Dũng (2A202601985), Phạm Văn Lưu (2A202601857)
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**

> Quy trình học vụ dành cho sinh viên Trường Đại học Bách khoa – ĐHQG TP.HCM, tập trung vào đăng ký môn học, mã hủy, rút/miễn môn và thanh toán học phí.

### Danh sách tài liệu (Data Inventory)

| #   | Tên tài liệu                            | Nguồn (Source URL)                                                   | Ngày lấy / Phiên bản      | Số ký tự | Metadata đã gán                                                 |
| --- | --------------------------------------- | -------------------------------------------------------------------- | ------------------------- | -------- | --------------------------------------------------------------- |
| 1   | Quy định và điều kiện đăng ký môn học   | https://mybk.hcmut.edu.vn/bksi/public/vi/article/82                  | 2026-08-03 / `not-stated` | 1.331    | `audience`, `department`, `category`, `language`, `institution` |
| 2   | Quy trình các đợt đăng ký môn học       | https://mybk.hcmut.edu.vn/bksi/public/vi/article/111                 | 2026-08-03 / `not-stated` | 1.366    | `audience`, `department`, `category`, `language`, `institution` |
| 3   | Mã hủy đăng ký môn học và nguyên nhân   | https://mybk.hcmut.edu.vn/bksi/public/vi/blog/ma-huu-dang-ky-mon-hoc | 2026-08-03 / 2023-08-03   | 1.102    | `audience`, `department`, `category`, `language`, `institution` |
| 4   | Điều kiện và quy trình rút môn học      | https://mybk.hcmut.edu.vn/bksi/public/vi/blog/rut-mon-hoc            | 2026-08-03 / `not-stated` | 727      | `audience`, `department`, `category`, `language`, `institution` |
| 5   | Thanh toán và thời hạn học phí          | https://mybk.hcmut.edu.vn/bksi/public/vi/blog/hoc-phi                | 2026-08-03 / `not-stated` | 922      | `audience`, `department`, `category`, `language`, `institution` |
| 6   | Quy trình và lưu ý khi xin miễn môn học | https://mybk.hcmut.edu.vn/bksi/public/vi/blog/mien-mon-hoc           | 2026-08-03 / `not-stated` | 884      | `audience`, `department`, `category`, `language`, `institution` |
| 7   | Quy trình sắp xếp TKB và phân công giảng dạy | https://hcmut.edu.vn/document/1751629315673_BK_QT_ED_009_02_Quy%20trinh%20Sap%20xep%20TKB%20Phan%20cong%20Giang%20day_01.7.20255.signed.pdf | 2026-08-03 / BK-QT-ED-009-02 | 1.258 | `audience=staff`, `department`, `category`, `language`, `institution` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu        | Ví dụ giá trị                   | Tại sao hữu ích cho truy xuất (retrieval)?                               |
| ------------------ | ----------- | ------------------------------- | ------------------------------------------------------------------------ |
| `doc_id`           | string      | `hcmut-course-withdrawal`       | Định danh ổn định để truy vết và xóa toàn bộ chunk của một tài liệu.     |
| `source_url`       | URL         | `https://mybk.hcmut.edu.vn/...` | Cho phép kiểm chứng nội dung với nguồn chính thức.                       |
| `retrieved_at`     | date        | `2026-08-03`                    | Cho biết thời điểm nhóm thu thập và hỗ trợ đánh giá độ mới.              |
| `document_version` | string/date | `2023-08-03` hoặc `not-stated`  | Phân biệt phiên bản và tránh suy đoán ngày hiệu lực khi nguồn không nêu. |
| `audience`         | enum        | `student`                       | Hỗ trợ bộ lọc bắt buộc `metadata_filter={"audience": "student"}`.        |
| `department`       | enum        | `academic-affairs`, `finance`   | Thu hẹp tìm kiếm theo đơn vị nghiệp vụ.                                  |
| `category`         | string      | `course-withdrawal`, `tuition`  | Phân loại chính xác mục đích và quy trình học vụ.                        |
| `language`         | enum        | `vi`                            | Hỗ trợ lọc theo ngôn ngữ corpus.                                         |
| `institution`      | string      | `HCMUT`                         | Tránh trộn quy định của nhiều trường trong tương lai.                    |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược | Số chunk | Độ dài TB | Giữ được ngữ cảnh? |
|---|---|---:|---:|---|
| Quy trình đăng ký | FixedSize | 5 | 297,2 | Một phần; có thể cắt giữa câu. |
| Quy trình đăng ký | Sentence | 5 | 271,8 | Tốt ở ranh giới câu, kích thước không đều. |
| Quy trình đăng ký | Recursive | 9 | 150,0 | Tốt; ưu tiên đoạn/dòng trước khi chia nhỏ. |
| Điều kiện đăng ký | FixedSize | 5 | 290,2 | Một phần; có đoạn bị tách khỏi tiêu đề. |
| Điều kiện đăng ký | Sentence | 4 | 331,2 | Khá tốt; câu liên quan được giữ cùng nhau. |
| Điều kiện đăng ký | Recursive | 7 | 188,4 | Tốt; giữ được cấu trúc đoạn ngắn. |
| Thanh toán học phí | FixedSize | 4 | 253,0 | Một phần; danh sách có thể bị cắt. |
| Thanh toán học phí | Sentence | 3 | 306,0 | Tốt với phần giải thích dạng câu. |
| Thanh toán học phí | Recursive | 5 | 183,0 | Tốt với tiêu đề, đoạn và danh sách. |

Benchmark được chạy bằng `scripts/evaluate_group_retrieval.py` trên 7 tài liệu. Backend là **local TF-IDF ký tự 3–5 gram**, fit chỉ trên corpus và không dùng mock. Nhóm đã cài `sentence-transformers`, nhưng checkpoint MiniLM không tải hoàn chỉnh trong môi trường chạy; script vẫn hỗ trợ `--provider local` để chạy lại khi checkpoint khả dụng.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Huy Nghĩa**

- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=75)`.
- **Mô tả & lý do chọn:** Kích thước cố định tạo baseline dễ dự đoán; overlap 75 ký tự giúp giữ ngữ cảnh gần biên chunk. Chiến lược tạo 19 chunk, độ dài trung bình 446,8 ký tự.
- **Code snippet:** Không có; dùng lớp tích hợp sẵn.

**Thành viên 2 — Phạm Thế Dũng**

- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`.
- **Mô tả & lý do chọn:** Gom ba câu giúp quy định dễ đọc và không cắt giữa câu. Chiến lược tạo 22 chunk, độ dài trung bình 343,6 ký tự, nhưng có thể tách điều kiện và ngoại lệ sang hai chunk.
- **Code snippet:** Không có; dùng lớp tích hợp sẵn.

**Thành viên 3 — Phạm Văn Lưu**

- **Loại chiến lược:** Custom `HeadingSectionChunker(chunk_size=500)`.
- **Mô tả & lý do chọn:** Tài liệu học vụ có cấu trúc Markdown rõ ràng nên tiêu đề cần đi cùng nội dung bên dưới. Section quá dài được chuyển sang `RecursiveChunker`; chiến lược tạo 24 chunk, độ dài trung bình 314,9 ký tự.
- **Code snippet:**

```python
class HeadingSectionChunker:
    def __init__(self, chunk_size=500):
        self.chunk_size = chunk_size
        self.fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text):
        sections = [
            part.strip()
            for part in re.split(r"(?=^#{1,6}\s)", text, flags=re.MULTILINE)
            if part.strip()
        ]
        chunks = []
        for section in sections:
            pieces = self.fallback.chunk(section) if len(section) > self.chunk_size else [section]
            chunks.extend(pieces)
        return chunks
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược | Điểm (/10) | Điểm mạnh | Điểm yếu |
|---|---|---:|---|---|
| Nguyễn Huy Nghĩa | Fixed 500, overlap 75 | 6 | Ít chunk, tốc độ nhanh, overlap giữ một phần ngữ cảnh. | Cắt giữa cấu trúc; không tìm được bảng mã hủy Q2. |
| Phạm Thế Dũng | 3 câu/chunk | 6 | Chunk tự nhiên, dễ đọc. | Điều kiện và ngoại lệ dài có thể nằm ở các chunk khác nhau. |
| Phạm Văn Lưu | Heading + Recursive | 8 | Tiêu đề đi cùng nội dung, top-1 đúng tài liệu ở 5/5 câu. | Bảng dài vẫn bị chia nhỏ; Q2 lấy đúng tài liệu nhưng sai dòng. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> Heading + Recursive tốt nhất với 8/10 vì tiêu đề của các quy trình học vụ chứa tín hiệu truy xuất mạnh và giúp cô lập từng mục như Đợt 1, Thời hạn hoặc Điều kiện. Tuy nhiên, Q2 cho thấy chia theo tiêu đề chưa đủ cho bảng dài; chunker cần nhận biết từng hàng bảng để giữ mã và ý nghĩa trong cùng một đơn vị.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi | Câu trả lời chuẩn | Chunk chứa thông tin |
|---:|---|---|---|
| 1 | Sinh viên đại học được đăng ký tối đa bao nhiêu tín chỉ trong đợt 1? | Tối đa 25 tín chỉ trong đợt 1. | `hcmut-course-registration-process::chunk_1` |
| 2 | Mã hủy T khi đăng ký môn học có nghĩa là gì? | Mã T nghĩa là trùng giờ trong thời khóa biểu. | `hcmut-registration-cancellation-codes::chunk_2` |
| 3 | Sinh viên được đăng ký rút môn trong thời gian nào và môn rút có tính học phí không? | Từ tuần thứ hai đến trước tuần thi cuối kỳ một tuần; môn rút vẫn tính học phí. | `hcmut-course-withdrawal::chunk_0` |
| 4 | Học phí học kỳ dự thính phải thanh toán khi nào? | Trong tuần đầu tiên của học kỳ dự thính. | `hcmut-tuition-payment::chunk_1` |
| 5 | Đơn vị nào xử lý yêu cầu mở thêm lớp và điều chỉnh thời khóa biểu ở đợt 2? | Sinh viên liên hệ giảng viên/khoa; nếu khoa đồng ý thì gửi đề nghị tới Phòng Đào tạo, nơi xử lý khoảng một đến hai ngày làm việc. Dùng `metadata_filter={"audience": "student"}`. | `hcmut-course-registration-process::chunk_2` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất | Chunk liên quan trong top-3? | Ghi chú |
|---:|---|---|---|---|
| 1 | Tín chỉ tối đa đợt 1 | Heading | Có, top-1; score 0,6041 | Chunk chứa đủ “25 tín chỉ”; đạt 2/2. |
| 2 | Ý nghĩa mã T | Heading | Một phần | Top-1 đúng tài liệu nhưng là chunk giới thiệu; dòng `T` không vào top-3; đạt 1/2. |
| 3 | Thời gian và học phí khi rút môn | Heading | Có, top-1; score 0,6250 | Một chunk chứa cả thời gian và nghĩa vụ học phí; đạt 2/2. |
| 4 | Hạn học phí dự thính | Heading/Sentence | Có, top-1; score 0,6558 | Chunk “Thời hạn” chứa câu trả lời đầy đủ; đạt 2/2. |
| 5 | Mở thêm lớp ở đợt 2 | Heading | Có, chunk hỗ trợ ở top-2 | Top-1 đúng tài liệu nhưng chi tiết trả lời ở top-2; đạt 1/2. |

Điểm tổng hợp tốt nhất: **8/10**. Đánh giá theo hướng extractive: chỉ coi câu trả lời đủ căn cứ khi một chunk riêng lẻ trong top-3 chứa toàn bộ các ý bắt buộc của gold answer; không cộng điểm cho thông tin suy đoán.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Có, rõ nhất ở Q5. Với Sentence và Heading, tìm kiếm không lọc đưa tài liệu vận hành `audience=staff` lên top-1; khi dùng `metadata_filter={"audience": "student"}`, tài liệu quy trình sinh viên lên top-1 và cả ba kết quả đều thuộc corpus sinh viên. Với FixedSize, tài liệu staff đứng top-2 trước lọc và bị loại hoàn toàn sau lọc.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Cấu trúc tiêu đề quan trọng với tài liệu quy trình: Heading đạt 8/10, cao hơn Fixed và Sentence cùng đạt 6/10.
- Metadata `audience` xử lý nhiễu mà similarity thuần túy không phân biệt: Q5 không lọc ưu tiên quy trình staff, còn lọc đưa hướng dẫn sinh viên lên đầu.
- Truy xuất đúng tài liệu chưa đủ; Q2 trả về đúng bảng mã hủy nhưng sai chunk chứa dòng mã `T`, nên agent vẫn thiếu căn cứ để trả lời.

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng corpus và backend, thay đổi ranh giới chunk làm kết quả khác rõ rệt. FixedSize ít chunk và nhanh nhưng dễ cắt cấu trúc; Sentence dễ đọc nhưng có thể tách điều kiện khỏi ngoại lệ; Heading giữ ý theo mục nên ổn định hơn cho câu hỏi về quy trình và thời hạn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ xử lý bảng theo từng hàng và lặp lại tiêu đề bảng trong mỗi chunk để sửa Q2. Nhóm cũng sẽ bổ sung metadata `effective_date`, kiểm tra phiên bản nguồn định kỳ và chạy lại script bằng MiniLM đa ngữ khi checkpoint tải ổn định để so sánh TF-IDF với embedding neural.

**Failure case:** Q2 là trường hợp thất bại chính. Truy vấn lấy đúng tài liệu mã hủy ở top-1 nhưng chunk trả về chỉ chứa tiêu đề và phần giới thiệu, trong khi dòng `T — trùng giờ thời khóa biểu` nằm ở `chunk_2`. Nguyên nhân là cả ba chiến lược chưa hiểu cấu trúc bảng; cải thiện đề xuất là `TableRowChunker`, thêm category filter `registration-errors` và mở rộng query bằng cụm “trùng lịch/thời khóa biểu”.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **37 / 40** |
