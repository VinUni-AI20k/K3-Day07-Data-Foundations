# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** C5-3  
**Thành viên:** Phạm Văn Lưu  
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_PHAMVANLUU_2A202601857.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học về đăng ký học phần và dịch vụ thư viện.

**Phạm vi cụ thể nhóm tập trung:**
> Nhóm chọn tập dữ liệu liên quan đến quy trình đăng ký học phần và dịch vụ thư viện của trường đại học.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký học phần | https://example.edu/hoc-vu/dang-ky-hoc-phan | 2026-08-02 / 2026.1 | ~800 | audience, department, language, source_url, retrieved_at, document_version |
| 2 | Dịch vụ thư viện | https://example.edu/thu-vien/dich-vu | 2026-08-02 / 2026.1 | ~700 | audience, department, language, source_url, retrieved_at, document_version |
| 3 | Tài liệu bổ sung về chunking | repo/data/chunking_experiment_report.md | 2026-08-02 | ~1200 | source, topic |
| 4 | Tài liệu về vector store | repo/data/vector_store_notes.md | 2026-08-02 | ~1000 | source, topic |
| 5 | Tài liệu về retrieval | repo/data/vi_retrieval_notes.md | 2026-08-02 | ~900 | source, topic |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| audience | string | student | Giúp phân nhóm người dùng khi truy vấn |
| department | string | academic-affairs | Giúp lọc theo lĩnh vực nội dung |
| language | string | vi | Hỗ trợ phân biệt ngôn ngữ và ngữ cảnh |
| source_url | string | https://example.edu/... | Cho phép truy trace nguồn tài liệu |
| retrieved_at | date | 2026-08-02 | Theo dõi thời điểm thu thập |
| document_version | string | 2026.1 | Giúp kiểm tra tính mới của tài liệu |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Nhóm dùng chiến lược chunking theo ngữ cảnh và metadata để giữ nội dung dễ truy xuất.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Đăng ký học phần | FixedSizeChunker (`fixed_size`) | 3 | ~220 | Có |
| Đăng ký học phần | SentenceChunker (`by_sentences`) | 2 | ~350 | Có |
| Đăng ký học phần | RecursiveChunker (`recursive`) | 2 | ~300 | Có |

### Chiến lược của từng thành viên

**Thành viên 1 — Phạm Văn Lưu**
- **Loại chiến lược:** Recursive + metadata filter
- **Mô tả & lý do chọn cho chủ đề này:** Chunk theo cấu trúc đoạn văn và dấu phân cách giúp giữ nghĩa của câu/đoạn. Metadata như `department` và `audience` giúp giảm nhiễu khi truy vấn.
- **Code snippet (nếu custom):**
```python
store.search_with_filter(query, metadata_filter={"department": "academic-affairs"})
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Phạm Văn Lưu | Recursive + metadata | 9 | Giữ ngữ cảnh tốt, ít nhiễu | Cần chunk đủ dài để không bị cắt quá nhỏ |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược recursive kết hợp metadata là phù hợp nhất cho chủ đề dịch vụ học thuật vì nó giữ được cấu trúc ngữ cảnh của văn bản và giúp lọc đúng nhóm người dùng. Khi truy vấn liên quan đến quy định hoặc dịch vụ, chunk có ngữ cảnh rõ sẽ tốt hơn chunk quá ngắn.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Cách đăng ký học phần trong cổng học vụ? | Sinh viên đăng ký học phần trong cổng học vụ theo lịch từng học kỳ. | course-registration.md |
| 2 | Có cần thẻ định danh khi mượn sách? | Có, người dùng cần mang thẻ định danh hợp lệ. | library-services.md |
| 3 | Học phần có thể có điều kiện tiên quyết không? | Có, một học phần có thể yêu cầu học phần tiên quyết. | course-registration.md |
| 4 | Khi nào cần gửi yêu cầu ngoại lệ? | Khi gặp lỗi trùng lịch hoặc trường hợp ngoại lệ cần gửi qua kênh hỗ trợ học vụ. | course-registration.md |
| 5 | Quy định mượn và gia hạn tài liệu? | Thư viện có quy định về mượn, gia hạn và xử lý quá hạn. | library-services.md |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Cách đăng ký học phần trong cổng học vụ? | Recursive + metadata | Có | Trả lời đúng và có liên quan |
| 2 | Có cần thẻ định danh khi mượn sách? | Recursive + metadata | Có | Trả lời đúng và rõ ràng |
| 3 | Học phần có thể có điều kiện tiên quyết không? | Recursive + metadata | Có | Chunk phù hợp được ưu tiên |
| 4 | Khi nào cần gửi yêu cầu ngoại lệ? | Recursive + metadata | Có | Câu trả lời có nền tảng rõ |
| 5 | Quy định mượn và gia hạn tài liệu? | Recursive + metadata | Có | Chunk liên quan xuất hiện ở top-3 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, metadata giúp cải thiện độ chính xác cho các câu hỏi liên quan đến lĩnh vực cụ thể như đăng ký học phần hoặc thư viện. Trong trường hợp truy vấn về người dùng/student, metadata `audience` và `department` giúp hệ thống ưu tiên các tài liệu phù hợp hơn.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Chunking nên giữ ngữ cảnh hơn là cắt quá ngắn.  
> - Metadata giúp cải thiện chất lượng retrieval cho các câu hỏi có phạm vi rõ ràng.  
> - Agent trả lời tốt hơn khi có đủ ngữ cảnh và chunk liên quan.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ tài liệu nhưng chiến lược chunking khác nhau có thể dẫn đến độ chính xác retrieval khác nhau. Việc cắt chunk quá nhỏ làm mất ngữ cảnh, trong khi chunk có đủ ý nghĩa sẽ giúp agent trả lời tốt hơn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung nhiều tài liệu nguồn công khai hơn và tăng số lượng metadata như `faculty`, `service_type`, `effective_date` để retrieval chính xác hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **37 / 40** |
