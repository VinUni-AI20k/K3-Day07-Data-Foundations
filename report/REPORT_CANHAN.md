# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [CHỜ SINH VIÊN CUNG CẤP]

**Nhóm:** [CHỜ NHÓM CUNG CẤP]

**Ngày cập nhật kỹ thuật:** 2026-08-03

> Báo cáo này chỉ ghi kết quả đã được xác minh trong repository. Corpus K3 hiện chỉ là dữ liệu khởi động nên chưa đủ điều kiện chấm retrieval thực tế.

## 1. Mục tiêu cá nhân và phần khởi động

Mục tiêu là hoàn thiện ba module `chunking.py`, `store.py`, `agent.py`, giữ nguyên public API, bảo toàn metadata và xây dựng luồng RAG deterministic cho unit test.

Cosine similarity cao nghĩa là hai vector có hướng gần nhau; giá trị gần 0 thể hiện ít liên hệ theo không gian embedding, còn gần -1 là ngược hướng. Ví dụ khái niệm có độ tương tự cao: “Sinh viên đăng ký học phần trên cổng học vụ” và “Cổng học vụ cho phép sinh viên chọn lớp học phần”. Cặp thấp: “Quy định mượn sách thư viện” và “Cách huấn luyện mô hình thị giác máy tính”. Cosine thường phù hợp với text embedding vì tập trung vào hướng của vector thay vì độ lớn.

Với tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:

```text
ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks
```

Nếu overlap tăng lên 100 thì kết quả là `ceil(9900 / 400) = 25 chunks`. Overlap lớn hơn giữ thêm ngữ cảnh qua ranh giới nhưng tăng số chunk, dung lượng và chi phí retrieval.

## 2. Các TODO đã hoàn thành

- `SentenceChunker.chunk`
- `RecursiveChunker.chunk` và `_split`
- `compute_similarity`
- `ChunkingStrategyComparator.compare`
- Toàn bộ phương thức của `EmbeddingStore`
- `KnowledgeBaseAgent.__init__` và `answer`
- Sửa lỗi stdout UTF-8 tại hai entrypoint Windows để `python ingest.py` và `python main.py` chạy được

## 3. Mô tả triển khai

### SentenceChunker

Văn bản được chuẩn hóa whitespace rồi nhận diện câu bằng regex giữ lại `.`, `!`, `?`, `…` và dấu nháy/ngoặc đóng sau dấu câu. Các câu được ghép tuần tự theo `max_sentences_per_chunk`; văn bản rỗng hoặc chỉ có whitespace trả về danh sách rỗng.

### RecursiveChunker

Thuật toán thử separator đúng thứ tự cấu hình. Đoạn còn quá dài mới được chuyển xuống separator mịn hơn; separator được gắn lại vào piece để không mất nội dung. Khi hết separator hoặc gặp `""`, thuật toán cắt cứng theo `chunk_size`, bảo đảm dừng và không sinh chunk rỗng.

### Cosine similarity

Hai vector phải cùng chiều và không rỗng. Hàm dùng `math.fsum` cho dot product và norm; vector zero trả `0.0`, còn sai chiều/rỗng raise `ValueError` rõ ràng.

### ChunkingStrategyComparator

Comparator chạy `FixedSizeChunker`, `SentenceChunker`, `RecursiveChunker` và trả đúng schema: `count`, `avg_length`, `min_length`, `max_length`, `chunks`.

### EmbeddingStore

Mỗi record có ID tài liệu, storage ID duy nhất, bản sao metadata, embedding và thứ tự chèn. Search dùng đúng embedder của store, cosine similarity, sắp xếp score giảm dần và dùng thứ tự chèn để phá hòa deterministic. Filter kiểm tra đủ mọi cặp key-value trước search. Delete khớp chính xác `metadata.doc_id`; metadata đầu vào không bị sửa.

### KnowledgeBaseAgent

Agent retrieve đúng `top_k`, đưa content và nguồn/doc ID vào vùng `<retrieved_context>`, coi nội dung tài liệu là dữ liệu không tin cậy để giảm prompt injection, và yêu cầu LLM chỉ trả lời từ context. Store rỗng trả thông báo thiếu thông tin mà không gọi LLM.

