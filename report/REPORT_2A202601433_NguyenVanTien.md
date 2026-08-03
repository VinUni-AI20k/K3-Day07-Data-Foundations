# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn Tiến
**MSSV:** 2A202601433
**Nhóm:** B2
**Ngày:** 03/08/2026

**Chiến lược tôi phụ trách trong nhóm:** `SentenceChunker(max_sentences_per_chunk=3)`.

**Cấu hình chạy:** corpus nhóm 7 tài liệu (41.241 ký tự), embedder `text-embedding-3-small`, `llm_fn` gọi `gpt-4o-mini`, `top_k=3`.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao nghĩa là gì?**
> Hai vector embedding hướng về cùng một phía, tức mô hình hiểu hai đoạn văn bản nói cùng một nội dung dù dùng từ khác nhau. Trong RAG, đây là cơ sở để tìm ra chunk phù hợp với câu hỏi.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Bước 1: Đưa thẻ thư viện vào đầu đọc mã vạch."
- Câu B: "Đầu tiên quét mã vạch trên thẻ thư viện."
- Tại sao tương đồng: cùng mô tả một thao tác, chỉ khác cách gọi ("đưa vào đầu đọc" và "quét").

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Bạn đọc cần mang thẻ sinh viên."
- Câu B: "Ký túc xá đóng cửa lúc 22 giờ."
- Tại sao khác: một bên là điều kiện sử dụng dịch vụ thư viện, một bên là giờ giấc ký túc xá — hai dịch vụ khác nhau.

**Tại sao cosine similarity được ưu tiên hơn khoảng cách Euclid?**
> Cosine chỉ đo góc, không đo độ dài vector, mà độ dài embedding lại phụ thuộc vào độ dài văn bản. Nhờ vậy một câu hỏi ngắn vẫn so sánh được với một chunk dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:**
```text
bước nhảy = 500 - 50 = 450
số chunk  = ceil((10000 - 50) / 450) = ceil(22,11) = 23 chunk
```
> Đáp án: **23 chunk**.

**Nếu overlap tăng lên 100:**
```text
bước nhảy = 500 - 100 = 400
số chunk  = ceil((10000 - 100) / 400) = ceil(24,75) = 25 chunk
```
> Tăng 2 chunk, tức tăng chi phí nhúng và lưu trữ khoảng 9%. Bù lại, overlap lớn hơn giúp một câu bị cắt ngang ranh giới vẫn xuất hiện trọn vẹn trong ít nhất một chunk.

> Ghi chú riêng với chiến lược của tôi: `SentenceChunker` **không có khái niệm overlap** — nó cắt theo số câu, và ranh giới câu vốn đã là ranh giới ngữ nghĩa tự nhiên. Đây vừa là ưu điểm (không bao giờ cắt giữa câu) vừa là nhược điểm (không có cơ chế bảo hiểm khi ý nghĩa trải qua nhiều câu).

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — đây là chiến lược tôi phụ trách nên tôi đọc kỹ nhất
> Dùng `re.compile(r"(?<=[.!?])\s+")`. Lookbehind nghĩa là điểm cắt nằm **sau** dấu câu, nên dấu chấm/chấm hỏi/chấm than vẫn dính vào cuối câu thay vì bị nuốt mất. `\s+` bắt luôn cả `". "`, `"! "`, `"? "` lẫn `".\n"` chỉ bằng một mẫu duy nhất. Sau khi tách thì `strip()` từng câu và bỏ phần tử rỗng để khoảng trắng thừa không tạo ra "câu ma". Gom câu bằng slicing theo bước `max_sentences_per_chunk` rồi nối lại bằng dấu cách. `max_sentences_per_chunk` được ép `max(1, ...)` trong `__init__` để không bao giờ tạo chunk rỗng.

**`RecursiveChunker.chunk` / `_split`**
> Thử lần lượt `["\n\n", "\n", ". ", " ", ""]`. Ba base case: text rỗng → `[]`; text đã `<= chunk_size` → giữ nguyên; hết separator → cắt cứng theo ký tự. Nếu separator không xuất hiện trong text thì tụt xuống separator kế tiếp. Gom greedy vào buffer, mảnh quá to thì đệ quy tiếp.

**`compute_similarity`**
> `dot(a,b) / (‖a‖·‖b‖)`. Nếu norm của một trong hai vector bằng 0 thì trả `0.0`, tránh `ZeroDivisionError`.

**`ChunkingStrategyComparator.compare`**
> Chạy cả ba chunker trên cùng text, trả về `count`, `avg_length`, `chunks` cho từng chiến lược. Lưu ý `SentenceChunker` ở đây cố định 3 câu/chunk chứ không quy đổi từ `chunk_size`, nên ba chiến lược không hoàn toàn cùng một mốc so sánh — bảng baseline chỉ nên dùng để quan sát xu hướng.

### Lớp EmbeddingStore

**`add_documents` + `search`**
> Mỗi tài liệu thành record `{id, content, metadata, embedding}`; nếu tài liệu không có metadata thì `doc_id` được gán bằng chính `id`. Embedding tính một lần khi add. Search nhúng câu hỏi rồi tính tích vô hướng với toàn bộ store (vector đã chuẩn hóa nên bằng cosine), sort giảm dần, cắt `top_k`.

