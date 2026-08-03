# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Minh Thu (01631)
**Nhóm:** Chưa xác định
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai embedding gần như cùng hướng, nên hai đoạn văn có nội dung hoặc ngữ cảnh tương tự theo mô hình embedding. Điểm càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên đăng ký học phần trên cổng thông tin.
- Câu B: Người học thực hiện đăng ký môn học trực tuyến.
- Tại sao tương đồng: Cả hai đều diễn đạt cùng một hành động đăng ký môn học qua hệ thống trực tuyến.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Thư viện cho phép gia hạn sách.
- Câu B: Ký túc xá có quy định giờ đóng cổng.
- Tại sao khác: Hai câu nói về hai dịch vụ đại học khác nhau, không cùng mục đích hay đối tượng thông tin.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine so sánh hướng của vector nên ít bị ảnh hưởng bởi độ lớn vector, vốn có thể thay đổi theo độ dài câu hoặc cách mô hình tạo embedding. Vì vậy nó phù hợp hơn để đánh giá mức gần nhau về ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11).
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng thành ceil((10.000 - 100) / (500 - 100)) = 25. Overlap lớn hơn giữ lại ngữ cảnh ở ranh giới các chunk, nhưng làm tăng số vector, chi phí lưu trữ và truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex tách sau dấu kết thúc câu (`.`, `!`, `?`) và khoảng trắng, sau đó loại phần rỗng và ghép tối đa `max_sentences_per_chunk` câu. Hàm trả về danh sách rỗng với văn bản rỗng, đồng thời ép số câu tối thiểu mỗi chunk là 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Chunker thử các dấu phân cách theo thứ tự ưu tiên: đoạn, dòng, câu, từ và cuối cùng là ký tự. Khi một phần còn dài, `_split` gọi lại với dấu phân cách ưu tiên thấp hơn; văn bản rỗng là base case và fallback ký tự giúp luôn trả về kết quả.

**`HeadingChunker.chunk` (custom)** — hướng tiếp cận:
> Chiến lược tùy chỉnh tách tại tiêu đề Markdown (`#` đến `######`) và giữ tiêu đề ở đầu mỗi chunk. Khi một mục dài hơn 450 ký tự, nội dung được chia theo từ nhưng lặp lại tiêu đề; vì vậy đoạn trả về vẫn nêu rõ quy định đang thuộc mục nào, như “Giờ mở cửa” hoặc “Điều chỉnh đăng ký”.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được embedding rồi lưu cùng `id`, `content` và metadata; lớp ưu tiên ChromaDB nếu có, nếu không dùng danh sách in-memory. Khi tìm kiếm, query cũng được embedding, điểm dot product với các vector đã chuẩn hoá được sắp giảm dần và chỉ lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc metadata trước rồi mới xếp hạng theo similarity để tránh kết quả sai đối tượng. Mỗi record có `metadata['doc_id']`; `delete_document` loại toàn bộ record có `doc_id` trùng và cho biết có xoá được bản ghi nào hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy các chunk top-k từ store, ghép nội dung chúng thành phần Context, rồi đặt câu hỏi sau Context trong prompt. Prompt yêu cầu LLM trả lời dựa trên thông tin đã truy xuất để giảm nguy cơ trả lời không có căn cứ.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$env:LAB_SOLUTION_PACKAGE="src.src_NguyenMinhThu_01631"
python -m pytest tests/ -v
======================== 42 passed in 0.19s ========================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

**Exercise 3.3: 5 cặp câu đánh giá (với mock embeddings)**

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Hướng dẫn đăng ký học phần trực tuyến. | Sinh viên đăng ký môn học trên cổng thông tin. | cao | -0.1704 | Không |
| 2 | Thư viện cho phép gia hạn sách. | Người học có thể gia hạn tài liệu mượn. | cao | -0.0589 | Không |
| 3 | Học phí được nộp theo học kỳ. | Ký túc xá có quy định giờ đóng cổng. | thấp | 0.0945 | Không |
| 4 | Vector store tìm kiếm theo embedding. | Cơ sở dữ liệu vector hỗ trợ tìm kiếm tương tự. | cao | 0.1010 | Không |
| 5 | Mưa lớn vào buổi chiều. | Thuật toán chunking chia văn bản thành các đoạn. | thấp | -0.0427 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Tất cả 5 dự đoán đều SAI! Các cặp có ý nghĩa gần nhau (1, 2, 4) được dự đoán cao nhưng thực tế lại âm hoặc rất thấp. Mock embedder sinh vector **xác định nhưng không có ý nghĩa** theo chuỗi ký tự, không hiểu ngữ cảnh/ngữ nghĩa. Kết quả này chứng minh mock chỉ dùng để kiểm tra tính đúng đắn của code, không thể dùng để đánh giá chất lượng retrieval.

---

## 5. Kết quả truy xuất của tôi (My Retrieval Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** với chiến lược của tôi (RecursiveChunker). **Lưu ý:** kết quả với mock embeddings không phản ánh chất lượng thực tế.

**Cấu hình chạy:** 
- Chunker: `RecursiveChunker(chunk_size=500)` → 83 chunks
- Embedder: Mock (deterministic nhưng không có ý nghĩa semantic)
- Q3 dùng `metadata_filter={“audience”: “student”}` theo yêu cầu K3

| # | Câu hỏi (Query) | Top-1 Chunk | Score | Liên quan? | Ghi chú |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mỗi học kỳ đăng ký tối thiểu/tối đa bao nhiêu tín chỉ? | course-registration::chunk_0 | 0.2683 | Không | Gold answer nằm ở phần 1.5.3, không match |
| 2 | Nếu sinh viên còn nợ học phí thì kỳ tiếp theo? | scholarship-policy::chunk_7 | 0.1580 | Không | Tuition payment info không ở top-1 |
| 3 | Học bổng KKHT Loại A bao nhiêu %? | tuition-payment::chunk_1 | 0.3085 | Không | Scholarship info không được match (despite filter) |
| 4 | Phòng ký túc xá 8 sinh viên bao nhiêu? | dormitory-policy::chunk_1 | 0.1347 | ✓ Có (Q4 duy nhất trả về đúng thông tin) | **Score: 2/10 — Chỉ Q4 thành công** |
| 5 | Khu tự học tầng 6 mở cửa khi nào? | scholarship-policy::chunk_0 | 0.1461 | Không | Library hours info không được match |

**Tóm tắt:** 1/5 câu hỏi (Q4) trả về thông tin đúng ở top-1. Kết quả xấu này do mock embeddings không hiểu ngữ cảnh. Cần chạy lại với local/OpenAI embedder để đánh giá công bằng.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 0 / 5 (toàn sai với mock) |
| Kết quả truy xuất của tôi (Retrieval Results — Phase 2) | 2 / 10 (1/5 câu đúng) |
| **Tổng phần cá nhân** | **47 / 60** |

**Ghi chú:** Điểm thấp ở Phần 4-5 do sử dụng mock embeddings. Cần chạy lại với local/OpenAI embedder để có đánh giá thực tế. Mock embeddings chỉ phù hợp kiểm thử code, không đánh giá chất lượng retrieval.
