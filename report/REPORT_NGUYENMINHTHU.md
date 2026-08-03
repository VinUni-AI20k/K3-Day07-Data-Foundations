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

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Hướng dẫn đăng ký học phần trực tuyến. | Sinh viên đăng ký môn học trên cổng thông tin. | cao | -0,0881 | Không |
| 2 | Thư viện cho phép gia hạn sách. | Người học có thể gia hạn tài liệu mượn. | cao | -0,2508 | Không |
| 3 | Học phí được nộp theo học kỳ. | Ký túc xá có quy định giờ đóng cổng. | thấp | 0,0707 | Có |
| 4 | Vector store tìm kiếm theo embedding. | Cơ sở dữ liệu vector hỗ trợ tìm kiếm tương tự. | cao | 0,0546 | Không |
| 5 | Mưa lớn vào buổi chiều. | Thuật toán chunking chia văn bản thành các đoạn. | thấp | -0,0177 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Hai cặp có ý nghĩa gần nhau (1, 2 và 4) lại cho điểm thấp vì bài kiểm thử dùng `MockEmbedder` xác định theo chuỗi ký tự, không phải embedding ngữ nghĩa thực. Điều này xác nhận mock chỉ phù hợp để kiểm tra tính đúng đắn của code; đánh giá retrieval thực tế cần local multilingual embedder hoặc OpenAI embedder.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

**Cấu hình chạy:** `HeadingChunker(chunk_size=450)` tạo 37 chunks. `EmbeddingStore` chạy với embedding TF-IDF cục bộ để đánh giá có thể tái lập; `sentence-transformers` chưa có trong môi trường nên chưa dùng được local multilingual embedder. Q3 dùng `metadata_filter={"audience": "student"}` theo yêu cầu K3.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mỗi học kỳ được đăng ký tối thiểu/tối đa bao nhiêu tín chỉ? | Top-3 chưa có mục 1.5.3. | 0,1787 | Không | Không tạo câu trả lời; cần cải thiện embedding. |
| 2 | Còn nợ học phí kỳ trước thì sao khi đăng ký kỳ tiếp theo? | Top-3 chưa có mục “Những lưu ý quan trọng”. | 0,1318 | Không | Không tạo câu trả lời; cần cải thiện embedding. |
| 3 | Học bổng KKHT Loại A bằng bao nhiêu phần trăm? | Top-3 chưa có mục 2.3.1.2, dù đã lọc `audience=student`. | 0,1953 | Không | Không tạo câu trả lời; cần multilingual embedder. |
| 4 | Phòng ký túc xá 8 sinh viên có giá bao nhiêu? | Mục “Mức phí hàng tháng”: 350.000 VNĐ/sinh viên/tháng. | 0,1926 | Có, top-1 | 350.000 VNĐ/sinh viên/tháng. |
| 5 | Khu tự học tầng 6 mở cửa khi nào? | Mục “Giờ mở cửa”: Thứ 2-Chủ nhật, 6h30-22h. | 0,3855 | Có, top-1 | Thứ 2 đến Chủ nhật, 6h30-22h. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 2 / 5. Q4 và Q5 ở top-1; Q1-Q3 thất bại vì TF-IDF không hiểu tốt các diễn đạt tương đương trong tiếng Việt.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> So với baseline `FixedSizeChunker(350, overlap=50)`, HeadingChunker tạo nhiều chunks hơn (37 so với 29) nhưng giữ nguyên tiêu đề mục với quy định; điều này giúp Q4 và Q5 trả về đúng mục ở top-1. Kết quả Q1-Q3 cho thấy chất lượng embedding quan trọng hơn chiến lược chunking: TF-IDF không thay thế được embedding ngữ nghĩa tiếng Việt. Nhóm cần chạy cùng 5 câu hỏi với local multilingual embedder để so sánh công bằng giữa các thành viên.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 4 / 10 |
| **Tổng phần cá nhân** | **54 / 60 (tạm thời)** |
