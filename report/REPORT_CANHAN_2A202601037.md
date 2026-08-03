# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đào Nam Hải
**MSSV:** 2A202601037
**Nhóm:** Nhóm 2k345
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai đoạn văn bản có sự tương đồng lớn về mặt ý nghĩa ngữ nghĩa (chúng trỏ về cùng một hướng trong không gian vector).

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi rất thích ăn phở bò vào buổi sáng.
- Câu B: Xe ô tô chạy bằng xăng hoặc điện.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn không liên quan (đồ ăn và phương tiện giao thông).

**Ví dụ có độ tương tự THẤP:**
- Câu A: Học sinh đang làm bài tập về nhà.
- Câu B: Học sinh đang giải các bài toán được giao về nhà.
- Tại sao khác:

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Bởi vì cosine similarity chỉ quan tâm đến góc giữa hai vector (hướng) thay vì độ lớn của chúng. Các văn bản có cùng ý nghĩa nhưng độ dài khác nhau vẫn có thể có độ tương tự cosine cao.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Số lượng chunk = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Nếu overlap tăng lên 100, số lượng chunk = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25. Tăng độ chồng chéo giúp tránh việc cắt ngang một ý/câu quan trọng, giữ lại ngữ cảnh đầy đủ hơn giữa các chunks.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Hướng tiếp cận:* Sử dụng biểu thức chính quy `(?<=[.!?])\s+|(?<=\.)\n` để chia nhỏ văn bản, với kỹ thuật lookbehind để giữ lại các dấu chấm, chấm hỏi, chấm cảm. Ngoại lệ như câu rỗng sẽ được loại bỏ bằng `.strip()`, sau đó ghép các câu lại theo số lượng tối đa `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Hướng tiếp cận:* Hàm `_split` hoạt động đệ quy: thử cắt văn bản bằng dấu phân cách (separator) đầu tiên, nếu chunk vẫn lớn hơn `chunk_size`, hàm tiếp tục gọi chính nó với mảng separators còn lại. Base case (cơ sở) là khi chiều dài văn bản nhỏ hơn `chunk_size` hoặc khi hết các dấu phân cách để thử.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Hướng tiếp cận:* Nếu có ChromaDB, lưu trữ thông qua client collection trực tiếp của thư viện. Nếu chạy in-memory, lưu bằng list dictionary, tính toán độ tương tự bằng hàm `compute_similarity` với phép tích vô hướng (dot product) chia cho tích độ dài hai vector, sau đó sắp xếp giảm dần.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Hướng tiếp cận:* Lọc (filter) được thực hiện TRƯỚC khi tính similarity (để giảm bớt không gian tìm kiếm). Việc xóa document được thực hiện bằng cách lọc bỏ các chunk có thuộc tính `doc_id` hoặc chuỗi `id` chứa ID của tài liệu đó ra khỏi collection/list.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Hướng tiếp cận:* `KnowledgeBaseAgent` gọi hàm `search` từ store để lấy `top_k` documents phù hợp nhất. Nó ráp tất cả các `content` thành một đoạn ngữ cảnh (Context), sau đó đặt Câu hỏi (Question) vào một prompt string để gọi tới `llm_fn` và trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AI Thực chiến\Thực hành\Day7\K3-Day07-2A202601874-Nguy-n-Xu-n-Ph-ng
plugins: anyio-4.14.2
collected 42 items

tests\test_solution.py ..........................................        [100%]

============================= 42 passed in 0.11s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Con chó sủa gâu gâu | Chó nhà tôi sủa rất to | cao | 0.89 | Đúng |
| 2 | Tôi thích ăn phở | Sở thích của tôi là món phở | cao | 0.85 | Đúng |
| 3 | Trời hôm nay mưa | Mai trời sẽ nắng | thấp | 0.35 | Đúng |
| 4 | Lập trình Python rất thú vị | Code Python khá dễ học | cao | 0.78 | Đúng |
| 5 | Hà Nội là thủ đô của VN | Tôi vừa mua một chiếc xe máy | thấp | 0.05 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Ngạc nhiên nhất:* Những câu từ đồng nghĩa nhưng cấu trúc rất khác (như cặp 2) vẫn có độ tương tự khá cao. Điều này chứng tỏ embedding nắm bắt tốt ý nghĩa ngữ nghĩa đằng sau từ vựng, không bị phụ thuộc hoàn toàn vào các ký tự trùng khớp (lexical match).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên được xem là đạt học phần tiên quyết A để đăng ký học phần B khi đáp ứng điều kiện điểm số nào? | Sinh viên bắt buộc phải học và đạt điểm từ C (hoặc Pass) trở lên... | 0.88 | Có | Cần đạt từ điểm C trở lên ở học phần tiên quyết A. |
| 2 | Nếu xảy ra xung đột lịch học hoặc trùng lịch thi trên hệ thống SIS khi đăng ký học phần thì sinh viên cần xử lý như thế nào? | Hệ thống SIS sẽ tự động chặn đăng ký... | 0.86 | Có | Sinh viên cần chọn nhóm lớp khác hoặc gửi Ticket hỗ trợ cho Registrar Office. |
| 3 | Hậu quả gì sẽ xảy ra đối với sinh viên nếu chậm nộp học phí quá hạn quy định của nhà trường? | Sinh viên nợ học phí quá hạn sẽ bị tạm khóa tài khoản... | 0.91 | Có | Bị khóa tài khoản SIS, không được thi kết thúc HP và không được đăng ký HP tiếp theo. |
| 4 | Theo hướng dẫn dành cho giảng viên, thời hạn tối đa để giảng viên hoàn tất nhập điểm thi kết thúc học phần là bao lâu? | Điểm thi kết thúc học phần phải được nhập hoàn tất... [Filter: audience=faculty] | 0.89 | Có | Giảng viên phải nhập điểm trong vòng 7 ngày làm việc kể từ ngày thi. |
| 5 | Sinh viên bình thường được đăng ký tối đa bao nhiêu tín chỉ và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính quy? | Ràng buộc tín chỉ: Tối đa 24 tín chỉ, tối thiểu 12 tín chỉ... | 0.87 | Có | Đăng ký tối đa 24 tín chỉ và tối thiểu 12 tín chỉ / học kỳ. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Bài học:* Tôi thấy chiến lược chunking đệ quy theo dấu câu hoạt động tốt nhất cho văn bản học thuật hoặc luật. Kết hợp metadata filtering (theo topic/department) thực sự cải thiện rõ rệt độ chính xác của top 3 kết quả.

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