**`search_with_filter` + `delete_document`**
> Lọc metadata trước rồi mới tính similarity trên tập con — như vậy `top_k` được lấp đầy bằng ứng viên hợp lệ và số phép tính giảm theo tỉ lệ lọc. `delete_document` dựng lại danh sách không chứa `doc_id` cần xóa, so độ dài trước/sau để trả `True`/`False`.

> Lưu ý: nhánh ChromaDB có được khởi tạo nhưng `search` luôn xếp hạng trên bộ nhớ trong, nên thực tế chưa được dùng.

### Tác tử KnowledgeBaseAgent

**`answer`**
> Retrieve top-k → dựng prompt có ngữ cảnh đánh số `[1] [2] [3]` kèm điểm và nguồn → gọi `llm_fn`. Prompt buộc chỉ trả lời dựa trên ngữ cảnh, **nói thẳng khi ngữ cảnh không chứa đáp án**, và trích số hiệu context đã dùng. Nếu không truy xuất được gì thì trả về hằng `NO_CONTEXT_ANSWER` mà không gọi LLM.

> Ràng buộc "nói thẳng khi không có đáp án" hóa ra rất quan trọng — xem Q1 ở Phần 5.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

```bash
python -m pytest tests/ -v
```

```text
============================= 42 passed in 0.21s =============================
```

**Số lượng bài test vượt qua: 42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chủ đề tôi chọn: dịch vụ thư viện.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | "Bước 1: Đưa thẻ thư viện vào đầu đọc mã vạch." | "Đầu tiên quét mã vạch trên thẻ thư viện." | Cao | 0.7154 | Đúng |
| 2 | "Thư viện cho mượn tài liệu." | "Bạn đọc có thể mượn sách tại thư viện." | Cao | 0.5968 | Đúng |
| 3 | "Đặt sách lên giá trả sách tự động." | "Trả tài liệu bằng thiết bị tự động của thư viện." | Cao | 0.4410 | **Sai** |
| 4 | "Bạn đọc cần mang thẻ sinh viên." | "Ký túc xá đóng cửa lúc 22 giờ." | Thấp | 0.3248 | Đúng |
| 5 | "Please return the book on time." | "Vui lòng trả sách đúng hạn." | Cao | 0.4900 | **Sai** |

**Kết quả: 3/5 dự đoán đúng.**

**Điều bất ngờ nhất:**
> Cặp 3. Hai câu mô tả **đúng cùng một thao tác** (trả sách bằng máy tự động) mà chỉ được **0.4410**, không hơn cặp 4 vốn hoàn toàn không liên quan (0.3248) là bao. Nguyên nhân là hai câu đổi gần hết từ vựng cụ thể: "sách" → "tài liệu", "giá trả sách" → "thiết bị", và câu B thêm "của thư viện" còn câu A thì không. Với câu ngắn, mỗi từ chiếm tỉ trọng lớn nên đổi từ vựng là đổi hướng vector.
>
> Điều này giải thích trực tiếp điểm yếu chiến lược của tôi: `SentenceChunker(3)` tạo ra **chunk ngắn**, mà chunk ngắn thì vector nhạy cảm với từ vựng và thiếu ngữ cảnh xung quanh để "neo" chủ đề. Nếu câu hỏi của người dùng dùng từ khác với tài liệu, chunk ngắn dễ trượt hơn chunk dài.
>
> Cặp 5 cũng sai: hai câu Anh–Việt cùng ý chỉ được 0.4900. So với cả nhóm thì kết quả cặp song ngữ dao động rất mạnh (bạn Bằng 0.3270, bạn Nga 0.4473, tôi 0.4900, bạn Tâm 0.5533) — tức khả năng liên kết chéo ngôn ngữ của model **có nhưng không đáng tin**. Corpus và câu hỏi nên thống nhất một ngôn ngữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược của tôi:** `SentenceChunker(max_sentences_per_chunk=3)` → **88 chunk**.
Chạy đúng 5 câu hỏi benchmark chung của nhóm.

| # | Câu hỏi | Top-1 chunk | Score | Hạng chunk chứa đáp án | Câu trả lời của agent | Điểm |
|---:|---|---|---:|---|---|---:|
| 1 | Đăng ký học phần + xử lý chưa đóng học phí | `ueh-dang-ky-huy-hoc-phan::chunk_11` | 0.6953 | hạng 2 | **"Context does not contain the answer."** — từ chối trả lời | 1 |
| 2 | Hạn nộp học phí HK I / HK II | `ftu-quy-dinh-thu-nop-hoc-phi::chunk_1` | 0.6321 | hạng 2 | "30 tháng 11 và 31 tháng 05" — đúng | 1 |
| 3 | Bước đầu tiên khi mượn tài liệu | `hanu-muon-tra-tai-lieu::chunk_1` | 0.5954 | **hạng 1** | "Đưa thẻ vào đầu đọc mã vạch" — đúng | 2 |
| 4 | Giờ đóng cửa / tắt đèn ký túc xá | `tdtu-noi-tru-ky-tuc-xa::chunk_0` | 0.5168 | hạng 1 và 3 | "Đóng cửa 22:00, tắt đèn 22:30" | 1 |
| 5 | Điều kiện xét học bổng *(có filter)* | `ueh-hoc-bong-khuyen-khich::chunk_8` | 0.6730 | **hạng 1** | Chỉ nêu "8 học kỳ chính", thiếu điều kiện "loại khá trở lên" | 1 |

