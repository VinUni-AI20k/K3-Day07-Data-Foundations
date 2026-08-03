# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Ngô Minh Phong - 2A202602025
**Nhóm:** Balerion
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiệm cận 1) thể hiện góc giữa hai vector rất nhỏ, tức là chúng hướng về gần như cùng một phía trong không gian. Về mặt ứng dụng, điều này đồng nghĩa với việc hai đối tượng dữ liệu được biểu diễn có mức độ tương đồng hoặc ý nghĩa ngữ nghĩa cực kỳ giống nhau.

**Ví dụ có độ tương tự CAO:**
Câu A: "Hướng dẫn cài đặt hệ điều hành Windows 11."
Câu B: "Cách setup Windows 11 cho máy tính."
Dù sử dụng các từ vựng khác nhau ("Hướng dẫn cài đặt" vs "Cách setup"), hai câu này mang ngữ nghĩa gần như y hệt nhau. Khi được mô hình AI chuyển thành vector, chúng sẽ hướng về cùng một phía trong không gian đa chiều, cho ra độ tương tự cosine rất cao (ví dụ: ~0.95).

**Ví dụ có độ tương tự THẤP:**
Câu A: "Hướng dẫn cài đặt hệ điều hành Windows 11."
Câu B: "Bí quyết nấu món phở bò ngon chuẩn vị."
Hai câu này đề cập đến hai chủ đề hoàn toàn không liên quan (công nghệ và ẩm thực). Khi được chuyển thành vector, hướng của chúng sẽ gần như vuông góc với nhau (góc ~90 độ) trong không gian.Do đó, độ tương tự cosine của chúng sẽ rất thấp và xấp xỉ bằng 0 (ví dụ: ~0.02). Điều này báo cho hệ thống (như trong các ứng dụng tìm kiếm hoặc RAG) biết rằng nội dung của hai câu này hoàn toàn độc lập và không có sự giao thoa về mặt ý nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự cosine được ưu tiên vì nó đo lường góc giữa hai vector để tập trung hoàn toàn vào ngữ nghĩa, bỏ qua độ lớn của vector (vốn bị ảnh hưởng bởi độ dài văn bản). Nhờ đó, hai văn bản có cùng chủ đề nhưng dài ngắn khác nhau vẫn được đánh giá là tương đồng, trong khi khoảng cách Euclid sẽ bị sai lệch rất lớn do độ chênh lệch về độ dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Số lượng chunk = làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11)
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi độ chồng chéo (overlap) tăng lên 100, tổng số lượng chunk sẽ tăng lên do khoảng cách dịch chuyển (stride) giữa mỗi lần cắt bị ngắn lại. Việc tăng overlap nhằm đảm bảo các câu hoặc đoạn thông tin quan trọng không bị cắt đứt đột ngột ở ranh giới các chunk, giúp hệ thống RAG giữ được trọn vẹn ngữ cảnh khi truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Sử dụng biểu thức chính quy (regex) `(?<=[.!?]) +` kết hợp lookbehind để tách câu chính xác mà vẫn giữ lại dấu câu cuối cùng. Thuật toán gom các câu liên tiếp sao cho mỗi đoạn không vượt quá `max_sentences_per_chunk`, và lưu ý loại bỏ các chuỗi rỗng hay khoảng trắng thừa để tránh rác dữ liệu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Áp dụng chiến lược chia để trị với hai base cases: văn bản đủ ngắn thì trả về luôn, hoặc hết separator thì cắt cứng theo `chunk_size`. Nếu văn bản dài, hàm thử cắt bằng separator ưu tiên cao nhất, gộp các mảnh lại cho đến khi đầy chunk. Các mảnh nào vẫn quá dài thì tiếp tục đưa vào đệ quy với separator có ưu tiên thấp hơn (nằm sau trong mảng).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Hàm `add_documents` duyệt qua các Document, sao chép an toàn `metadata` để không sửa nhầm, tự gán ID cho chunk và gọi hàm embed content để nhét vào store (bộ nhớ trong). Hàm `search` nhúng câu query thành vector (chỉ một lần) rồi tính `_dot` với tất cả chunk đã lưu, lưu lại điểm số, sắp xếp giảm dần và cắt đúng `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Hàm `search_with_filter` tiến hành vòng lặp để lọc (filter) trước các bản ghi trong danh sách, chỉ giữ lại các chunk có metadata trùng khớp, sau đó mới gọi hàm `_search_records`. Hàm `delete_document` sử dụng list comprehension để lọc lại (keep) toàn bộ `_store` ngoại trừ các chunk có chứa `metadata['doc_id']` cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Cấu trúc hàm gọi đến vector store để lấy `top_k` chunk, ghép nối lại thành đoạn văn bản ngữ cảnh (context_str), mỗi đoạn được đánh số đếm `[1], [2]...` kèm theo `doc_id` của nó. Prompt truyền vào LLM được chia rõ các phần: khối Hướng dẫn nghiêm ngặt (chỉ dùng context; nói rõ nếu không đủ), khối Context và khối Question.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.5, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Cuong\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: D:\VinUni\LABS\K3-DAY07_TeamBalerion
plugins: anyio-4.12.0, Faker-37.1.0, langsmith-0.10.10
collecting ... collected 42 items

...
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 1.78s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Tôi thích nghiên cứu về trí tuệ nhân tạo. | Học máy và AI là niềm đam mê của tôi. | cao | 0.8542 | Đúng |
| 2 | Tôi rất yêu thích lập trình Python. | Tôi cực kỳ ghét lập trình Python. | thấp | 0.8123 | Sai |
| 3 | Con chó nhà hàng xóm đang sủa ầm ĩ. | Một chú cún đang kêu rất ồn ào bên ngoài. | cao | 0.7491 | Đúng |
| 4 | VinUni là một trường đại học xuất sắc. | Hôm nay trời mưa to và gió rất lớn. | thấp | 0.0521 | Đúng |
| 5 | Apple ra mắt dòng điện thoại mới. | Quả táo này ăn rất giòn và ngọt. | thấp | 0.1584 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp số 2 mang lại kết quả bất ngờ nhất (2 câu mang nghĩa đối lập nhưng điểm tương đồng lại rất cao > 0.8). Điều này cho thấy mô hình embedding biểu diễn từ vựng bằng cách gom nhóm chúng theo "ngữ cảnh xuất hiện chung" (cùng nói về lập trình Python, có cấu trúc ngữ pháp y hệt) thay vì hiểu trọn vẹn ngữ nghĩa đối lập (yêu thích >< ghét).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tất cả sinh viên đại học nhập học từ năm 2025 đến năm 2030 sẽ nhận được mức hỗ trợ học phí là bao nhiêu? | important-dates-2026::chunk_3: 100% sinh viên nhập học từ năm 2025 đến 2030 sẽ tiếp tục được nhận tài trợ 35%... | 0.8142 | Có | [DUMMY LLM] Tôi đã đọc context... |
| 2 | Ứng viên nữ theo đuổi lĩnh vực khoa học công nghệ có thể nhận loại học bổng nào và trị giá bao nhiêu? | undergraduate-scholarships-2026::chunk_3: Học bổng đặc thù ngành: Trị giá 5% học phí dành cho các ngành học đặc thù... | 0.8111 | Có | [DUMMY LLM] Tôi đã đọc context... |
| 3 | Kỳ tuyển sinh sớm (Early Round) hệ đại học năm 2026 của VinUni diễn ra vào khoảng thời gian nào? | important-dates-2026::chunk_0: # Các mốc quan trọng trong tuyển sinh đại học VinUni năm 2026... | 0.8175 | Có | [DUMMY LLM] Tôi đã đọc context... |
| 4 | Sinh viên ứng tuyển vào kỳ Tuyển sinh sớm (Early Round) và tham gia VinUni Open Day sẽ nhận được đặc quyền tài chính gì? | important-dates-2026::chunk_9: “Đặc quyền” thêm cho ứng viên nộp hồ sơ tại kỳ Tuyển sinh sớm: Miễn lệ phí tuyển... | 0.7442 | Có | [DUMMY LLM] Tôi đã đọc context... |
| 5 | Chương trình Tiến sĩ tại VinUni tập trung nghiên cứu chuyên sâu vào những lĩnh vực trọng yếu nào? | phd-admissions-2026::chunk_0: # Tuyển sinh chương trình Tiến sĩ VinUni năm 2026 Chào mừng bạn đến với chương... | 0.7492 | Có | [DUMMY LLM] Tôi đã đọc context... |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Điều tôi ấn tượng nhất là các bạn trong team đã có thể thảo luận và đưa ra nhiều ý tưởng, đề xuất cải thiện hướng tiếp cận để code dễ đọc, dễ test và dễ bảo trì, ví dụ như việc tách biến `embedding_fn` để mock dễ dàng khi test và có thể mở rộng thêm các loại embedder khác trong tương lai.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5/ 5 |
| Hướng tiếp cận của tôi (My Approach) | 10/ 10 |
| Hoàn thiện code (Core Implementation — tests) | 30/ 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5/ 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10/ 10 |
| **Tổng phần cá nhân** | **60/ 60** |
