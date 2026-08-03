# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Huỳnh Hoàng Việt
**MSSV:** 2A202601105
**Nhóm:** B2
**Ngày:** 03/08/2026

**Chiến lược tôi phụ trách trong nhóm:** `HeadingChunker(chunk_size=900)` — chiến lược custom do tôi thiết kế, đáp ứng yêu cầu riêng của lớp K3 về chia nhỏ theo tiêu đề/mục.

**Cấu hình chạy:** corpus nhóm 7 tài liệu (41.241 ký tự), embedder `text-embedding-3-small`, `llm_fn` gọi `gpt-4o-mini`, `top_k=3`.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao nghĩa là gì?**
> Hai vector embedding cùng hướng trong không gian nhiều chiều, tức mô hình mã hóa hai đoạn văn bản với cùng một "tổ hợp chủ đề". Hai văn bản nói cùng một nội dung, kể cả khi không dùng chung từ nào.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Không được nấu ăn trong phòng ở."
- Câu B: "Cấm sử dụng bếp nấu nướng tại phòng nội trú."
- Tại sao tương đồng: cùng một điều cấm, chỉ khác cách diễn đạt và mức độ trang trọng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên phải giữ gìn vệ sinh phòng ở."
- Câu B: "Điểm trung bình tích lũy xét học bổng được tính theo tín chỉ."
- Tại sao khác: một bên là nội quy sinh hoạt, một bên là công thức tính điểm — khác cả chủ đề lẫn mục đích.

**Tại sao cosine similarity được ưu tiên hơn khoảng cách Euclid?**
> Cosine chỉ đo góc, bỏ qua độ lớn vector. Độ lớn embedding phụ thuộc mạnh vào độ dài văn bản, nên với Euclid, một điều khoản dài và một câu hỏi ngắn cùng chủ đề vẫn bị coi là "xa nhau". Cosine so được câu hỏi ngắn với chunk dài — đúng thứ retrieval cần.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:**
```text
bước nhảy = 500 - 50 = 450
số chunk  = ceil((10000 - 50) / 450) = ceil(22,11) = 23 chunk
```
> Đáp án: **23 chunk**. Kiểm chứng bằng `FixedSizeChunker`: vị trí bắt đầu 0, 450, …, 9900 → đúng 23 chunk.