**Chunk liên quan trong top-3: 5/5 — cao nhất nhóm. Điểm truy xuất: 6/10.**

### Kết quả trái với dự đoán ban đầu của nhóm

Bảng baseline `ChunkingStrategyComparator` cho thấy `by_sentences` là chiến lược yếu nhất trên corpus này: văn bản hành chính dùng nhiều dòng gạch đầu dòng và mục đánh số **không kết thúc bằng dấu chấm** ("+ Học kỳ I: …"), nên bộ tách câu không thấy ranh giới và hoặc dồn cục, hoặc cắt vụn. Nhóm giao tôi chạy chính chiến lược này để kiểm chứng nhận định đó bằng số liệu thật.

Kết quả: **6/10, ngang với ba chiến lược còn lại**, và tôi là người **duy nhất có chunk liên quan trong top-3 ở cả 5 câu**. Bài học rút ra cho cả nhóm: **thống kê chunk (count, avg_length) không dự đoán được chất lượng truy xuất** — phải chạy benchmark thật mới biết.

### Hai điểm đáng nói nhất

**Q1 — chiến lược duy nhất ghi điểm.** Cả bốn bạn còn lại đều được 0 điểm ở câu này; chiến lược của tôi đưa được chunk liên quan lên hạng 2. Đáng chú ý hơn là **agent trả lời "Context does not contain the answer"** — tức nó nhận ra ngữ cảnh không đủ để kết luận và **từ chối trả lời**. Trong khi đó agent của các bạn khác lại trả lời rất tự tin dựa trên Điều 6 (nộp phiếu đăng ký) — câu đó có thật trong tài liệu nhưng **sai điều khoản**, vì hình thức đăng ký chung là trực tuyến ở Điều 2.

Nói cách khác: chiến lược của tôi ghi điểm ở Q1 không phải vì tìm ra đáp án, mà vì **không đưa ra đáp án sai**. Với hệ thống tra cứu quy định, từ chối đúng lúc có giá trị hơn một câu trả lời sai nghe thuyết phục.

**Q4 — chunk ngắn lại giúp.** Chiến lược của tôi đưa `tdtu-noi-tru-ky-tuc-xa::chunk_0` lên hạng 1, nên agent trả lời "đóng cửa 22:00, tắt đèn 22:30" — **đúng theo TDTU**. Bốn bạn còn lại đều trộn giờ của hai trường (23h00 của IUBH với 22:30 của TDTU). Nhưng phải nói thật: đây là **may mắn**, không phải thiết kế. Top-1 tình cờ là tài liệu TDTU nên agent chỉ thấy một nguồn; nó không hề phân biệt được nguồn. Nếu thứ tự đảo lại thì tôi cũng sai như các bạn. Gốc rễ vẫn là corpus thiếu trường metadata `institution`.

### Điểm yếu

Q2 và Q5 tôi chỉ được 1 điểm dù chunk đúng nằm trong top-3. Nguyên nhân chung là **chunk thiếu ngữ cảnh tiêu đề**: `SentenceChunker` cắt theo câu nên tiêu đề "1.2 Thời hạn nộp học phí" hay "2.2 Điều kiện xét học bổng" bị tách thành chunk riêng, không đi kèm nội dung bên dưới. Ở Q5, agent lấy đúng chunk hạng 1 nhưng chunk đó bắt đầu ở giữa danh sách nên nó tóm sai điều kiện chính.

### Nếu làm lại

- Ghép dòng tiêu đề của mục vào đầu mỗi chunk câu — giữ ưu điểm "không bao giờ cắt giữa câu" mà thêm được ngữ cảnh chủ đề.
- Tăng `max_sentences_per_chunk` từ 3 lên 5–6 để chunk có đủ ngữ cảnh, đỡ nhạy cảm với thay đổi từ vựng (xem cặp 3 ở Phần 4).
- Thêm metadata `institution` để lỗi Q4 không còn phụ thuộc vào may mắn của thứ hạng.

**Điều hay nhất tôi học được từ thành viên khác:**
> Hai bạn dùng `HeadingChunker` (Việt và Nga) đều thắng Q5 nhờ giữ dòng tiêu đề dính với danh sách điều kiện — đúng thứ chiến lược của tôi thiếu. Nếu kết hợp được hai ý tưởng, cắt theo câu **trong phạm vi từng mục có tiêu đề**, thì có thể vừa giữ ranh giới câu tự nhiên vừa có ngữ cảnh chủ đề. Đây là hướng tôi muốn thử nếu có thêm thời gian.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |

Trừ 1 điểm phần hướng tiếp cận vì nhánh ChromaDB chưa thực sự được `search` sử dụng.
