# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K3 University Services
**Thành viên:**
- Trương Đình Khoa (nhóm trưởng) — 2A202601297
- Diêm Công Thành (thành viên) — 2A202601689
- Nguyễn Quang Huy (thành viên) — 2A202601873

**Ngày:** 2026-08-03

### Phân công công việc

| Thành viên | Mã học viên | Vai trò | Phần việc chính | Sản phẩm phụ trách |
|------------|-------------|---------|-----------------|--------------------|
| Trương Đình Khoa | 2A202601297 | Nhóm trưởng | Điều phối, hoàn thiện core code, chạy tests, thử `RecursiveChunker` | `src/chunking.py`, `src/store.py`, `src/agent.py`, kết quả kiểm thử và retrieval cá nhân |
| Diêm Công Thành | 2A202601689 | Thành viên | Thu thập/làm sạch tài liệu học phí, học bổng; thử `FixedSizeChunker` baseline | `tuition-extension.md`, `bcu-scholarship-2026.md`, số liệu fixed-size |
| Nguyễn Quang Huy | 2A202601873 | Thành viên | Thu thập/làm sạch tài liệu thư viện, ký túc xá, BHYT; thử `SentenceChunker` | `library-services.md`, `dormitory-registration.md`, `health-insurance-2026.md`, số liệu sentence chunking |
| Cả nhóm | - | Phối hợp | Thống nhất 5 benchmark queries, gold answers, metadata schema và failure analysis | `REPORT_NHOM.md`, `sources.csv` |

## 1. Lựa chọn tài liệu

### Phạm vi bộ tài liệu

Nhóm tập trung vào các dịch vụ và quy định sinh viên UIT: đăng ký học phần, gia hạn học phí, học bổng, thư viện, ký túc xá và bảo hiểm y tế.

### Danh sách tài liệu

| # | Tên tài liệu | Nguồn | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------------------|----------|-----------------|
| 1 | Quy trình đăng ký học phần UIT | https://student.uit.edu.vn/mot-so-quy-trinh-danh-cho-sinh-vien | 2026-08-03 / not-stated | 746 | `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 2 | Tài khoản và dịch vụ thư viện UIT | https://lib.uit.edu.vn/tin-hoat-dong/thong-bao-tai-khoan-thu-vien-danh-cho-tan-sinh-vien-uit-khoa-2024 | 2026-08-03 / 2024-activity-news | 884 | `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 3 | Gia hạn học phí học kỳ 2 đợt 2 UIT | https://ctsv.uit.edu.vn/bai-viet/thong-bao-gia-han-hoc-phi-hoc-ky-2-dot-2-lan-cuoi | 2026-08-03 / 2026-03-23 | 886 | `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 4 | Học bổng chương trình liên kết BCU 2026 | https://oep.uit.edu.vn/vi/node/24821 | 2026-08-03 / 2026-06-01 | 968 | `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 5 | Đăng ký Ký túc xá ĐHQG-HCM cho sinh viên UIT | https://ctsv.uit.edu.vn/bai-viet/nhap-hoc-dang-ky-ky-tuc-xa-dhqg-hcm | 2026-08-03 / 2023-08-19 | 855 | `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |
| 6 | Bảo hiểm y tế sinh viên UIT năm 2026 | https://ctsv.uit.edu.vn/bai-viet/thong-bao-mua-bao-hiem-y-te-nam-2026 | 2026-08-03 / 2025-12-09 | 887 | `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version` |

**Danh sách kiểm tra quản trị dữ liệu:**
- [x] Corpus chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata.

### Cấu trúc Metadata

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|--------------------------------|
| `audience` | string | `student`, `all` | Lọc tài liệu dành cho sinh viên, tránh nhầm với tài liệu cho cán bộ/giảng viên. |
| `department` | string | `student-affairs`, `library` | Khoanh vùng đơn vị phụ trách khi câu hỏi liên quan đến dịch vụ cụ thể. |
| `category` | string | `tuition`, `scholarship`, `dormitory` | Metadata quan trọng nhất để lọc theo chủ đề. |
| `language` | string | `vi` | Hữu ích nếu corpus đa ngữ. |
| `source_url` | string | URL gốc | Giúp truy vết câu trả lời. |
| `retrieved_at` | date string | `2026-08-03` | Cho biết ngày lấy dữ liệu. |
| `document_version` | string | `2026-03-23` | Cho biết phiên bản/ngày hiệu lực khi nguồn có nêu. |

