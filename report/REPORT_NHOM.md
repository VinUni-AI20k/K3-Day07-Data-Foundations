# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

## 1. Thông tin nhóm

| Thành viên | Mã học viên | Vai trò | Strategy chính |
|---|---|---|---|
| Trương Đình Khoa | 2A202601297 | Nhóm trưởng | `S1_RECURSIVE_450` |
| Diêm Công Thành | 2A202601689 | Thành viên | `S2_FIXED_450_50` |
| Nguyễn Quang Huy | 2A202601873 | Thành viên | `S3_SENTENCE_3` |

Ngày audit và benchmark: 2026-08-03. Python: 3.11.15 trong `.venv`.

## 2. Dataset

Chủ đề K3 là dịch vụ và quy định sinh viên UIT. Corpus gồm 6 tài liệu UTF-8 công khai; `scripts/validate_dataset.py` xác nhận 6/6 tài liệu hợp lệ, `doc_id` duy nhất và `sources.csv` khớp một-một.

| ID | Chủ đề | Nguồn | Ngày truy cập | Phiên bản nguồn |
|---|---|---|---|---|
| `k3-course-registration` | Đăng ký học phần | https://student.uit.edu.vn/mot-so-quy-trinh-danh-cho-sinh-vien | 2026-08-03 | `not-stated` |
| `k3-library-services` | Thư viện | https://lib.uit.edu.vn/tin-hoat-dong/thong-bao-tai-khoan-thu-vien-danh-cho-tan-sinh-vien-uit-khoa-2024 | 2026-08-03 | `2024-activity-news` |
| `k3-tuition-extension` | Gia hạn học phí | https://ctsv.uit.edu.vn/bai-viet/thong-bao-gia-han-hoc-phi-hoc-ky-2-dot-2-lan-cuoi | 2026-08-03 | `2026-03-23` |
| `k3-bcu-scholarship-2026` | Học bổng | https://oep.uit.edu.vn/vi/node/24821 | 2026-08-03 | `2026-06-01` |
| `k3-dormitory-registration` | Ký túc xá | https://ctsv.uit.edu.vn/bai-viet/nhap-hoc-dang-ky-ky-tuc-xa-dhqg-hcm | 2026-08-03 | `2023-08-19` |
| `k3-health-insurance-2026` | Bảo hiểm y tế | https://ctsv.uit.edu.vn/bai-viet/thong-bao-mua-bao-hiem-y-te-nam-2026 | 2026-08-03 | `2025-12-09` |

Quy trình: lấy phần nội dung công khai cần thiết, loại menu/footer, lưu Markdown và YAML front matter. Metadata chung: `doc_id`, `title`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version`. Ingestion giữ thêm `source` và `chunk_index` trên từng chunk.

Hạn chế: corpus nhỏ, mỗi tài liệu chỉ có một heading cấp 1 và chỉ đại diện một trường đại học; benchmark không suy rộng ra toàn bộ dịch vụ đại học.

## 3. Benchmark queries

| ID | Query | Gold answer | Source | Pass criteria |
|---|---|---|---|---|
| Q1 | Sinh viên xác nhận đăng ký học phần ở hệ thống nào? | `dkhp.uit.edu.vn`, tài khoản chứng thực | `k3-course-registration` | Top-3 có cả hệ thống và cách đăng nhập |
| Q2 | Hạn hoàn thành học phí được gia hạn? | Trước 17/04/2026 | `k3-tuition-extension` | Top-3 nêu đúng ngày |
| Q3 | Mức học bổng BCU cho sinh viên đứng đầu? | 3.500.000 đồng | `k3-bcu-scholarship-2026` | Top-3 có đối tượng và mức tiền |
| Q4 | Hạn đăng ký KTX sau nhập học? | 07 ngày | `k3-dormitory-registration` | Lọc `audience=student`; Top-3 có mốc bắt đầu và thời hạn |
| Q5 | Sinh viên đóng BHYT 2026 bao nhiêu? | 631.800 đồng | `k3-health-insurance-2026` | Top-3 nêu trực tiếp phần sinh viên đóng |

Schema đầy đủ và expected evidence nằm trong `evaluation/benchmark_queries.json`.

## 4. Strategy từng thành viên

| Thành viên | Strategy | Chunk size | Overlap | Metadata | top_k |
|---|---|---:|---:|---|---:|
| Trương Đình Khoa | Recursive | 450 | 0 | Giữ toàn bộ; Q4 lọc audience | 3 |
| Diêm Công Thành | Fixed-size | 450 | 50 | Giữ toàn bộ; Q4 lọc audience | 3 |
| Nguyễn Quang Huy | Sentence | 3 câu | 0 | Giữ toàn bộ; Q4 lọc audience | 3 |
| Trương Đình Khoa (bổ sung K3) | Heading + Recursive | 450 | 0 | Giữ toàn bộ; Q4 lọc audience | 3 |

Thử nghiệm bổ sung tách tại Markdown heading rồi recursive khi section quá dài. Vì mỗi tài liệu hiện chỉ có một H1, kết quả giống recursive; đây là bằng chứng thực nghiệm về giới hạn corpus, không phải kết luận heading luôn không hữu ích.

Tất cả strategy dùng cùng model local `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, vector 384 chiều, không fallback.

## 5. Kết quả từng query

