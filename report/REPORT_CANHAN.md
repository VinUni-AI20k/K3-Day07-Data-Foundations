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

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                     | Câu B                                         | Dự đoán | Điểm thực tế | Đúng? |
| --- | ----------------------------------------- | --------------------------------------------- | ------- | ------------ | ----- |
| 1   | Python là ngôn ngữ lập trình bậc cao.     | Python là một ngôn ngữ lập trình cấp cao.     | cao     | 0,96         | Có    |
| 2   | Sinh viên có thể gia hạn sách ở thư viện. | Thư viện hỗ trợ mượn và gia hạn tài liệu.     | cao     | 0,89         | Có    |
| 3   | Hạn cuối đăng ký học phần là khi nào?     | Khi nào sinh viên phải đóng học phí?          | thấp    | 0,36         | Có    |
| 4   | Học bổng xét dựa trên thành tích học tập. | Điểm số tốt có thể là tiêu chí nhận học bổng. | cao     | 0,82         | Có    |
| 5   | Ký túc xá có chỗ đỗ xe không?             | Quy trình đăng ký môn học gồm những bước nào? | thấp    | 0,18         | Có    |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Kết quả bất ngờ nhất là cặp 3 vẫn có mức tương đồng thấp nhưng không bằng 0, vì cả hai câu cùng thuộc ngữ cảnh thủ tục học vụ và có cấu trúc hỏi về thời hạn. Điều này cho thấy embedding không chỉ đối sánh từ khóa mà còn biểu diễn một phần chủ đề và cách dùng ngôn ngữ. Vì vậy cần chọn ngưỡng điểm và kiểm tra ngữ cảnh, thay vì chỉ dựa vào một điểm similarity.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| #   | Câu hỏi (Query)                                         | Top-1 Chunk truy xuất được (tóm tắt)                         | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                     |
| --- | ------------------------------------------------------- | ------------------------------------------------------------ | ---------- | ------------------------------ | ------------------------------------------------------------------- |
| 1   | Sinh viên gia hạn sách thư viện bằng cách nào?          | Hướng dẫn gia hạn tài liệu qua hệ thống thư viện.            | 0,84       | Có                             | Nêu các bước gia hạn trực tuyến và lưu ý thời hạn trả sách.         |
| 2   | Khi nào sinh viên có thể đăng ký học phần?              | Quy định về thời gian và các bước đăng ký môn học.           | 0,79       | Có                             | Tóm tắt thời gian mở cổng và quy trình đăng ký.                     |
| 3   | Có thể điều chỉnh hoặc hủy học phần đã đăng ký không?   | Chính sách thêm, hủy hoặc điều chỉnh học phần.               | 0,73       | Có                             | Giải thích việc điều chỉnh phải thực hiện trong thời gian quy định. |
| 4   | Thư viện xử lý trường hợp trả sách quá hạn thế nào?     | Quy định mượn trả, quá hạn và trách nhiệm người mượn.        | 0,76       | Có                             | Nêu yêu cầu trả đúng hạn và hậu quả khi quá hạn.                    |
| 5   | Điều kiện sử dụng dịch vụ thư viện của sinh viên là gì? | Thông tin về đối tượng sử dụng và quy định dịch vụ thư viện. | 0,68       | Có                             | Cho biết sinh viên hợp lệ được dùng dịch vụ theo quy định.          |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

> Qua demo, tôi thấy việc viết câu hỏi có tiêu chí kiểm chứng rõ ràng giúp đánh giá retrieval công bằng hơn so với các câu hỏi quá rộng. Một kinh nghiệm hữu ích khác là gắn metadata nhất quán ngay từ lúc ingest, vì nó cho phép thu hẹp phạm vi tìm kiếm theo loại dịch vụ hoặc đối tượng người dùng. Tôi cũng học được rằng chunk ngắn, có ranh giới câu hợp lý thường dễ trích dẫn và giải thích hơn khi trình bày kết quả.

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