## 4. Quyết định kỹ thuật và trường hợp biên

- Giữ in-memory store làm nguồn kết quả deterministic; ChromaDB chỉ là mirror tùy chọn khi package khả dụng.
- Cho phép nội dung giống nhau với ID khác nhau; storage ID nội bộ tránh xung đột.
- `top_k <= 0`, câu hỏi rỗng, chunk size không hợp lệ và overlap không hợp lệ đều raise `ValueError`.
- Đã kiểm tra: empty/whitespace text, một câu không dấu kết, dấu câu tiếng Việt cạnh dấu nháy, câu/đoạn dài, nhiều đoạn, fallback cắt cứng, metadata preservation, vector zero/rỗng/sai chiều, store rỗng, filter không khớp, xóa thiếu ID và duplicate text.

## 5. Cấu hình retrieval cá nhân và dự đoán trước benchmark

Cấu hình demo hiện tại dùng `FixedSizeChunker(chunk_size=500, overlap=50)`, metadata từ YAML front matter và mock embedder 64 chiều. Dự đoán cần kiểm chứng sau khi có corpus thật: sentence/recursive chunking có thể tạo chunk dễ đọc hơn fixed-size trên tài liệu quy định có cấu trúc; metadata `audience`, `department`, `category` có thể tăng precision khi query xác định đối tượng.

Không dùng dự đoán này làm kết luận benchmark.

## 6. Bằng chứng kiểm thử

```text
Python thực tế: 3.13.14 (máy chưa cài Python 3.11)
Dependencies: pytest 9.1.1, python-dotenv 1.2.2
Baseline: 11 passed, 31 failed
Sau triển khai: 42 passed, 0 failed, 0 skipped (0.06s)
Ingestion self-check: parse 4 khóa metadata, tạo 18 chunk
Main demo: nạp 2 tài liệu template thành 3 chunk; exit code 0
Supplemental edge checks: OK
```

Lệnh đã chạy:

```powershell
python -m pytest tests/ -v
python ingest.py
python main.py
```

## 7. Benchmark retrieval thực tế

**Embedding backend thực tế:** mock embeddings fallback

**Corpus:** 2 tài liệu khởi động, đều tự ghi là template và dùng URL `example.edu`

**Số benchmark query hợp lệ:** 0

**Kết quả:** [CHƯA CÓ KẾT QUẢ THỰC NGHIỆM]

Không ghi gold answer, điểm retrieval, success/failure case hoặc chiến lược tốt nhất vì chưa có 5–10 tài liệu nguồn thật và chưa chạy local multilingual embedder. Kết quả score của mock trong `main.py` chỉ xác minh pipeline, không phản ánh semantic retrieval.

## 8. Hạn chế và hướng cải thiện

1. Cài Python 3.11 và chạy lại toàn bộ test để xác minh đúng runtime chuẩn của lab.
2. Thu thập 5–10 nguồn đại học công khai, thay URL/template và kiểm tra metadata một-một với `sources.csv`.
3. Cài `requirements-local.txt`, chạy cùng năm query trên ba cấu hình chunking, lưu top-1/top-3 và gold evidence.
4. Bổ sung ngưỡng relevance hoặc cơ chế đánh giá context nếu thiết kế agent được mở rộng ngoài API hiện tại.

## 9. Phần cần sinh viên/nhóm hoàn thiện

- Thông tin sinh viên và nhóm: [CHỜ NHÓM CUNG CẤP]
- Năm cặp similarity prediction bằng local embedder: [CHƯA CÓ KẾT QUẢ THỰC NGHIỆM]
- Năm benchmark query/gold answer thống nhất: [CHỜ NHÓM CUNG CẤP]
- Phân tích retrieval thành công/thất bại và so sánh dự đoán: [CHƯA CÓ KẾT QUẢ THỰC NGHIỆM]
- Tự đánh giá điểm: [CHỜ SINH VIÊN CUNG CẤP]