| Query | Strategy | Top-1 | Top-3 | Rank đúng | Nhận xét |
|---|---|---:|---:|---:|---|
| Q1 | Recursive | 1 | 1 | 1 | Evidence đầy đủ ở rank 1 |
| Q2 | Recursive | 1 | 1 | 1 | Evidence đầy đủ ở rank 1 |
| Q3 | Recursive | 0 | 1 | 3 | Top-1 cùng chủ đề nhưng thiếu đủ evidence |
| Q4 | Recursive | 1 | 1 | 1 | Filter audience không đổi rank |
| Q5 | Recursive | 0 | 1 | 2 | Rank 1 chưa có câu mức đóng đầy đủ |
| Q1 | Fixed | 1 | 1 | 1 | Evidence đầy đủ ở rank 1 |
| Q2 | Fixed | 0 | 1 | 2 | Overlap tạo chunk cạnh tranh ở rank 1 |
| Q3 | Fixed | 1 | 1 | 1 | Mức tiền và đối tượng cùng chunk |
| Q4 | Fixed | 1 | 1 | 1 | Evidence đầy đủ ở rank 1 |
| Q5 | Fixed | 0 | 1 | 2 | Evidence đầy đủ ở rank 2 |
| Q1 | Sentence | 1 | 1 | 1 | Evidence đầy đủ ở rank 1 |
| Q2 | Sentence | 0 | 1 | 3 | Câu hạn thanh toán ở rank 3 |
| Q3 | Sentence | 1 | 1 | 1 | Câu đầy đủ, dễ đọc |
| Q4 | Sentence | 1 | 1 | 1 | Evidence đầy đủ ở rank 1 |
| Q5 | Sentence | 0 | 1 | 2 | Evidence đầy đủ ở rank 2 |

Heading+Recursive có cùng rank với Recursive cho cả 5 query. Score và toàn bộ evidence text nằm trong `evaluation/benchmark_results.json`.

## 6. So sánh tổng hợp

| Strategy | Hit@1 | Hit@3 | MRR | Precision@3 | Coherence (0–2) | Grounding (0–2) |
|---|---:|---:|---:|---:|---:|---:|
| Recursive 450 | 0.6000 | 1.0000 | 0.7667 | 0.3333 | 2.0000 | 1.6000 |
| Fixed 450/50 | 0.6000 | 1.0000 | **0.8000** | 0.3333 | 1.0000 | 1.6000 |
| Sentence 3 | 0.6000 | 1.0000 | 0.7667 | 0.3333 | **2.0000** | 1.6000 |
| Heading + Recursive 450 | 0.6000 | 1.0000 | 0.7667 | 0.3333 | **2.0000** | 1.6000 |

Precision@3 là số chunk có đủ expected evidence chia cho 3; mỗi query chỉ cần một chunk evidence nên giá trị 0.3333 là kỳ vọng khi Top-3 chứa đúng một chunk hoàn chỉnh. Q4 được chạy cả có và không filter; `audience=student` không cải thiện rank trong corpus nhỏ này, nên Metadata Utility là trung tính chứ không bị phóng đại.

## 7. Failure cases

Không có lỗi Hit@3. Các lỗi Top-1:

| Query | Strategy | Expected | Actual | Root cause | Cải thiện |
|---|---|---|---|---|---|
| Q3 | Recursive/Heading | Chunk có “đứng đầu” + 3.500.000 | Đúng ở rank 3 | Query gần các chunk học bổng khác cùng tài liệu | Tăng trọng số heading hoặc hybrid keyword |
| Q5 | Tất cả | Câu “sinh viên đóng 631.800” | Đúng ở rank 2 | Chunk khác cùng tài liệu có ngữ nghĩa BHYT rộng hơn | Rerank theo số tiền/evidence term |
| Q2 | Fixed | Câu hạn 17/04/2026 | Đúng ở rank 2 | Overlap tạo chunk gần nhau | Giảm overlap hoặc rerank |
| Q2 | Sentence | Câu hạn 17/04/2026 | Đúng ở rank 3 | Nhóm 3 câu làm loãng ý về hạn | Thử 1–2 câu/chunk |

Không quy lỗi cho model khi corpus/chunking giải thích được các miss.

## 8. Kết luận

- Hit@3 tốt nhất: cả bốn cấu hình đều 1.0000.
- MRR tốt nhất và cấu hình chi phí/triển khai đơn giản nhất trong benchmark này: Fixed 450/50 (0.8000).
- Chunk dễ đọc nhất: Recursive, Sentence và Heading+Recursive (coherence 2.0000).
- Đề xuất nhóm: dùng Recursive 450 cho câu trả lời cần evidence dễ đọc; dùng Fixed 450/50 làm baseline/rerieval đơn giản. Không có một strategy thắng mọi tiêu chí.
- Hướng phát triển: mở rộng corpus nhiều section, thử hybrid lexical+dense reranking và đánh giá filter trên tài liệu có cùng category nhưng khác audience.

## 9. Bằng chứng chạy

- `.venv\Scripts\python.exe -m pytest tests/ -v`: 42 passed trong 0.08s.
- `.venv\Scripts\python.exe scripts\validate_dataset.py`: 6/6 hợp lệ.
- `.venv\Scripts\python.exe scripts\run_semantic_benchmark.py`: local model, 5 query, 4 cấu hình, exit 0.
- `.venv\Scripts\python.exe main.py`: exit 0, nạp 13 chunk cấu hình mặc định.
