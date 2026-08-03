# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [CHỜ NHÓM CUNG CẤP]

**Thành viên:** [CHỜ NHÓM CUNG CẤP]

**Ngày cập nhật kỹ thuật:** 2026-08-03

## 1. Chủ đề và trạng thái dữ liệu

**Chủ đề K3:** dịch vụ và quy định đại học.

**Trạng thái:** corpus chưa đạt điều kiện benchmark.

Repository hiện có đúng hai file trong `data/k3_university/`:

| File | Phạm vi | Trạng thái nguồn |
|---|---|---|
| `course-registration.md` | Đăng ký học phần | Template, URL `example.edu`, cần thay bằng nguồn thật |
| `library-services.md` | Dịch vụ thư viện | Template, URL `example.edu`, cần thay bằng nguồn thật |

Hai dòng trong `sources.csv` đều ghi `example-template-replace-me`. Vì vậy không coi đây là dữ liệu crawl thực tế và không dùng làm gold evidence.

## 2. Dữ liệu còn thiếu và nguồn cần thu thập

Cần bổ sung tối thiểu 3 tài liệu (khuyến nghị 5–8 tài liệu) từ trang chính thức/công khai của trường:

1. Quy định đăng ký, hủy và điều chỉnh học phần.
2. Biểu phí, thời hạn và phương thức đóng học phí.
3. Điều kiện, hồ sơ và lịch xét học bổng.
4. Quy định mượn, gia hạn và xử lý quá hạn thư viện.
5. Điều kiện đăng ký, phí và nội quy ký túc xá.
6. FAQ hoặc kênh hỗ trợ sinh viên chính thức.

Không tự động crawl hay khẳng định đã thu thập các nguồn trên.

## 3. Cách thu thập, format và metadata schema

Mỗi nguồn công khai được làm sạch thành một file UTF-8 `.md`/`.txt`; menu, footer và dữ liệu nhạy cảm bị loại bỏ. `sources.csv` phải khớp một-một với các file. Mỗi tài liệu dùng YAML front matter:

| Trường | Kiểu | Mục đích |
|---|---|---|
| `doc_id` | string | ID ổn định, duy nhất |
| `title` | string | Tên tài liệu/nguồn |
| `source_url` | string | Truy vết trang gốc |
| `retrieved_at` | date | Ngày lấy dữ liệu |
| `document_version` | string/date | Phiên bản hoặc ngày hiệu lực |
| `audience` | enum | Lọc student/faculty/staff/all |
| `department` | string | Lọc đơn vị phụ trách |
| `category` | string | Lọc nhóm chính sách/dịch vụ |
| `language` | string | Quản lý ngôn ngữ corpus |

Ingestion đã được xác minh theo luồng: front matter → `Document` → chunk → gắn `doc_id`, `chunk_index`, source metadata → embedding → store.

## 4. Template năm benchmark query

> Các câu dưới đây là **template chờ corpus thật**, chưa phải benchmark đã chạy. Không có gold answer vì repository chưa có nguồn thật hỗ trợ.

| ID | Câu hỏi dự kiến | Gold answer | Tài liệu nguồn cần có | Chunk kỳ vọng | Tiêu chí pass |
|---|---|---|---|---|---|
| Q1 | Sinh viên được đăng ký hoặc điều chỉnh học phần trong thời gian nào? | [CHỜ NGUỒN THẬT] | Quy định đăng ký học phần | Mục lịch/thời hạn | Top-3 chứa đúng điều khoản và câu trả lời trích được bằng chứng |
| Q2 | Điều kiện và thời hạn đóng học phí là gì? | [CHỜ NGUỒN THẬT] | Thông báo/quy định học phí | Mục điều kiện + hạn nộp | Top-3 có đúng mục, không suy đoán số tiền/thời hạn |
| Q3 | Sinh viên cần đáp ứng điều kiện nào để xét học bổng? | [CHỜ NGUỒN THẬT] | Quy định học bổng | Mục đối tượng + điều kiện | Top-3 chứa đủ điều kiện bắt buộc |
| Q4 | Sinh viên có thể gia hạn tài liệu thư viện như thế nào? | [CHỜ NGUỒN THẬT] | Quy định mượn/gia hạn | Mục gia hạn | Top-3 có quy trình và ngoại lệ nếu nguồn nêu |
| Q5 | Quy định đăng ký ký túc xá dành cho sinh viên là gì? | [CHỜ NGUỒN THẬT] | Nội quy/hướng dẫn KTX | Mục đăng ký cho student | Dùng `metadata_filter={"audience": "student"}` và top-3 có đúng đối tượng |