**Nếu overlap tăng lên 100:**
```text
bước nhảy = 500 - 100 = 400
số chunk  = ceil((10000 - 100) / 400) = ceil(24,75) = 25 chunk
```
> Tăng 2 chunk (~9% chi phí nhúng và lưu trữ). Đổi lại, overlap lớn hơn giúp một điều khoản nằm vắt ngang ranh giới chunk vẫn xuất hiện trọn vẹn trong ít nhất một chunk. Với văn bản quy định, "điều kiện" và "hệ quả" thường nằm liền nhau nên cắt đứt giữa chừng là mất luôn câu trả lời.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`**
> Regex `(?<=[.!?])\s+`. Lookbehind giữ dấu câu lại ở cuối câu, `\s+` bắt được cả `". "`, `"! "`, `"? "` lẫn `".\n"` bằng một mẫu. Sau khi tách thì `strip()` và loại phần tử rỗng, rồi gom theo `max_sentences_per_chunk` bằng slicing. Text rỗng hoặc toàn khoảng trắng trả về `[]`.

**`RecursiveChunker.chunk` / `_split`**
> Ba base case: text rỗng → `[]`; `len(text) <= chunk_size` → trả nguyên khối; hết separator hoặc gặp `""` → cắt cứng theo ký tự. Nếu separator không có trong text thì tụt xuống separator kế tiếp. Các mảnh được gom greedy vào buffer chừng nào còn `<= chunk_size`; mảnh quá to thì đệ quy với danh sách separator còn lại.

**`compute_similarity`**
> `dot(a,b) / (‖a‖·‖b‖)`, dùng lại `_dot`. Nếu một trong hai norm bằng 0 thì trả `0.0` để tránh chia cho 0.

**`ChunkingStrategyComparator.compare`**
> Chạy cả ba chunker trên cùng text, trả dict ba khóa `fixed_size` / `by_sentences` / `recursive`, mỗi khóa gồm `count`, `avg_length`, `chunks`. `overlap` của `FixedSizeChunker` được suy ra bằng 10% `chunk_size` để không vượt quá kích thước chunk khi `chunk_size` nhỏ.

### Chiến lược custom của tôi — `HeadingChunker`

> Đây là phần tôi đầu tư nhiều nhất, nằm trong `NguyenDuyHaiBang_2A202601225/custom_chunkers.py`.

> Nhận xét xuất phát: corpus K3 gần như luôn đánh số theo `Chương … / Điều N. … / I) … / 1.1 …`. Một điều khoản là một đơn vị ngữ nghĩa trọn vẹn, nên cắt tại ranh giới tiêu đề sẽ cho chunk trả lời được trọn một câu hỏi. Thuật toán ba bước: (1) cắt tại mỗi dòng khớp regex tiêu đề, tiêu đề đi kèm phần thân bên dưới nó; (2) gộp mục quá ngắn với mục kế tiếp để không tạo chunk chỉ có mỗi tiêu đề; (3) mục quá dài thì cắt tiếp theo dòng, và **lặp lại dòng tiêu đề ở đầu mỗi phần** (`"{heading} (tiếp)"`) để phần sau không mất ngữ cảnh khi nhúng.

```python
HEADING = re.compile(
    r"^\s*("
    r"Điều\s+\d+|CHƯƠNG\s+[IVXLC\d]+|Chương\s+[IVXLC\d]+|"
    r"Mục\s+\d+|MỤC\s+\d+|Phần\s+\d+|"
    r"[IVX]+\)|[IVX]+\.\s|"
    r"\d+(\.\d+)*[.)]\s|"
    r"#{1,6}\s"
    r")"
)
```

> Bước (3) là quyết định đáng nói nhất. Không có nó, phần thứ hai của một điều khoản dài sẽ trở thành chunk "mồ côi" không biết mình thuộc điều nào — đúng lỗi mà `RecursiveChunker` mắc phải ở Q5.

### Lớp EmbeddingStore

**`add_documents` + `search`**
> Mỗi tài liệu thành record `{id, content, metadata, embedding}`; `doc_id` được gán mặc định bằng `id` nếu tài liệu không có metadata. Search nhúng câu hỏi một lần rồi tính tích vô hướng với mọi embedding đã lưu (vector đã chuẩn hóa nên bằng cosine), sort giảm dần, cắt `top_k`.

**`search_with_filter` + `delete_document`**
> Lọc metadata trước, tìm similarity sau — `top_k` được lấp đầy bằng ứng viên hợp lệ và số phép tính giảm theo tỉ lệ lọc. `delete_document` dựng lại danh sách bỏ `doc_id` cần xóa rồi so độ dài trước/sau để trả `True`/`False`.

> Lưu ý: nhánh ChromaDB có được khởi tạo nhưng `search` luôn xếp hạng trên bộ nhớ trong, nên thực tế nhánh này chưa được dùng.

### Tác tử KnowledgeBaseAgent

**`answer`**
> Retrieve → dựng prompt → gọi `llm_fn`. Ngữ cảnh đánh số `[1] [2] [3]` kèm điểm và nguồn để truy vết. Prompt buộc chỉ trả lời theo ngữ cảnh, nói thẳng khi ngữ cảnh không có đáp án, và trích số hiệu context. Store rỗng thì trả hằng `NO_CONTEXT_ANSWER`, không gọi LLM.

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

Chủ đề tôi chọn: nội quy ký túc xá, và đặc biệt là **các dòng tiêu đề** — vì chiến lược của tôi dựa hoàn toàn vào tiêu đề.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | "Điều 2. Quy định về sinh hoạt" | "Các qui định liên quan tới sinh hoạt hằng ngày" | Cao | 0.5539 | Đúng |
| 2 | "Giờ đóng cửa ký túc xá là 23h00." | "Ký túc xá ngừng cho ra vào lúc 11 giờ đêm." | Cao | 0.5795 | Đúng |
| 3 | "Không được nấu ăn trong phòng ở." | "Cấm sử dụng bếp nấu nướng tại phòng nội trú." | Cao | 0.6134 | Đúng |
| 4 | "Sinh viên phải giữ gìn vệ sinh phòng ở." | "Điểm trung bình tích lũy xét học bổng được tính theo tín chỉ." | Thấp | 0.2593 | Đúng |
| 5 | "Điều 1. Giờ giấc sinh hoạt, học tập" | "Điều 3. Quy định về an ninh, trật tự" | Cao | 0.3310 | **Sai** |

**Kết quả: 4/5 dự đoán đúng.**

**Điều bất ngờ nhất:**
> Cặp 5. Tôi đoán cao vì hai câu **cùng dạng cấu trúc** — đều là dòng "Điều N." của cùng một văn bản nội quy, dùng chung khuôn mẫu ngôn ngữ hành chính. Thực tế chỉ **0.3310**, thấp gần bằng cặp 4 vốn hoàn toàn không liên quan.
>
> Bài học rất trực tiếp với chiến lược của tôi: embedding **không quan tâm tới cấu trúc, chỉ quan tâm tới nội dung**. Hai tiêu đề cùng khuôn "Điều N." nhưng nói về hai chủ đề khác nhau (giờ giấc và an ninh) thì vector vẫn xa nhau. Đây thực ra là tin tốt: nó có nghĩa là khi tôi ghép tiêu đề vào đầu mỗi chunk, tiêu đề **đóng góp tín hiệu chủ đề thật** chứ không phải nhiễu khuôn mẫu làm mọi chunk giống nhau. Nếu điều ngược lại đúng thì `HeadingChunker` đã phản tác dụng.
>
> Cặp 2 cũng đáng chú ý: "23h00" và "11 giờ đêm" là cùng một mốc thời gian viết theo hai kiểu, và model vẫn nhận ra (0.5795). Nhưng con số không phải thế mạnh của chunk dài — xem Q2 ở Phần 5.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược của tôi:** `HeadingChunker(chunk_size=900)` → **86 chunk** — ít nhất nhóm.
Chạy đúng 5 câu hỏi benchmark chung của nhóm.

| # | Câu hỏi | Top-1 chunk | Score | Hạng chunk chứa đáp án | Câu trả lời của agent | Điểm |
|---:|---|---|---:|---|---|---:|
| 1 | Đăng ký học phần + xử lý chưa đóng học phí | `ueh-dang-ky-huy-hoc-phan::chunk_8` | 0.6649 | ngoài top-3 (hạng 4) | Trả lời theo Điều 6 — sai điều khoản | 0 |
| 2 | Hạn nộp học phí HK I / HK II | `ftu-quy-dinh-thu-nop-hoc-phi::chunk_1` | 0.6578 | hạng 3 | "30 tháng 11 và 31 tháng 05" — đúng | 1 |
| 3 | Bước đầu tiên khi mượn tài liệu | `hanu-muon-tra-tai-lieu::chunk_0` | 0.5901 | **hạng 1** | "Đưa thẻ vào đầu đọc mã vạch" — đúng | 2 |
| 4 | Giờ đóng cửa / tắt đèn ký túc xá | `iubh-noi-quy-ky-tuc-xa::chunk_1` | 0.5756 | hạng 1 và 3 | "Đóng cửa 23h00, tắt đèn 22:30" — trộn hai trường | 1 |
| 5 | Điều kiện xét học bổng *(có filter)* | `ueh-hoc-bong-khuyen-khich::chunk_7` | 0.6386 | **hạng 1** | Nêu đúng "loại khá trở lên" + điểm rèn luyện | 2 |

**Chunk liên quan trong top-3: 4/5. Điểm truy xuất: 6/10.**

### Chiến lược của tôi thắng ở đâu, thua ở đâu

**Thắng rõ nhất — Q5.** Điều kiện xét học bổng nằm trong danh sách gạch đầu dòng dưới tiêu đề "2.2 Điều kiện để sinh viên tham gia xét học bổng". Chiến lược của tôi giữ nguyên cả khối nên chunk đó ở **hạng 1/86** và agent trả lời đúng. Cùng câu này, `RecursiveChunker(500)` của bạn Bằng cắt tại `\n\n` làm tiêu đề rời khỏi danh sách, đẩy chunk đáp án xuống **hạng 7/100** và được 0 điểm. Đây là bằng chứng trực tiếp nhất cho giả thuyết thiết kế của tôi.

**Thua ở Q2 (chỉ 1 điểm).** Chunk chứa hai mốc "30/11" và "31/05" dài **789 ký tự**, nên hai con số bị pha loãng trong vector và chunk tụt xuống hạng 3. Bạn Tâm dùng `FixedSizeChunker(500,50)` và bạn Nga dùng `HeadingChunker(500)` đều đưa được chunk này lên hạng 1 và ăn 2 điểm. Bài học: **chunk dài tốt cho câu hỏi tra cứu điều khoản, nhưng hại cho câu hỏi cần mốc số cụ thể.**

**Q4 — cả 5 thành viên đều mắc.** Retrieval của tôi tốt (chunk đúng ở hạng 1), nhưng agent ghép "đóng cửa 23h00" của IUBH với "tắt đèn 22:30" của TDTU thành một câu trả lời không đúng với trường nào. Đây là lỗi tầng LLM do corpus gom quy định 6 trường mà thiếu metadata phân biệt cơ sở đào tạo. Không chiến lược chunking nào cứu được lỗi này.

**Về chi phí:** chiến lược của tôi tạo **ít chunk nhất nhóm (86)** mà vẫn đạt điểm ngang các bạn — tức chất lượng và chi phí nhúng không nhất thiết đánh đổi nhau, miễn là chiến lược khớp với cấu trúc tài liệu. Trên corpus không đánh số (email, FAQ tự do), lợi thế này sẽ biến mất vì regex tiêu đề sẽ không khớp gì cả.

### Nếu làm lại

- Giảm `chunk_size` xuống khoảng 500–600 để lấy lại điểm Q2 mà vẫn giữ được tiêu đề — bạn Nga đã chứng minh hướng này chạy được.
- Thêm metadata `institution` để agent không trộn quy định hai trường.
- Với câu hỏi đa ý như Q1, tách thành hai truy vấn rồi hợp kết quả; chunk đáp án của tôi ở hạng 4 nên chỉ cần `top_k=5` là cứu được.

**Điều hay nhất tôi học được từ thành viên khác:**
> Bạn Nga chạy cùng thuật toán `HeadingChunker` nhưng chunk ngắn hơn (119 chunk so với 86 của tôi) và **vẫn thắng Q5**. Điều đó trả lời được câu hỏi mà một mình tôi không kiểm chứng được: lợi thế đến từ **việc giữ tiêu đề dính với nội dung**, chứ không phải từ việc chunk dài hơn. Nếu nhóm chỉ có một biến thể `HeadingChunker` thì hai yếu tố này lẫn vào nhau và kết luận sẽ không chắc chắn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |

Tôi để 10/10 phần hướng tiếp cận vì ngoài các TODO bắt buộc, tôi còn thiết kế và giải thích được chiến lược custom `HeadingChunker` cùng lý do cho từng bước — và giả thuyết thiết kế đó được xác nhận bằng số liệu ở Q5.
