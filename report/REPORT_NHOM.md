\# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [2k355]

**Thành viên:** 
|STT|Mã HV|Họ và tên|
|---|-----|---------|
|1| 2A202601649 | Lê Công Dũng |
|2| 2A202601215 | Phùng Hồng Phước |
|3| 2A202601567 | Trần Đức Mạnh| 
**Ngày:** [02/08/2026]

> Nộp 1 bản / nhóm. Phần cá nhân mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`.

---

## 1. Lựa chọn tài liệu (Document Set Quality) - Nhóm

### Phạm vi bộ tài liệu

**Chủ đề cố định theo lớp K3:** Dịch vụ / quy định đại học.

**Phạm vi cụ thể nhóm tập trung:**  
Nhóm chọn bộ tài liệu về dịch vụ và quy định hỗ trợ sinh viên VinUniversity, gồm thư viện, hỗ trợ học tập, sức khỏe tinh thần - thể chất, phát triển nghề nghiệp, hỗ trợ tài chính, học bổng và ký túc xá.

### Định dạng và cách nạp dữ liệu

Tất cả tài liệu đã được chuyển sang `.md` và đặt trong `data/k3_university/`. Mỗi file có YAML front matter ở đầu file để `ingest.py` đọc metadata, sau đó phần nội dung bên dưới được đưa vào chunker.

Cách nạp đã kiểm tra:

```python
from ingest import build_knowledge_base
from src.chunking import RecursiveChunker
from src.embeddings import _mock_embed

store = build_knowledge_base(
    "data/k3_university",
    embedding_fn=_mock_embed,
    chunker=RecursiveChunker(chunk_size=500),
)
print(store.get_collection_size())
```

Kết quả kiểm tra nhanh: nạp được **29 chunk** với `RecursiveChunker(chunk_size=500)`.

### Danh sách tài liệu

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|--------------------|----------------------|----------|-----------------|
| 1 | Dịch vụ mượn tài liệu và thiết bị tại Thư viện VinUniversity | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ | 2026-08-03 / `not-stated` | 1,358 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 2 | Dịch vụ hỗ trợ học tập của Thư viện VinUniversity | https://library.vinuni.edu.vn/services/learning-services/ | 2026-08-03 / `not-stated` | 964 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 3 | Dịch vụ sức khỏe thể chất và tinh thần tại VinUniversity | https://vinuni.edu.vn/vinuni-wellbeing-services/ | 2026-08-03 / `not-stated` | 1,100 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 4 | Dịch vụ phát triển nghề nghiệp tại VinUniversity | https://vinuni.edu.vn/aid/career-services/ | 2026-08-03 / `not-stated` | 1,045 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 5 | Quy trình yêu cầu hỗ trợ tài chính cho sinh viên VinUniversity | https://policy.vinuni.edu.vn/all-policies/guidelines-for-student-financial-support-request/ | 2026-08-03 / `GDL-FAO-001-V2.0 (2025-04-22)` | 1,671 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 6 | Tiêu chí duy trì học bổng đầu vào và hỗ trợ tài chính tại VinUniversity | https://policy.vinuni.edu.vn/all-policies/criteria-to-maintain-the-entry-scholarship-and-financial-aid-support/ | 2026-08-03 / `GDL-SAM-004-V2.1 (2025-09-04)` | 1,274 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 7 | Phòng ở và tiện ích ký túc xá VinUniversity | https://vinuni.edu.vn/student_life/residential-life/dormitory-room/ | 2026-08-03 / `not-stated` | 1,034 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |
| 8 | Quyền tiếp cận dịch vụ hỗ trợ theo Bộ quy tắc sinh viên VinUniversity | https://policy.vinuni.edu.vn/all-policies/student-affairs-regulations-code-of-conduct/ | 2026-08-03 / `VU_CTSV02.EN V5.0 (2025-12-24)` | 1,610 | `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`, `department`, `category`, `language`, `source_language`, `content_form` |

### Cấu trúc metadata

| Trường metadata | Kiểu | Ví dụ giá trị | Tác dụng cho retrieval |
|----------------|------|---------------|------------------------|
| `doc_id` | string | `vinuni-financial-aid-request` | Gắn chunk với tài liệu gốc, hỗ trợ truy vết và xóa theo tài liệu. |
| `title` | string | `Quy trình yêu cầu hỗ trợ tài chính...` | Cho tín hiệu ngữ nghĩa và giúp đọc kết quả dễ hơn. |
| `source_url` | URL string | `https://policy.vinuni.edu.vn/...` | Kiểm chứng nguồn chính thức. |
| `retrieved_at` | date string | `2026-08-03` | Kiểm tra độ mới của dữ liệu. |
| `document_version` | string | `GDL-FAO-001-V2.0 (2025-04-22)` | Phân biệt phiên bản chính sách. |
| `audience` | string | `undergraduate-student` | Lọc theo nhóm sinh viên phù hợp. |
| `department` | string | `library-and-learning-resources` | Lọc theo đơn vị phụ trách. |
| `category` | string | `library-borrowing` | Lọc theo nhóm nhu cầu/dịch vụ. |
| `language` | string | `vi` | Lọc theo ngôn ngữ nội dung. |
| `content_form` | string | `translated-summary` | Biết đây là bản tóm lược/dịch thay vì nguyên văn đầy đủ. |