## 2. Thiết kế chiến lược

### Phân tích đường cơ sở

Chạy `ChunkingStrategyComparator().compare()` với `chunk_size=300` trên 3 tài liệu đầu.

| Tài liệu | Strategy | Số chunk | Độ dài TB | Giữ được ngữ cảnh không? |
|----------|----------|----------|-----------|--------------------------|
| Học bổng BCU | `fixed_size` | 4 | 264.5 | Trung bình, có thể cắt giữa ý. |
| Học bổng BCU | `by_sentences` | 3 | 321.0 | Tốt, giữ câu nguyên vẹn. |
| Học bổng BCU | `recursive` | 4 | 240.5 | Tốt, ưu tiên đoạn/câu. |
| Đăng ký học phần | `fixed_size` | 3 | 268.7 | Trung bình. |
| Đăng ký học phần | `by_sentences` | 2 | 371.5 | Tốt nhưng chunk hơi dài. |
| Đăng ký học phần | `recursive` | 3 | 247.3 | Tốt, cân bằng kích thước và ngữ cảnh. |
| Ký túc xá | `fixed_size` | 4 | 236.2 | Trung bình. |
| Ký túc xá | `by_sentences` | 3 | 283.3 | Tốt. |
| Ký túc xá | `recursive` | 4 | 212.2 | Tốt, dễ lọc theo đoạn. |

### Chiến lược của từng thành viên

**Thành viên 1 — Trương Đình Khoa (2A202601297)**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=450)`
- **Mô tả & lý do chọn:** Khoa phụ trách chiến lược recursive vì corpus là các trang hướng dẫn ngắn, có tiêu đề và đoạn văn rõ. Recursive chunking giữ ranh giới đoạn/câu tốt hơn fixed-size, nhưng vẫn fallback được nếu một đoạn quá dài.

**Thành viên 2 — Diêm Công Thành (2A202601689)**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=450, overlap=50)`
- **Mô tả & lý do chọn:** Thành phụ trách fixed-size baseline vì chiến lược này dễ kiểm soát, có overlap để giảm mất ngữ cảnh ở biên chunk và phù hợp làm mốc so sánh. Điểm yếu là có thể cắt giữa câu hoặc giữa một quy trình.

**Thành viên 3 — Nguyễn Quang Huy (2A202601873)**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`
- **Mô tả & lý do chọn:** Huy phụ trách sentence chunking vì tài liệu dịch vụ sinh viên thường viết theo câu hướng dẫn rõ ràng. Chiến lược này giữ câu nguyên vẹn, nhưng nếu câu dài hoặc chứa nhiều ý thì chunk có thể quá rộng.

**Custom theo heading/section đề xuất cho K3:**

```python
class HeadingChunker:
    def chunk(self, text: str) -> list[str]:
        sections = []
        current = []
        for line in text.splitlines():
            if line.startswith("#") and current:
                sections.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current).strip())
        return [section for section in sections if section]
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Strategy | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|------------|----------|----------------------|-----------|----------|
| Trương Đình Khoa | `Recursive(450)` | 9 | Cân bằng giữa độ dài và tính mạch lạc, top-3 có chunk liên quan 5/5. | Với mock embedder, top-1 đôi khi chưa đúng đoạn chứa đáp án chi tiết. |
| Diêm Công Thành | `FixedSize(450/50)` | 8 | Có overlap, một số câu có top-1 tốt. | Cắt giữa câu, khó đọc khi giải thích kết quả. |
| Nguyễn Quang Huy | `Sentence(3)` | 8 | Chunk dễ đọc, giữ câu nguyên. | Chunk dài hơn, có thể chứa nhiều ý không cần thiết. |

Chiến lược tốt nhất cho chủ đề này là recursive hoặc heading-based. Văn bản dịch vụ đại học thường có cấu trúc đoạn/mục rõ, nên giữ ranh giới tự nhiên giúp chunk dễ đọc và dễ truy vết hơn fixed-size.

## 3. Câu hỏi đánh giá & Chất lượng truy xuất

### Câu hỏi đánh giá & câu trả lời chuẩn

