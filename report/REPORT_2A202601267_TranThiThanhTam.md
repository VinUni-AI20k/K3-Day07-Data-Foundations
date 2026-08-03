# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Thị Thanh Tâm
**MSSV:** 2A202601267
**Nhóm:** B2
**Ngày:** 03/08/2026

**Chiến lược tôi phụ trách trong nhóm:** `FixedSizeChunker(chunk_size=500, overlap=50)`.

**Cấu hình chạy:** corpus nhóm 7 tài liệu (41.241 ký tự), embedder `text-embedding-3-small`, `llm_fn` gọi `gpt-4o-mini`, `top_k=3`.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao nghĩa là gì?**
> Hai vector embedding hướng về cùng một phía trong không gian nhiều chiều, tức mô hình hiểu hai đoạn văn bản nói về cùng một nội dung — kể cả khi chúng dùng từ ngữ khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Học phí được thu theo học kỳ."
- Câu B: "Mỗi học kỳ sinh viên phải nộp tiền học một lần."
- Tại sao tương đồng: cùng nói về chu kỳ thu học phí, chỉ khác cách diễn đạt.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Hạn nộp học phí học kỳ I là ngày 30 tháng 11."
- Câu B: "Thư viện mở cửa từ 7h30 đến 22h00."
- Tại sao khác: hai dịch vụ khác nhau, chỉ giống nhau ở chỗ đều nhắc tới mốc thời gian.

**Tại sao cosine similarity được ưu tiên hơn khoảng cách Euclid?**
> Cosine chỉ đo góc giữa hai vector, bỏ qua độ dài — mà độ dài embedding phụ thuộc mạnh vào độ dài văn bản. Nhờ vậy một câu hỏi ngắn vẫn so sánh được với một chunk dài, đúng thứ retrieval cần.

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
> Tăng 2 chunk, tức tăng chi phí nhúng và lưu trữ khoảng 9%. Đổi lại, overlap lớn hơn giúp một câu nằm vắt ngang ranh giới chunk vẫn xuất hiện trọn vẹn trong ít nhất một chunk — quan trọng với văn bản quy định, nơi "điều kiện" và "hệ quả" thường nằm liền nhau.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`**
> Dùng regex `(?<=[.!?])\s+`. Lookbehind giúp giữ lại dấu câu ở cuối câu, còn `\s+` bắt được cả `". "`, `"! "`, `"? "` lẫn `".\n"` chỉ bằng một mẫu. Sau khi tách thì `strip()` từng câu và bỏ phần tử rỗng, rồi gom theo `max_sentences_per_chunk`. Text rỗng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`**
> Thử lần lượt các separator `["\n\n", "\n", ". ", " ", ""]`. Ba base case: text rỗng trả `[]`; text đã ngắn hơn `chunk_size` thì trả nguyên khối; hết separator thì cắt cứng theo ký tự. Nếu separator không tồn tại trong text thì tụt xuống separator kế tiếp thay vì trả về đoạn quá khổ.

**`compute_similarity`**
> Công thức cosine `dot(a,b) / (‖a‖·‖b‖)`, dùng lại hàm `_dot` có sẵn. Trường hợp một trong hai vector có độ dài bằng 0 thì trả về `0.0` để tránh chia cho 0.

**`ChunkingStrategyComparator.compare`**
> Gọi lần lượt cả ba chunker trên cùng đoạn text, trả về dict ba khóa `fixed_size` / `by_sentences` / `recursive`, mỗi khóa gồm `count`, `avg_length` và danh sách `chunks` để đối chiếu bằng mắt.

### Lớp EmbeddingStore

**`add_documents` + `search`**
> Mỗi tài liệu được chuẩn hóa thành record gồm `id`, `content`, `metadata`, `embedding`. Nếu tài liệu không có metadata thì tự gán `doc_id` bằng chính `id` để việc lọc và xóa sau này vẫn chạy. Khi tìm kiếm, hệ thống nhúng câu hỏi một lần rồi tính tích vô hướng với mọi embedding đã lưu — vì backend trả vector đã chuẩn hóa nên tích vô hướng bằng đúng cosine — sau đó sắp xếp giảm dần và cắt `top_k`.

