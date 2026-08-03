# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy định đăng ký học, học phí và các dịch vụ hỗ trợ sinh viên tại Đại học RMIT Việt Nam, gồm thư viện và thẻ sinh viên.

### Kết quả kiểm tra dữ liệu

| Điều kiện | Kết quả | Bằng chứng |
|-----------|---------|------------|
| Có 5–10 tài liệu | Đạt | 7 file Markdown trong `data/k3_university/` |
| Mọi file đủ metadata | Đạt | 7/7 file có `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version` và `audience` |
| `sources.csv` khớp một–một | Đạt | 7 dòng dữ liệu tương ứng đúng 7 `doc_id` và 7 đường dẫn file tồn tại |
| Trường phân vai có ít nhất hai giá trị | Đạt | `audience`: `student` (6 tài liệu), `all` (1 tài liệu) |

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Change or cancel your enrolment | [RMIT Vietnam](https://www.rmit.edu.vn/students/my-studies/enrolment/change-or-cancel-your-enrolment) | 2026-08-03 / `not-stated` | 6,024 | `audience=student`; `department=registrar`; `category=enrolment-policy`; `language=en` |
| 2 | Defer a payment | [RMIT Vietnam](https://www.rmit.edu.vn/students/my-studies/fees-and-payments/defer-a-payment) | 2026-08-03 / `not-stated` | 7,553 | `audience=student`; `department=student-administration`; `category=payment-extension`; `language=en` |
| 3 | Enrolment at RMIT Vietnam | [RMIT Vietnam](https://www.rmit.edu.vn/students/my-studies/enrolment) | 2026-08-03 / `not-stated` | 4,079 | `audience=student`; `department=registrar`; `category=enrolment`; `language=en` |
| 4 | Fees and payments | [RMIT Vietnam](https://www.rmit.edu.vn/students/my-studies/fees-and-payments) | 2026-08-03 / `not-stated` | 4,583 | `audience=student`; `department=student-administration`; `category=tuition-fees`; `language=en` |
| 5 | Borrowing and returning | [RMIT Vietnam](https://www.rmit.edu.vn/libraryvn/borrowing-and-resources/borrowing-and-returning) | 2026-08-03 / `not-stated` | 6,485 | `audience=all`; `department=library`; `category=borrowing-policy`; `language=en` |
| 6 | RMIT student cards | [RMIT Vietnam](https://www.rmit.edu.vn/students/support/admin-support/rmit-student-cards) | 2026-08-03 / `not-stated` | 7,108 | `audience=student`; `department=student-administration`; `category=student-id`; `language=en` |
| 7 | Student support | [RMIT Vietnam](https://www.rmit.edu.vn/students/support) | 2026-08-03 / `not-stated` | 4,368 | `audience=student`; `department=student-services`; `category=support-services`; `language=en` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi định danh duy nhất | `rmit-defer-payment` | Truy vết chunk về đúng tài liệu gốc và đối chiếu với `sources.csv`. |
| `title` | Chuỗi | `Defer a payment` | Hiển thị và nhận diện tài liệu trong kết quả truy xuất. |
| `source_url` | URL công khai | `https://www.rmit.edu.vn/students/...` | Kiểm chứng nội dung và minh bạch nguồn. |
| `retrieved_at` | Ngày ISO `YYYY-MM-DD` | `2026-08-03` | Đánh giá độ mới của bản dữ liệu đã thu thập. |
| `document_version` | Chuỗi phiên bản/ngày hoặc `not-stated` | `not-stated` | Phân biệt các phiên bản chính sách và tránh suy đoán khi nguồn không nêu phiên bản. |
| `audience` | Enum | `student`, `all` | Lọc tài liệu theo nhóm đối tượng; có hai giá trị để chứng minh metadata filtering. |
| `department` | Enum | `registrar`, `library`, `student-administration` | Thu hẹp tìm kiếm theo đơn vị phụ trách dịch vụ hoặc quy định. |
| `category` | Enum | `enrolment-policy`, `tuition-fees`, `borrowing-policy` | Lọc theo nghiệp vụ cụ thể trước khi xếp hạng semantic. |
| `language` | Mã ngôn ngữ | `en` | Chọn tài liệu theo ngôn ngữ khi corpus được mở rộng. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Defer a payment | FixedSizeChunker (`fixed_size`, size=400, overlap=50) | 20 | 392.8 | Có overlap nhưng có thể cắt giữa điều kiện. |
| Defer a payment | SentenceChunker (`by_sentences`, 3 câu/chunk) | 13 | 527.5 | Giữ trọn câu nhưng chunk khá dài. |
| Defer a payment | RecursiveChunker (`recursive`, size=400) | 20 | 343.2 | Giữ tốt ranh giới đoạn/dòng của danh sách điều kiện. |
| Borrowing and returning | FixedSizeChunker (`fixed_size`, size=400, overlap=50) | 17 | 388.4 | Có thể cắt rời hạn mức và quy tắc gia hạn. |
| Borrowing and returning | SentenceChunker (`by_sentences`, 3 câu/chunk) | 9 | 641.7 | Các dòng số liệu ít dấu câu làm chunk quá dài. |
| Borrowing and returning | RecursiveChunker (`recursive`, size=400) | 16 | 360.7 | Giữ các dòng hạn mức/thời hạn gần nhau. |
| RMIT student cards | FixedSizeChunker (`fixed_size`, size=400, overlap=50) | 19 | 387.4 | Có overlap nhưng đôi khi cắt giữa danh sách công dụng. |
| RMIT student cards | SentenceChunker (`by_sentences`, 3 câu/chunk) | 12 | 533.6 | Danh sách không có dấu chấm làm chunk dài. |
| RMIT student cards | RecursiveChunker (`recursive`, size=400) | 19 | 337.8 | Phù hợp cấu trúc dòng và mục của trang dịch vụ. |

> Baseline dùng phần thân tài liệu do `load_documents()` đã bỏ YAML front matter; các số liệu trên không tính metadata.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nhữ Trọng Thành**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=400)` với separator mặc định `\n\n → \n → . → khoảng trắng → ký tự`.
- **Mô tả & lý do chọn cho chủ đề này:** Corpus là các trang quy định/dịch vụ có nhiều mục và danh sách theo dòng. Recursive chunking ưu tiên giữ các ranh giới tự nhiên này, đồng thời vẫn hạ xuống từ hoặc ký tự khi một mục vượt 400 ký tự.
- **Kết quả Checkpoint 5:** `bench.py` nạp 103 chunks và in top-3 cùng câu trả lời có nguồn cho đủ 5 query đã khóa.
- **Code snippet (nếu custom):**
```python
chunker = RecursiveChunker(chunk_size=400)
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nhữ Trọng Thành | RecursiveChunker (`chunk_size=400`) | 0/10 với MockEmbedder | Chunk có ranh giới dòng/đoạn khá mạch lạc; đủ `doc_id`, `chunk_index`, nguồn để truy vết failure. | MockEmbedder không biểu diễn ngữ nghĩa; không evidence marker nào xuất hiện trong top-3. Recursive không overlap nên mỗi đoạn bằng chứng chỉ có một cơ hội được xếp hạng. |
| | | | | |
| | | | | |

> Hai dòng còn lại chờ kết quả `bench.py` của các thành viên khác trên cùng corpus, 5 query và embedder; không suy diễn hoặc điền thay khi chưa có output thực tế.

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chưa thể kết luận strategy tốt nhất từ baseline mock và khi chưa có kết quả của các thành viên còn lại. MockEmbedder chỉ kiểm tra pipeline; nhóm cần chạy lại mọi strategy bằng cùng một multilingual semantic embedder rồi so sánh chunk-level trên đúng năm evidence marker đã khóa.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | **[Số liệu + filter]** Đối với sinh viên đại học và sau đại học, hạn mức mượn, thời hạn mượn, số lần và thời lượng gia hạn là bao nhiêu? Dùng filter `audience=all`. | 25 tài liệu trong 30 ngày; gia hạn 1 lần thêm 15 ngày, tối đa 45 ngày, nếu chưa quá hạn và không bị đặt giữ. | `rmit-library-borrowing-returning`, Recursive-400 chunks 3–4. |
| 2 | **[Điều kiện]** Sinh viên cần đáp ứng những điều kiện nào để được xin gia hạn thanh toán cho Standard Course? | Không ở học kỳ đầu; nợ cũ dưới 5 triệu đồng; chứng minh hoàn cảnh bất ngờ và khả năng trả đủ trong tối đa 45 ngày; đã tuân thủ các hạn gia hạn trước. | `rmit-defer-payment`, Recursive-400 chunks 7–8. |
| 3 | **[Quy trình]** Muốn hủy toàn bộ đăng ký chương trình, sinh viên phải nộp biểu mẫu nào và ở đâu? | Hoàn thành Program Cancellation form trong mục Submit Request của myRMIT. | `rmit-change-cancel-enrolment`, Recursive-400 chunk 10. |
| 4 | **[Liệt kê]** Thẻ sinh viên RMIT có thể được sử dụng cho những mục đích nào? | Mượn tài liệu; in/scan/photocopy; vào khu vực an ninh; xác minh tại kỳ đánh giá và điểm dịch vụ; nhận ưu đãi. | `rmit-student-cards`, Recursive-400 chunks 3–4. |
| 5 | **[Ngoại lệ]** Nếu hủy đăng ký sau Census Date nhưng không tham gia lớp học, sinh viên có còn phải trả học phí và các khoản phí khác không? | Có. Sinh viên vẫn phải chịu học phí và các khoản phí khác dù không tham gia lớp học. | `rmit-change-cancel-enrolment`, Recursive-400 chunk 9. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Hạn mức/thời gian mượn | Chưa kết luận; Recursive-400 hiện tại | Không | Có filter: top-3 đều đúng doc thư viện nhưng là chunks 13, 9, 8; evidence nằm ở chunks 3–4. |
| 2 | Điều kiện gia hạn thanh toán | Chưa kết luận; Recursive-400 hiện tại | Không | Top-3 là `fees-payments:2`, `fees-payments:7`, `student-cards:6`; thiếu cả hai evidence marker. |
| 3 | Quy trình hủy chương trình | Chưa kết luận; Recursive-400 hiện tại | Không | Top-1 đúng chủ đề đăng ký nhưng ở `rmit-enrolment:0`; không chứa Program Cancellation form. |
| 4 | Công dụng thẻ sinh viên | Chưa kết luận; Recursive-400 hiện tại | Không | Top-3 có đúng doc thẻ nhưng là chunk 4 (ưu đãi); bằng chứng chính ở chunk 3 nên không được tính liên quan. |
| 5 | Nghĩa vụ phí sau Census Date | Chưa kết luận; Recursive-400 hiện tại | Không | Top-1 là quy định hư hỏng sách; không có câu về nghĩa vụ học phí trong top-3. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có tác dụng ở Q1 về precision cấp tài liệu: có filter `audience=all`, ba kết quả đều thuộc `rmit-library-borrowing-returning`; không filter, top-3 bị lẫn `rmit-defer-payment` và `rmit-enrolment`. Tuy nhiên filter chưa cải thiện precision cấp chunk vì cả hai lượt đều không lấy được chunks 3–4 chứa số liệu, cho thấy metadata chỉ thu hẹp phạm vi chứ không thay thế semantic ranking.

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
