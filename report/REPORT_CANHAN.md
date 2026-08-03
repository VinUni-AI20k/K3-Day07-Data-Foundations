# Template Báo Cáo Cá Nhân — Lab 7

> Đây là template dùng chung. Không điền kết quả của thành viên khác. Mọi số liệu phải lấy từ `evaluation/benchmark_results.json` hoặc output terminal.

## 1. Thông tin sinh viên

- Họ tên: [CHỜ THÀNH VIÊN CUNG CẤP]
- Mã học viên: [CHỜ THÀNH VIÊN CUNG CẤP]
- Nhóm: B1-3

## 2. Vai trò

[CHỜ THÀNH VIÊN XÁC NHẬN]

## 3. Phần code đã hoàn thành

Mô tả phần cá nhân thực hiện; không đổi public API của `src`.

## 4. Python environment

- Python chuẩn nhóm: 3.11.15
- Interpreter: `.venv\Scripts\python.exe`
- Unit test chung: 42/42 pass (audit 2026-08-03)

## 5. Dataset

Corpus chung gồm 6 tài liệu UIT; ghi rõ tài liệu cá nhân phụ trách.

## 6. Metadata schema

Các trường chung: `doc_id`, `title`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version`, `chunk_index`.

## 7. Strategy cá nhân

[CHƯA XÁC NHẬN THAM SỐ]

## 8. Tham số

- Chunk size: [CHƯA XÁC NHẬN]
- Overlap/số câu/separators: [CHƯA XÁC NHẬN]
- top_k: 3

## 9. Local embedding backend

- Model chung: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Dimension: 384
- Fallback: false

## 10. Năm benchmark queries

Tham chiếu `evaluation/benchmark_queries.json`; không tạo query riêng làm mất tính so sánh.

## 11. Kết quả retrieval

[CHƯA ĐIỀN KẾT QUẢ CÁ NHÂN]

## 12. Metrics

| Hit@1 | Hit@3 | MRR | Precision@3 | Coherence | Grounding |
|---:|---:|---:|---:|---:|---:|
| [CHƯA ĐIỀN] | [CHƯA ĐIỀN] | [CHƯA ĐIỀN] | [CHƯA ĐIỀN] | [CHƯA ĐIỀN] | [CHƯA ĐIỀN] |

## 13. Failure cases

[CHƯA PHÂN TÍCH]

## 14. So sánh dự đoán và thực tế

[CHỜ THÀNH VIÊN CUNG CẤP]

## 15. Hạn chế

Nêu hạn chế corpus, chunking và metric của strategy cá nhân.

## 16. Hướng cải thiện

[CHỜ THÀNH VIÊN CUNG CẤP]

## 17. Bằng chứng test

Ghi command, Python version, tổng pass/fail và duration thực tế.

## 18. Bằng chứng benchmark

Trỏ tới strategy tương ứng trong `evaluation/benchmark_results.json` và bảng tóm tắt trong `evaluation/benchmark_summary.md`.