**`search_with_filter` + `delete_document`**
> Lọc metadata **trước** rồi mới tính similarity trên tập con. Lọc trước có hai lợi ích: `top_k` được lấp đầy bằng ứng viên hợp lệ, và số phép tính giảm theo tỉ lệ lọc. `delete_document` dựng lại danh sách không chứa `doc_id` cần xóa rồi so độ dài trước/sau để trả `True` hoặc `False`.

> Lưu ý trung thực: nhánh ChromaDB có được khởi tạo nhưng `search` và `search_with_filter` **luôn** xếp hạng trên bộ nhớ trong (`self._store`), nên trên thực tế nhánh Chroma chưa được sử dụng.

### Tác tử KnowledgeBaseAgent

**`answer`**
> Ba bước: truy xuất top-k → dựng prompt → gọi `llm_fn`. Ngữ cảnh được đánh số `[1] [2] [3]` kèm điểm số và nguồn để câu trả lời trích dẫn được. Prompt yêu cầu chỉ trả lời dựa trên ngữ cảnh và nói thẳng khi ngữ cảnh không chứa đáp án. Nếu không truy xuất được gì thì trả về thông báo cố định, không gọi LLM.

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

Chủ đề tôi chọn: học phí — cùng mảng với chiến lược tôi phụ trách.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | "Học phí được thu theo học kỳ." | "Mỗi học kỳ sinh viên phải nộp tiền học một lần." | Cao | 0.6385 | Đúng |
| 2 | "Sinh viên nộp học phí qua ngân hàng." | "Có thể chuyển khoản học phí tại quầy giao dịch." | Cao | 0.5690 | Đúng |
| 3 | "Hạn nộp học phí học kỳ I là ngày 30 tháng 11." | "Thư viện mở cửa từ 7h30 đến 22h00." | Thấp | 0.3190 | Đúng |
| 4 | "Nộp học phí trễ thì không được dự thi." | "Sinh viên chưa hoàn thành học phí sẽ bị hạn chế quyền dự thi." | Cao | 0.6008 | Đúng |
| 5 | "Tuition must be paid before the exam." | "Sinh viên phải đóng học phí trước kỳ thi." | Cao | 0.5533 | Đúng |

**Kết quả: 5/5 dự đoán đúng.**

**Điều bất ngờ nhất:**
> Cặp 5 — hai câu khác ngôn ngữ nhưng vẫn đạt 0.5533, cao hơn hẳn cặp 3 vốn cùng tiếng Việt. Điều này **ngược với kết quả của bạn Bằng**, nơi một cặp Anh–Việt cùng ý chỉ được 0.3270. So lại hai cặp thì khác biệt nằm ở chỗ cặp của tôi ngắn, cấu trúc song song và trùng nhiều thực thể ("học phí/tuition", "kỳ thi/exam"), còn cặp của bạn Bằng dài và diễn đạt lệch nhau hơn. Kết luận rút ra: mô hình **có** khả năng liên kết chéo ngôn ngữ, nhưng khả năng đó yếu và phụ thuộc vào độ song song của câu — nên vẫn không đáng tin để làm corpus song ngữ.
>
> Điểm thứ hai: cặp 3 hoàn toàn không liên quan mà vẫn được 0.3190, tức điểm cosine không bao giờ về gần 0. Phải đọc điểm theo thứ hạng, không đặt ngưỡng tuyệt đối.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược của tôi:** `FixedSizeChunker(chunk_size=500, overlap=50)` → **94 chunk**.
Chạy đúng 5 câu hỏi benchmark chung của nhóm (xem `REPORT_NHOM.md` Phần 3).