## 5. Ba cấu hình cần so sánh

| Cấu hình | Chunker | Tham số cần cố định | Metadata |
|---|---|---|---|
| A | `FixedSizeChunker` | `chunk_size`, `overlap` | Toàn bộ front matter + `doc_id`, `chunk_index` |
| B | `SentenceChunker` | `max_sentences_per_chunk`, quy tắc ghép câu | Như A |
| C | `RecursiveChunker` | `chunk_size`, danh sách separator | Như A |

Chiến lược của từng thành viên: [CHỜ NHÓM CUNG CẤP]

## 6. Bảng kết quả so sánh

| Query | Strategy | Top-1 đúng? | Top-3 có chunk đúng? | Score | Nguồn | Nhận xét |
|---|---|---:|---:|---:|---|---|
| [CHƯA CHẠY] | [CHƯA CHẠY] | — | — | — | — | [CHƯA CÓ KẾT QUẢ THỰC NGHIỆM] |

**Embedding backend yêu cầu khi benchmark:** local multilingual embedder.

**Backend đã chạy hiện tại:** mock embeddings fallback, chỉ dùng kiểm tra pipeline.

**Chiến lược tốt nhất:** [CHƯA CÓ KẾT QUẢ THỰC NGHIỆM]

Chưa phân tích Retrieval Precision, Chunk Coherence, Metadata Utility, Grounding Quality hay Data Strategy Impact vì chưa có benchmark hợp lệ. Không kết luận từ score mock.

## 7. Demo flow dự kiến

```text
Chọn corpus thật và query
→ parse front matter
→ chọn cấu hình chunking
→ ingest vào EmbeddingStore bằng local embedder
→ search/search_with_filter top-3
→ hiển thị score + nguồn + chunk
→ KnowledgeBaseAgent tạo câu trả lời grounded
→ đối chiếu gold evidence
```

## 8. Hạn chế và đề xuất cải tiến

- Thiếu ít nhất ba tài liệu thật và toàn bộ gold evidence.
- Chưa xác minh trên Python 3.11; máy audit chỉ có Python 3.13.14.
- Chưa cài/chạy local multilingual model nên chưa thể so sánh semantic retrieval.
- Cần kiểm tra URL, quyền sử dụng, ngày truy xuất và version trước benchmark.
- Sau khi có dữ liệu, chạy đúng năm query trên cả ba cấu hình, ghi toàn bộ top-1/top-3 thay vì chỉ ví dụ thuận lợi.

## 9. Phân công

| Công việc | Người phụ trách | Trạng thái |
|---|---|---|
| Xác minh và thu thập nguồn | [CHỜ NHÓM CUNG CẤP] | Chưa thực hiện |
| Chuẩn hóa metadata/corpus | [CHỜ NHÓM CUNG CẤP] | Chưa thực hiện |
| Thống nhất gold answers | [CHỜ NHÓM CUNG CẤP] | Chưa thực hiện |
| Chạy cấu hình A/B/C | [CHỜ NHÓM CUNG CẤP] | Chưa thực hiện |
| Tổng hợp demo và failure analysis | [CHỜ NHÓM CUNG CẤP] | Chưa thực hiện |