| # | Câu hỏi | Gold answer | Chunk chứa thông tin |
|---|---------|-------------|----------------------|
| 1 | Sinh viên xác nhận đăng ký học phần ở hệ thống nào? | Sinh viên xác nhận trên `dkhp.uit.edu.vn` bằng tài khoản chứng thực. | `k3-course-registration::chunk_1` |
| 2 | Sinh viên được gia hạn học phí phải hoàn thành trước ngày nào? | Sinh viên được gia hạn phải hoàn thành học phí trước ngày 17/04/2026. | `k3-tuition-extension::chunk_2` |
| 3 | Học bổng khuyến khích học tập BCU cho sinh viên đứng đầu là bao nhiêu? | Mức học bổng là 3.500.000 đồng cho sinh viên đứng đầu mỗi khóa/ngành. | `k3-bcu-scholarship-2026::chunk_1` |
| 4 | Tân sinh viên đăng ký ký túc xá trong bao nhiêu ngày sau nhập học? | Trong thời hạn 07 ngày kể từ ngày hoàn tất thủ tục nhập học tại trường. | `k3-dormitory-registration::chunk_2` |
| 5 | Sinh viên phải đóng bao nhiêu tiền bảo hiểm y tế năm 2026? | Sinh viên đóng 631.800 đồng sau phần ngân sách nhà nước hỗ trợ. | `k3-health-insurance-2026::chunk_1` |

### Tổng hợp chất lượng truy xuất

| # | Câu hỏi | Strategy tốt nhất | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------|---------------------------------|---------|
| 1 | Hệ thống xác nhận ĐKHP | `FixedSize` | Có | Filter `category=course-registration` loại bỏ tài liệu nhiễu. |
| 2 | Hạn hoàn thành học phí | `Recursive` | Có | Top-1 chứa đúng đoạn hạn hoàn thành. |
| 3 | Mức học bổng BCU | `FixedSize` | Có | Chunk liên quan nằm top-3 với cả ba strategy. |
| 4 | Thời hạn đăng ký KTX | `Sentence` | Có | Filter `audience=student` vẫn còn rộng nhưng top-3 có chunk đúng. |
| 5 | Mức đóng BHYT | `Recursive` | Có | Filter `category=health-insurance` rất hữu ích. |

Lọc bằng metadata giúp rõ nhất ở các câu 1, 2, 3 và 5 vì `category` trùng trực tiếp với chủ đề câu hỏi. Câu 4 dùng `metadata_filter={"audience": "student"}` theo yêu cầu K3, nhưng filter này rộng nên vẫn có thể trả về chunk học bổng hoặc BHYT bên cạnh chunk ký túc xá.

## 4. Demo & Bài học nhóm

**Insights sẽ trình bày:**
- Metadata `category` có tác động lớn hơn lựa chọn chunker khi corpus nhỏ nhưng nhiều chủ đề sinh viên gần nhau.
- Mock embedder không phản ánh tốt ngữ nghĩa tiếng Việt; nên dùng `EMBEDDING_PROVIDER=local` khi so sánh chiến lược thật.
- Chunk theo câu/đoạn giúp giải thích kết quả retrieval dễ hơn chunk fixed-size.

**Bài học rút ra:** Cùng một corpus nhưng chiến lược chunking khác nhau làm thay đổi vị trí chunk chứa đáp án trong top-3. Recursive chunking cho chunk ngắn và mạch lạc, còn sentence chunking dễ đọc nhưng đôi khi gộp nhiều ý.

**Đánh giá phân công:** Khối lượng công việc được chia theo ba mảng tương đương: Khoa phụ trách code và chiến lược recursive, Thành phụ trách nhóm tài liệu tài chính/học bổng và baseline fixed-size, Huy phụ trách nhóm tài liệu dịch vụ sinh viên và sentence chunking. Cả ba cùng rà soát benchmark queries để tránh một người quyết định toàn bộ tiêu chí đánh giá.

**Failure case:** Khi chạy `python main.py "Sinh viên đăng ký ký túc xá ở đâu?"` với mock embedder và không filter, top-1 trả về tài liệu thư viện thay vì ký túc xá. Lỗi này đến từ mock embedding không hiểu ngữ nghĩa và truy vấn không dùng metadata; cải thiện bằng embedder local đa ngữ và filter `category=dormitory`.

## Tự Đánh Giá

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu | 9 / 10 |
| Thiết kế chiến lược | 14 / 15 |
| Chất lượng truy xuất | 9 / 10 |
| Thuyết trình | 5 / 5 |
| **Tổng phần nhóm** | **37 / 40** |