---

## 2. Thiết kế chiến lược (Strategy Design) - Nhóm

### Baseline analysis

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=500)` trên 3 tài liệu đại diện:

| Tài liệu | Chiến lược | Số chunk | Độ dài trung bình | Nhận xét |
|----------|------------|----------|-------------------|----------|
| `vinuni-career-development` | FixedSizeChunker | 3 | 381.7 | Nhanh, đều kích thước, nhưng có thể cắt ngang ý. |
| `vinuni-career-development` | SentenceChunker | 3 | 346.7 | Giữ câu hoàn chỉnh, hợp với nội dung mô tả dịch vụ. |
| `vinuni-career-development` | RecursiveChunker | 3 | 347.0 | Giữ đoạn/câu tốt, ít phá vỡ cấu trúc. |
| `vinuni-dormitory-services` | FixedSizeChunker | 3 | 378.0 | Tốt cho baseline nhưng đôi khi tách giữa thông tin phòng và tiện ích. |
| `vinuni-dormitory-services` | SentenceChunker | 3 | 343.0 | Dễ đọc, chunk bám theo từng ý dịch vụ. |
| `vinuni-dormitory-services` | RecursiveChunker | 3 | 343.3 | Cân bằng giữa kích thước và tính mạch lạc. |
| `vinuni-financial-aid-request` | FixedSizeChunker | 4 | 455.2 | Ít chunk hơn nhưng có nguy cơ gộp nhiều bước quy trình. |
| `vinuni-financial-aid-request` | SentenceChunker | 5 | 332.6 | Phù hợp với câu hỏi hỏi thời hạn/quy trình cụ thể. |
| `vinuni-financial-aid-request` | RecursiveChunker | 5 | 332.6 | Phù hợp nhất với văn bản có heading và đoạn ngắn. |

### Chiến lược của từng thành viên

**Thành viên 1 - Fixed-size tuned**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=450, overlap=80)`
- **Lý do chọn:** Đây là baseline nhanh nhất, dễ tái lập và phù hợp khi cần nạp dữ liệu nhanh. Overlap 80 ký tự giúp giảm rủi ro mất thông tin ở ranh giới chunk, nhất là các câu dài về quy trình hoặc điều kiện.
- **Metadata dùng khi lọc:** `category`, `audience`, `department`.

