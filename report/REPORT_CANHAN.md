# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Dương Ngọc Tiến
**Nhóm:** K3-Thư viện
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Hai văn bản có hướng của vector nhúng gần như trùng nhau, đồng nghĩa với việc chúng có ý nghĩa, chủ đề và ngữ cảnh rất giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Thời tiết hôm nay có mưa lớn"
- Câu B: "Hôm nay trời mưa to"
- Tại sao tương đồng: Cả hai câu đều nói về hiện tượng thời tiết mưa nhiều trong ngày hôm nay.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thời tiết hôm nay có mưa lớn"
- Câu B: "Trái táo này rất ngon"
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác biệt (thời tiết vs ẩm thực).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Vì khoảng cách Euclid bị ảnh hưởng bởi độ dài của văn bản (magnitude của vector). Độ tương tự cosine chỉ xét góc giữa hai vector nên phù hợp để so sánh ngữ nghĩa dù văn bản dài hay ngắn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `ceil((10000 - 50) / (500 - 50))` = `ceil(9950 / 450)` = `ceil(22.11)` = 23
> *Đáp án:* 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Số lượng chunk sẽ tăng lên thành 25 (`ceil(9900/400)`). Việc tăng chồng chéo giúp bảo toàn ngữ cảnh ở ranh giới giữa các chunk, tránh việc một câu hay một đoạn văn bị đứt gãy ý nghĩa.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
> Sử dụng regex `(\. |\! |\? |\.\n)` để tách văn bản thành các câu riêng biệt, đồng thời bảo toàn dấu câu đó. Ngoại lệ như câu kết thúc không có dấu câu được xử lý bằng cách kiểm tra và append phần dư thừa vào mảng câu cuối cùng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
> Thuật toán tách dần theo thứ tự ưu tiên của dấu phân cách. Base case là khi đoạn văn bản nhỏ hơn `chunk_size` hoặc khi không còn dấu phân cách nào (lúc này sẽ ép buộc tách bằng `FixedSizeChunker`).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
> `add_documents` lưu các dict chứa chunk content, metadata và tính embedding. `search` sẽ gọi `compute_similarity` tính Cosine Similarity giữa query vector và toàn bộ vector trong kho, rồi sắp xếp giảm dần kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
> Việc lọc được thực hiện **trước** quá trình tính độ tương tự, bằng cách lặp và so khớp các metadata filter. `delete_document` thực hiện xóa bằng cách tạo lại bộ nhớ tạm, loại bỏ các dict có `id` trùng khớp doc_id cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
> Gọi hàm `search` lấy top K kết quả, sau đó nối (join) các đoạn nội dung thành 1 khối text. Cuối cùng nhúng vào prompt theo format: `Context: {context}\n\nQuestion: {question}\n\nAnswer:` rồi đưa vào hàm LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]
============================= 42 passed in 0.18s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Thời tiết hôm nay có mưa lớn" | "Hôm nay trời mưa to" | cao | 0.85 | Có |
| 2 | "Trường đại học Bách Khoa" | "Trường đại học Xây Dựng" | thấp | 0.25 | Có |
| 3 | "Tôi thích học Toán" | "Môn Toán là môn tôi yêu thích" | cao | 0.92 | Có |
| 4 | "Tôi thích học Toán" | "Môn Văn rất thú vị" | thấp | 0.31 | Có |
| 5 | "Quy định thư viện" | "Luật mượn sách" | cao | 0.78 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Bất ngờ nhất là cặp số 5, tuy hai câu dùng từ vựng hoàn toàn khác nhau ("quy định", "thư viện" khác với "luật", "mượn sách") nhưng điểm tương đồng vẫn cao. Điều này minh chứng embeddings biểu diễn ý nghĩa ở cấp độ khái niệm (concept) thay vì chỉ so khớp mặt chữ (keyword).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thư viện mở cửa lúc mấy giờ vào cuối tuần? | Phòng tự học 301, 303, 401, 418 mở cửa từ 8h00-19h00 (cả T7, CN). | 0.734 | Có | Vào cuối tuần (Thứ 7, Chủ nhật), phòng tự học mở cửa từ 8h00 đến 19h00. |
| 2 | Để làm thẻ thư viện cần mang theo giấy tờ gì? | Xuất trình thẻ hợp lệ (thẻ cán bộ, thẻ sinh viên, thẻ học viên...) khi vào thư viện. | 0.703 | Có | Để làm thẻ thư viện HUST, bạn đọc cần mang theo thẻ sinh viên hợp lệ hoặc thẻ cán bộ. |
| 3 | Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng mấy? | Tài liệu trong các phòng đọc chuyên ngành tại Thư viện Tạ Quang Bửu... | 0.530 | Có | Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng 4 (P.402 hoặc P.411). |
| 4 | Hệ thống phân loại sách nào được sử dụng trong thư viện? | Tài liệu trong các phòng đọc chuyên ngành tại Thư viện Tạ Quang Bửu xếp theo DDC và Cutter. | 0.630 | Có | Thư viện sử dụng Khung phân loại DDC (Dewey Decimal Classification) và xếp giá theo Cutter. |
| 5 | Có được phép mượn giáo trình Cơ lý thuyết về nhà không? | Chính sách mượn giáo trình tại phòng 111... | 0.427 | Có | Giáo trình được mượn về nhà theo chính sách tại phòng 111, còn tài liệu phòng đọc chuyên ngành chỉ được đọc tại chỗ. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Tôi học được cách sử dụng RecursiveChunker linh hoạt. Việc điều chỉnh các separators từ đoạn văn (newline) đến cấp câu và từ vựng giúp chia cắt ngữ cảnh tốt hơn nhiều so với FixedSizeChunker, nhất là khi xử lý các file Markdown.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