| # | Câu hỏi | Top-1 chunk | Score | Có liên quan? | Câu trả lời của agent | Điểm |
|---:|---|---|---:|---|---|---:|
| 1 | Đăng ký học phần bằng hình thức nào, chưa đóng học phí bị xử lý ra sao? | `ftu-quy-dinh-thu-nop-hoc-phi::chunk_4` | 0.7168 | Không có trong top-3 | Trả lời theo Điều 6 (nộp phiếu đăng ký) — sai điều khoản | 0 |
| 2 | Hạn nộp học phí HK I và HK II? | `ftu-quy-dinh-thu-nop-hoc-phi::chunk_1` | 0.6733 | Đúng, hạng 1 | "30 tháng 11 và 31 tháng 05" — đúng | 2 |
| 3 | Bước đầu tiên khi mượn tài liệu tự động? | `hanu-muon-tra-tai-lieu::chunk_0` | 0.6037 | Đúng, hạng 1 | "Đưa thẻ vào đầu đọc mã vạch" — đúng | 2 |
| 4 | Ký túc xá đóng cửa và tắt đèn lúc mấy giờ? | `tdtu-noi-tru-ky-tuc-xa::chunk_1` | 0.4881 | Đúng, hạng 2 và 3 | "Đóng cửa 23:00, tắt đèn 22:30" — trộn hai trường | 1 |
| 5 | Điều kiện xét học bổng? | `ueh-hoc-bong-khuyen-khich::chunk_8` | 0.6575 | Đúng, hạng 1 | Chỉ nêu điều kiện "8 học kỳ chính", thiếu điều kiện "loại khá trở lên" | 1 |

**Chunk liên quan trong top-3: 4/5. Điểm truy xuất: 6/10.**

### Nhận xét về chiến lược của tôi

Điểm mạnh rõ nhất là ở câu 2 và câu 3. Chunk cố định 500 ký tự khá ngắn nên khi câu trả lời là một mốc số cụ thể ("30 tháng 11", "31 tháng 05"), con số đó chiếm tỉ trọng lớn trong vector và được xếp hạng 1. Overlap 50 ký tự cũng cứu được vài câu bị cắt ngang ranh giới.

Điểm yếu là chunk **không mang theo tiêu đề**. Ở câu 5 tôi lấy đúng chunk ở hạng 1 nhưng vẫn chỉ được 1 điểm, vì chunk đó bắt đầu bằng đoạn giữa câu ("…ặc bằng số tín chỉ bố trí theo kế hoạch đào tạo…") nên agent tóm sai điều kiện chính. Hai bạn dùng `HeadingChunker` giữ được tiêu đề "2.2 Điều kiện để sinh viên tham gia xét học bổng" nên agent trả lời đúng và được 2 điểm.

Câu 4 thì cả 5 thành viên đều chỉ được 1 điểm: retrieval đúng nhưng agent ghép giờ đóng cửa của IUBH (23h00) với giờ tắt đèn của TDTU (22:30) thành một câu trả lời không đúng với trường nào. Nguyên nhân là corpus gom quy định của 6 trường mà thiếu trường metadata phân biệt cơ sở đào tạo.

### Nếu làm lại

- Ghép dòng tiêu đề của mục vào đầu mỗi chunk cố định — giữ được ưu thế chunk ngắn mà vẫn có ngữ cảnh.
- Thêm metadata `institution` để agent không trộn quy định hai trường.
- Với câu hỏi hỏi hai ý như câu 1 thì tách thành hai truy vấn rồi hợp kết quả.

**Điều hay nhất tôi học được từ thành viên khác:**
> Cùng corpus và cùng bộ câu hỏi, chỉ đổi cách cắt chunk mà điểm chênh từ 4/10 tới 6/10. Đáng chú ý là bốn chiến lược cùng đạt 6/10 nhưng thắng ở những câu khác nhau — chiến lược của tôi thắng câu có mốc số, chiến lược chunk theo tiêu đề thắng câu tra cứu điều khoản. Vậy không có chiến lược nào tốt nhất tuyệt đối; phải chọn theo dạng câu hỏi mà người dùng hay hỏi.

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

Trừ 1 điểm phần hướng tiếp cận vì nhánh ChromaDB chưa thực sự được `search` sử dụng. Phần truy xuất ghi đúng điểm chạy thật là 6/10.