**Thành viên 2 - Sentence-based**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=2)`
- **Lý do chọn:** Bộ tài liệu chủ yếu là mô tả dịch vụ và chính sách ngắn, nên giữ câu hoàn chỉnh giúp gold answer dễ nằm gọn trong một chunk. Chiến lược này hợp với câu hỏi hỏi số lượng, thời hạn, địa điểm hoặc điều kiện.
- **Metadata dùng khi lọc:** `category`, `department`, `document_version`.

**Thành viên 3 - Recursive / section-aware**
- **Loại chiến lược:** `RecursiveChunker(separators=["\n## ", "\n\n", "\n", ". ", " "], chunk_size=500)`
- **Lý do chọn:** Các file `.md` có tiêu đề và một số phần như “Điều kiện”, “Thời hạn và quy trình”, nên ưu tiên tách theo section/đoạn sẽ giữ ngữ cảnh tốt hơn fixed-size. Đây là chiến lược nhóm ưu tiên cho demo vì cân bằng được độ mạch lạc và số lượng chunk.
- **Metadata dùng khi lọc:** `category`, `department`, `audience`, `source_url`.

### So sánh giữa các thành viên

| Thành viên | Chiến lược | Điểm truy xuất dự kiến (/10) | Điểm mạnh | Điểm yếu |
|------------|------------|------------------------------|-----------|----------|
| Thành viên 1 | Fixed-size tuned | 7 | Rất nhanh, đơn giản, ít tham số. | Có thể cắt ngang câu hoặc heading. |
| Thành viên 2 | Sentence-based | 8 | Câu trả lời cụ thể thường nằm gọn trong chunk. | Nếu một ý trải qua nhiều câu/đoạn thì có thể thiếu ngữ cảnh. |
| Thành viên 3 | Recursive / section-aware | 9 | Giữ cấu trúc đoạn và heading tốt nhất. | Cần chọn separator và chunk size phù hợp. |

**Chiến lược tốt nhất cho chủ đề này:**  
Nhóm chọn `RecursiveChunker` có ưu tiên heading/đoạn làm chiến lược chính, vì dữ liệu là tài liệu chính sách và dịch vụ đã được format bằng Markdown. Metadata filtering vẫn rất quan trọng cho các câu hỏi dễ nhầm giữa hỗ trợ tài chính, học bổng, quyền sinh viên và dịch vụ sinh viên.

---

## 3. Câu hỏi đánh giá & chất lượng truy xuất - Nhóm

### Bộ 5 câu hỏi đánh giá chung của nhóm

Lưu ý: đây là **bộ câu hỏi chung cho cả nhóm**. Mỗi thành viên dùng cùng 5 câu hỏi này để chạy chiến lược riêng, sau đó so sánh kết quả.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk/tài liệu chứa thông tin |
|---|-----------------|----------------------------------|-------------------------------|
| 1 | Sinh viên đại học VinUniversity được mượn tối đa bao nhiêu tài liệu và trong bao lâu? | Sinh viên đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần. Sách có thể gia hạn một lần thêm 1 tuần nếu chưa quá hạn và không có người khác yêu cầu giữ sách. | `vinuni-library-borrowing`, đoạn đầu về mượn tài liệu |
| 2 | Nếu muốn yêu cầu hỗ trợ tài chính cho học kỳ Thu, sinh viên cần nộp hồ sơ trong khoảng thời gian nào và hạn xử lý là ngày nào? | Đợt học kỳ Thu nhận hồ sơ từ 20/6 đến 10/7 và có hạn xử lý 2/8. | `vinuni-financial-aid-request`, mục “Thời hạn và quy trình” |
| 3 | Học bổng Full và 100% cần GPA tối thiểu bao nhiêu để duy trì? | Học bổng Full và 100% yêu cầu GPA tích lũy của năm được đánh giá đạt ít nhất 3.2, tính theo trung bình hai học kỳ chính Thu và Xuân. | `vinuni-scholarship-maintenance`, đoạn về học bổng Full và 100% |
| 4 | Trong ký túc xá VinUni, có những loại căn hộ nào và sinh viên nam/nữ ở tòa nào? | Khu ở có căn 8 người khoảng 96 m2 cấu hình 3/3/2, căn 2 người khoảng 21.2 m2, căn 4 người khoảng 50.5 m2 cấu hình 2/2. Sinh viên nữ ở tòa JA, sinh viên nam ở tòa JB. | `vinuni-dormitory-services`, đoạn đầu về khu nội trú |
| 5 | Với metadata `category=health-and-wellbeing`, sinh viên cần đến phòng nào để nhận dịch vụ y tế trực tiếp và số hotline là gì? | Khi lọc `category=health-and-wellbeing`, tài liệu phù hợp là wellbeing services. Sinh viên có thể đến trực tiếp phòng I119, tầng 1, tòa I; đường dây dịch vụ y tế là (+84) 866 200 019. | `vinuni-wellbeing-services`, đoạn về dịch vụ y tế |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|----------------------------------|----------------------------------|---------|
| 1 | Mượn tối đa bao nhiêu tài liệu và bao lâu? | Sentence-based hoặc Recursive | Có | Câu trả lời nằm trong đoạn đầu, dễ truy xuất. |
| 2 | Thời hạn hỗ trợ tài chính học kỳ Thu | Recursive | Có | Heading “Thời hạn và quy trình” giúp giữ đúng ngữ cảnh. |
| 3 | GPA duy trì học bổng Full/100% | Sentence-based hoặc Recursive | Có | Cần tránh nhầm với học bổng 50%-90% và hỗ trợ tài chính theo nhu cầu. |
| 4 | Loại căn hộ và tòa JA/JB | Recursive | Có | Một đoạn chứa nhiều chi tiết; chunk quá nhỏ có thể thiếu một phần. |
| 5 | Metadata health-and-wellbeing, phòng y tế và hotline | Recursive + metadata filter | Có | Metadata filter giúp loại bỏ các dịch vụ hỗ trợ khác của Student Affairs. |

**Metadata filtering có giúp ích không?**  
Có. Metadata filtering hữu ích nhất ở câu 5 vì query có thể bị lẫn với các tài liệu về hỗ trợ sinh viên, quyền sinh viên hoặc thư viện. Khi lọc `category=health-and-wellbeing`, hệ thống thu hẹp về đúng tài liệu wellbeing và tăng khả năng lấy chunk chứa phòng I119 cùng hotline y tế.

---

## 4. Thuyết trình (Demo) & bài học nhóm

**Những insight nhóm sẽ trình bày:**
- Cùng một bộ tài liệu nhưng chunking theo câu/đoạn cho câu trả lời dễ kiểm chứng hơn fixed-size.
- Metadata như `category`, `department`, `audience` đặc biệt hữu ích khi nhiều tài liệu cùng nói về “hỗ trợ sinh viên”.
- Tài liệu dạng chính sách nên ưu tiên giữ heading và đoạn để tránh tách rời điều kiện, thời hạn và quy trình.

**Bài học rút ra khi so sánh trong nhóm:**  
Fixed-size nhanh và ổn cho baseline, nhưng với tài liệu dịch vụ/quy định, chunk theo câu hoặc theo section thường tạo ngữ cảnh tự nhiên hơn. Nhóm nhận thấy chất lượng dữ liệu và metadata ảnh hưởng nhiều không kém thuật toán chunking.

**Nếu làm lại, nhóm sẽ thay đổi gì trong data strategy?**  
Nhóm sẽ bổ sung thêm metadata `effective_date`, `policy_owner` và `service_location` để lọc tốt hơn. Ngoài ra, nhóm sẽ lưu thêm bản nguyên văn tiếng Anh hoặc trích đoạn nguồn gốc bên cạnh bản tóm lược tiếng Việt để tăng khả năng kiểm chứng.

---

## Tự đánh giá phần nhóm

| Tiêu chí | Điểm tự đánh giá |
|----------|------------------|
| Lựa chọn tài liệu | 9 / 10 |
| Thiết kế chiến lược | 13 / 15 |
| Chất lượng truy xuất | 9 / 10 |
| Thuyết trình | 4 / 5 |
| **Tổng phần nhóm** | **35 / 40** |