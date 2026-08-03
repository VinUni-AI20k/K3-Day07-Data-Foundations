# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Trần Quang Mạnh - 2A202601035
**Nhóm:** B63
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> Khi thực hiện so sánh 2 vector, không thể so sánh như so sánh số thông thường vì bản thân vector là một dãy các số. Vì vậy cần phải dùng đến một phép đo là cosine similarity để thực hiện đo độ tương đồng (là góc) giữa 2 vector.

**Ví dụ có độ tương tự CAO:**

- Câu A: Tôi đã ăn bánh mỳ trước khi đi học.
- Câu B: Trước khi đi học, tôi đã ăn bánh mỳ.
- Tại sao tương đồng: Cả 2 câu dù cấu trúc khác nhau nhưng vẫn nói về việc ăn bánh mỳ trước khi đi học.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Sáng nay trời mưa to.
- Câu B: Sáng nay tôi vẫn đi học.
- Tại sao khác: Việc trời mưa to và tôi đi học là 2 việc không có sự liên quan đến nhau mật thiết.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> Khi so sánh 2 văn bản, cosine similarity thực hiện đo độ tương đồng bằng góc giữa 2 vector đại diện cho 2 văn bản đấy. Điều này giúp linh hoạt hơn khi bỏ qua khoảng cách thực tế giữa 2 văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> _Trình bày phép tính:_ Bước dịch giữa hai chunk liên tiếp là `500 - 50 = 450` ký tự. Chunk đầu tiên bao phủ 500 ký tự, sau đó mỗi chunk mới bổ sung tối đa 450 ký tự; vì vậy số chunk là `ceil((10.000 - 500) / 450) + 1 = 23`.
> _Đáp án:_ 23 chunk.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> Khi overlap tăng lên 100, bước dịch giảm còn 400 ký tự nên số chunk tăng thành `ceil((10.000 - 500) / 400) + 1 = 25`. Overlap lớn giúp thông tin nằm ở ranh giới giữa hai chunk ít bị mất ngữ cảnh hơn, đổi lại tăng chi phí lưu trữ và truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Tôi dùng regex `(?<=[.!?])\s+|\.\n` để tách sau dấu chấm, chấm than hoặc chấm hỏi khi tiếp theo là khoảng trắng, đồng thời xử lý trường hợp xuống dòng sau dấu chấm. Sau khi tách, tôi `strip()` và loại phần tử rỗng để văn bản trống, nhiều khoảng trắng hoặc dấu câu ở cuối không tạo ra chunk rỗng. Các câu được ghép theo đúng giới hạn `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán ưu tiên tách theo các separator từ lớn đến nhỏ: đoạn văn, dòng mới, kết thúc câu, khoảng trắng và cuối cùng là cắt theo số ký tự. Nó gom các mảnh vào một bộ đệm cho đến khi vượt `chunk_size`; khi vượt, bộ đệm được xử lý tiếp bằng separator có độ ưu tiên thấp hơn. Base case là khi đoạn hiện tại đã không dài hơn `chunk_size`, hoặc không còn separator phù hợp thì cắt cứng theo kích thước chunk.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> Mỗi `Document` được chuyển thành một record gồm ID nội bộ, nội dung, embedding và metadata; metadata luôn giữ `doc_id` để nhận diện tài liệu gốc. Khi tìm kiếm, hệ thống embed câu truy vấn, tính tích vô hướng với embedding của từng record, sắp xếp điểm giảm dần rồi lấy `top_k`. Với embedding đã được chuẩn hoá, tích vô hướng đóng vai trò tương đương cách xếp hạng theo cosine similarity.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> Tôi lọc metadata trước khi tính điểm tương tự để chỉ so sánh các chunk thỏa điều kiện, ví dụ đúng khoa hoặc đúng ngôn ngữ. Hàm xóa duyệt các record và giữ lại những record có `metadata["doc_id"]` khác ID cần xóa; kết quả trả về là `True` khi ít nhất một chunk đã bị loại. Cách này cũng phù hợp với tài liệu đã được chia thành nhiều chunk vì tất cả đều mang cùng `doc_id`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Agent lấy các chunk liên quan nhất bằng `store.search(question, top_k)`, nối nội dung của chúng thành phần `Context`. Prompt nêu rõ yêu cầu chỉ trả lời dựa trên ngữ cảnh, sau đó đặt lần lượt `Context`, `Question` và vị trí `Answer`. Cấu trúc này tách rõ dữ liệu tham chiếu khỏi câu hỏi và giúp mô hình trả lời có căn cứ hơn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
42 passed in 0.08s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

**Lệnh tái lập kết quả similarity và retrieval:** `.venv\Scripts\python.exe bench.py`.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                     | Câu B                                         | Dự đoán | Điểm thực tế | Đúng? |
| --- | ----------------------------------------- | --------------------------------------------- | ------- | ------------ | ----- |
| 1   | Python là ngôn ngữ lập trình bậc cao.     | Python là một ngôn ngữ lập trình cấp cao.     | cao     | 0,0582       | Không |
| 2   | Sinh viên có thể gia hạn sách ở thư viện. | Thư viện hỗ trợ mượn và gia hạn tài liệu.     | cao     | -0,1218      | Không |
| 3   | Hạn cuối đăng ký học phần là khi nào?     | Khi nào sinh viên phải đóng học phí?          | thấp    | -0,2183      | Có    |
| 4   | Học bổng xét dựa trên thành tích học tập. | Điểm số tốt có thể là tiêu chí nhận học bổng. | cao     | 0,0714       | Không |
| 5   | Ký túc xá có chỗ đỗ xe không?             | Quy trình đăng ký môn học gồm những bước nào? | thấp    | 0,1090       | Có    |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Kết quả bất ngờ nhất là các cặp có ý nghĩa gần nhau như cặp 1 và 2 vẫn có điểm rất thấp khi dùng `MockEmbedder`. Nguyên nhân là mock embedding được sinh xác định từ hash của toàn bộ chuỗi, nên không biểu diễn ngữ nghĩa; nó chỉ phù hợp để kiểm thử kỹ thuật pipeline. Vì vậy, kết quả ngữ nghĩa thực tế cần dùng LocalEmbedder hoặc embedding API, còn `bench.py` hiện là bằng chứng tái lập cho cấu hình mock.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| #   | Câu hỏi (Query)                                      | Top-1 Chunk truy xuất được (tóm tắt)                        | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                      |
| --- | ---------------------------------------------------- | ----------------------------------------------------------- | ---------- | ------------------------------ | -------------------------------------------------------------------- |
| 1   | Ai có thể sử dụng dịch vụ thư viện?                  | Chunk thư viện: sinh viên, giảng viên và nhân viên.         | 0,1722     | Có                             | Demo extractive trả về ngữ cảnh thư viện có ba nhóm người dùng.      |
| 2   | Người dùng cần mang gì khi mượn tài liệu ở thư viện? | Chunk học vụ ở top-1; chunk thư viện có bằng chứng ở top-2. | 0,2349     | Không                          | Demo extractive chứa bằng chứng “thẻ định danh hợp lệ” trong top-3.  |
| 3   | Sinh viên đăng ký học phần ở đâu?                    | Chunk thư viện ở top-1; chunk học vụ có bằng chứng ở top-3. | 0,2105     | Không                          | Demo extractive chứa thông tin “cổng học vụ” trong top-3.            |
| 4   | Trước khi xác nhận đăng ký, cần kiểm tra gì?         | Chunk học vụ có học phần tiên quyết và điều kiện.           | -0,0815    | Có                             | Demo extractive trả về ngữ cảnh về điều kiện và học phần tiên quyết. |
| 5   | Khi gặp lỗi trùng lịch, sinh viên cần làm gì?        | Chunk học vụ ở top-1; bằng chứng xử lý lỗi ở top-3.         | 0,1945     | Không                          | Demo extractive chứa hướng dẫn điều chỉnh lớp ở top-3.               |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

> `bench.py` dùng agent extractive giả lập để kiểm tra việc inject context mà không gọi API LLM. Vì đang dùng `MockEmbedder`, các tóm tắt trên chỉ xác nhận bằng chứng có trong top-3, không phải đánh giá chất lượng trả lời ngữ nghĩa của mô hình. Thiết bị hiện tại đã không đủ điều kiện để gọi API Embedding Model cũng như chạy các mô hình Embedding local từ Huggingface.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Qua benchmark, tôi nhận thấy cần phân biệt rõ kiểm thử kỹ thuật với đánh giá chất lượng ngữ nghĩa. Mock embedding giúp tái lập kết quả và kiểm tra pipeline, nhưng có thể xếp một chunk không liên quan ở top-1; vì thế cần đánh giá cả top-3 và dùng embedder ngữ nghĩa thật khi chấm chất lượng. Tôi cũng học được rằng gắn metadata nhất quán ngay từ lúc ingest giúp kiểm tra nguồn và thu hẹp kết quả theo loại dịch vụ.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | 5 / 5            |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10          |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30          |
| Dự đoán độ tương tự (Similarity Predictions)    | 5 / 5            |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10          |
| **Tổng phần cá nhân**                           | **60 / 60**      |
