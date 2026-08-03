# REPORT CÁ NHÂN — Lab 07
## K3: Nền Tảng Dữ Liệu, Embedding & Vector Store

**Họ và tên:** Tạ Thị Nga
**MSSV:** 2A202601125
**Ngày thực hiện:** 2026-08-03
**Nhóm:** B2

> *Ghi chú khi tổng hợp:* Báo cáo giữ nguyên khung do bạn dựng. Ba chỗ mô tả code ở Phần 2 đã được **sửa lại cho khớp với `NguyenDuyHaiBang_2A202601225/` thật** (ghi rõ ở từng mục). Phần 4 thay số `MockEmbedder` bằng số chạy thật với `text-embedding-3-small`. Phần 5 đã điền hết các ô `[CẦN TÔI XEM LẠI]` bằng số liệu chạy thật của chiến lược `HeadingChunker(500, min=200)`.

---

## Phần 1 — Khởi động

### Bài 1.1 — Cosine Similarity bằng ngôn ngữ đời thường

**Điều gì xảy ra khi hai đoạn văn bản có cosine similarity cao?**

Khi hai đoạn văn bản có cosine similarity cao, có nghĩa là chúng nói về cùng một chủ đề hoặc truyền đạt ý nghĩa tương tự nhau, dù cách dùng từ có thể khác nhau. Hệ thống embedding "hiểu" rằng hai đoạn này đang nói về cùng một thứ và đặt chúng gần nhau trong không gian vector. Trong hệ thống RAG, đây là cơ sở để tìm ra đoạn văn bản phù hợp nhất với câu hỏi của người dùng.

**Ví dụ cụ thể:**

- **Độ tương tự CAO:** "Sinh viên cần đóng học phí trước ngày 15 mỗi tháng." và "Hạn nộp tiền học phí là ngày 15 hàng tháng." — Hai câu này diễn đạt khác nhau nhưng cùng ý nghĩa về thời hạn đóng học phí.
- **Độ tương tự THẤP:** "Quy trình đăng ký học phần bắt đầu vào tuần đầu mỗi học kỳ." và "Hôm nay thời tiết Hà Nội nắng đẹp và nhiệt độ khoảng 32 độ." — Hai câu này hoàn toàn không liên quan nhau về chủ đề.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance?**

Euclidean distance đo khoảng cách tuyệt đối giữa hai điểm trong không gian, nên nó bị ảnh hưởng bởi độ dài của vector. Một đoạn văn bản dài sẽ tạo ra vector có magnitude lớn hơn đoạn ngắn, khiến chúng "xa nhau" về mặt Euclidean dù nói cùng một chủ đề. Cosine similarity chỉ đo góc giữa hai vector — tức là đo *hướng*, không đo *độ dài* — nên không bị ảnh hưởng bởi việc văn bản dài hay ngắn.

---

### Bài 1.2 — Bài toán tính toán Chunking

**Đề bài:** Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`.

**Công thức:**

```
số chunk = ceil((độ_dài_tài_liệu - overlap) / (chunk_size - overlap))
```

**Tính với `overlap=50`:**

```
số chunk = ceil((10000 - 50) / (500 - 50))
         = ceil(9950 / 450)
         = ceil(22.11...)
         = 23 chunks
```

**Tính lại với `overlap=100`:**

```
số chunk = ceil((10000 - 100) / (500 - 100))
         = ceil(9900 / 400)
         = ceil(24.75)
         = 25 chunks
```

**Kiểm chứng bằng code:** chạy `FixedSizeChunker(chunk_size=500, overlap=50)` trên chuỗi 10.000 ký tự cho đúng 23 chunk — vị trí bắt đầu chạy 0, 450, 900, …, 9900, chunk cuối chỉ còn 100 ký tự.

**So sánh:** Tăng `overlap` từ 50 → 100 làm tăng số chunk từ 23 lên 25, tức là tốn thêm bộ nhớ và thời gian xử lý. Lý do muốn tăng overlap là để mỗi cặp chunk liền kề có đoạn nội dung dùng chung nhiều hơn, giúp tránh trường hợp một câu quan trọng bị cắt đúng ở ranh giới giữa hai chunk. Đây là sự đánh đổi giữa chi phí lưu trữ và chất lượng truy xuất.

---

## Phần 2 — Hướng tiếp cận của tôi

### 2.1 `compute_similarity` — `NguyenDuyHaiBang_2A202601225/chunking.py` dòng 129–141

**Thuật toán:** Tính cosine similarity theo công thức `dot(a, b) / (||a|| × ||b||)`. Dùng hàm `_dot()` có sẵn để tính tích vô hướng, sau đó tính norm của từng vector bằng `math.sqrt(_dot(v, v))`.

**Quyết định thiết kế đáng nói nhất:** Kiểm tra `norm == 0.0` trước khi chia. Nếu một trong hai vector là vector không, hàm trả về `0.0` thay vì raise `ZeroDivisionError`. Điều này quan trọng vì một đoạn văn bản rỗng hoặc toàn whitespace có thể tạo ra zero vector sau khi nhúng.

**Hạn chế đã biết:** So sánh `== 0.0` với số thực có thể gặp vấn đề floating-point với vector gần không nhưng không bằng không chính xác; một ngưỡng epsilon nhỏ (ví dụ `< 1e-10`) sẽ an toàn hơn.

---

### 2.2 `SentenceChunker` — `NguyenDuyHaiBang_2A202601225/chunking.py` dòng 38–63

**Thuật toán:** Dùng `re.compile(r"(?<=[.!?])\s+")` để tách câu. Pattern này là **lookbehind assertion**: nó tách tại vị trí *sau* dấu câu và whitespace, nên dấu câu vẫn gắn liền với câu trước thay vì bị mất. Sau đó `strip()` từng câu, bỏ phần tử rỗng, rồi gom từng nhóm `max_sentences_per_chunk` câu bằng `" ".join(group)`.

**Quyết định thiết kế đáng nói nhất:** Dùng lookbehind thay vì split trực tiếp theo `.` giúp giữ nguyên dấu câu trong output. Ngoài ra `\s+` bắt được cả `". "`, `"! "`, `"? "` lẫn `".\n"` chỉ bằng một mẫu duy nhất, thay vì phải liệt kê bốn trường hợp.

**Hạn chế đã biết:** Pattern có thể tách sai ở các từ viết tắt có dấu chấm (ví dụ `"TS. Nguyễn"`, `"e.g. this"`). Với corpus K3 thì hạn chế này lộ rõ ở một dạng khác: văn bản hành chính dùng nhiều dòng đánh số **không kết thúc bằng dấu chấm** ("+ Học kỳ I: …"), nên bộ tách câu không thấy ranh giới và dồn chúng thành khối lớn.

---

### 2.3 `RecursiveChunker` — `NguyenDuyHaiBang_2A202601225/chunking.py` dòng 65–122

> ⚠️ *Đã sửa so với bản nháp:* bản nháp mô tả bước "re-attach separator (`pieces.append(part + separator)`)" và một "merge pass" chạy sau. Mã nguồn thật **không làm như vậy**.

**Thuật toán thật:** `chunk()` chặn text rỗng rồi ủy quyền cho `_split(text, separators)`. `_split` có ba base case: text rỗng → `[]`; `len(text) <= chunk_size` → trả nguyên khối; hết separator hoặc gặp separator `""` → cắt cứng theo ký tự bằng `_hard_split` (dòng 120). Ở bước đệ quy, nếu separator không xuất hiện trong text (`len(parts) == 1`) thì **tụt xuống separator kế tiếp** thay vì trả về đoạn quá khổ. Việc gom là **greedy trong một lượt duy nhất**, không có merge pass riêng: dồn các mảnh vào một buffer bằng `buffer + separator + part` chừng nào còn `<= chunk_size`; mảnh nào tự nó đã quá to thì đệ quy tiếp với danh sách separator còn lại.

**Quyết định thiết kế đáng nói nhất:** Separator được **nối lại khi gộp** (`buffer + separator + part`) chứ không gắn vào từng mảnh ngay sau khi split. Nhờ vậy văn bản trong chunk trung thực với input, mà không sinh separator thừa ở cuối chunk.

**Hạn chế đã biết:** Gom greedy một lượt không tối ưu toàn cục, nên phân phối độ dài chunk có thể không đều. Với corpus K3, hạn chế nghiêm trọng hơn là việc cắt tại `\n\n` **tách tiêu đề khỏi danh sách nội dung bên dưới** — chính là nguyên nhân chiến lược này đạt điểm thấp nhất nhóm (xem Phần 5 và `REPORT_NHOM.md`).

---

### 2.4 `ChunkingStrategyComparator` — `NguyenDuyHaiBang_2A202601225/chunking.py` dòng 144–163

> ⚠️ *Đã sửa so với bản nháp:* bản nháp mô tả một heuristic quy đổi `max_sentences = chunk_size // avg_sentence_len`. Mã nguồn thật **không có** heuristic này.

**Thuật toán thật:** Chạy cả ba chunker trên cùng văn bản: `FixedSizeChunker(chunk_size, overlap=chunk_size // 10)`, `SentenceChunker(max_sentences_per_chunk=3)` — cố định 3 câu, không quy đổi từ `chunk_size` — và `RecursiveChunker(chunk_size)`. Trả về dict ba khóa `fixed_size` / `by_sentences` / `recursive`, mỗi entry gồm `count`, `avg_length`, `chunks`.

**Quyết định thiết kế đáng nói nhất:** `overlap` của `FixedSizeChunker` được suy ra từ `chunk_size` (10%) thay vì để mặc định 50, để khi gọi `compare()` với `chunk_size` nhỏ thì overlap không vượt quá kích thước chunk.

**Hạn chế đã biết:** Vì `SentenceChunker` cố định 3 câu/chunk còn hai chunker kia dùng `chunk_size` theo ký tự, ba chiến lược **không thực sự cùng một mốc so sánh**. Đây là lý do bảng baseline chỉ nên dùng để quan sát xu hướng, không dùng để kết luận chiến lược nào tốt hơn — kết luận đó phải dựa vào benchmark truy xuất ở Phần 5.

---

### 2.5 `EmbeddingStore` — `NguyenDuyHaiBang_2A202601225/store.py`

**Thuật toán:** Lưu trữ in-memory bằng list `self._store`. Mỗi record là dict `{id, content, metadata, embedding}`. Embedding được tính **một lần khi add**. `search()` nhúng câu hỏi rồi tính dot product với toàn bộ embedding đã lưu — vì backend trả vector đã chuẩn hóa nên dot product bằng đúng cosine — sort giảm dần, lấy top-k. `search_with_filter()` tái sử dụng helper `_search_records()` sau khi đã lọc theo `metadata_filter`.

**Quyết định thiết kế đáng nói nhất:** Lưu `doc_id` vào **trong** `metadata` của record (mặc định bằng `doc.id` nếu tài liệu không có metadata). Điều này cho phép `delete_document()` lọc chính xác bằng `metadata['doc_id']` kể cả với `Document` không kèm metadata.

**Hạn chế đã biết:** In-memory store không persist qua các lần chạy, và tìm kiếm là O(n). Ngoài ra nhánh ChromaDB tuy có được khởi tạo và ghi song song, nhưng `search()` / `search_with_filter()` **luôn** xếp hạng trên `self._store` — nên trên thực tế nhánh Chroma hiện chưa được sử dụng.

---

### 2.6 `KnowledgeBaseAgent` — `NguyenDuyHaiBang_2A202601225/agent.py`

> ⚠️ *Đã sửa so với bản nháp:* bản nháp ghi "không xử lý trường hợp store rỗng — prompt vẫn được gửi đi". Mã nguồn thật **có** xử lý.

**Thuật toán thật:** Pipeline RAG 3 bước — **(1) Retrieve** `store.search(question, top_k)`; **(2) Build prompt** với phần `Context:` chứa các chunk đánh số `[1] [2] [3]` kèm `score` và nguồn (`source_url`, lùi về `source`/`doc_id` qua helper `_source_of`); **(3) Generate** gọi `llm_fn(prompt)`.

**Quyết định thiết kế đáng nói nhất:** Nếu không truy xuất được chunk nào, hàm trả về hằng `NO_CONTEXT_ANSWER` (`NguyenDuyHaiBang_2A202601225/agent.py` dòng 16) và **không gọi LLM** — tránh tốn một lần gọi mà chắc chắn sẽ bịa. Prompt cũng ràng buộc ba điều: chỉ trả lời dựa trên ngữ cảnh, nói thẳng khi ngữ cảnh không chứa đáp án, và trích số hiệu context đã dùng.

**Hạn chế đã biết (thực tế đã xảy ra):** Cơ chế chống bịa chỉ chặn được trường hợp **không có** ngữ cảnh. Nó không chặn được trường hợp ngữ cảnh **có nhưng sai** — xem Q1 và Q4 ở Phần 5, nơi agent trả lời rất thuyết phục dựa trên chunk sai điều khoản hoặc sai trường.

---

## Phần 3 — Kết quả kiểm thử

```bash
python -m pytest tests/ -v
```

```text
============================= 42 passed in 0.21s =============================
```

**Số lượng bài test vượt qua: 42 / 42**

---

## Phần 4 — Dự đoán độ tương tự (Bài 3.3)

> *Đã thay số:* bản nháp dùng `MockEmbedder` (hash MD5, không mang ngữ nghĩa). Bảng dưới chạy bằng **`text-embedding-3-small`** — cùng embedder với benchmark nhóm, nên kết quả mới có ý nghĩa để suy luận.

Chủ đề tôi chọn: học bổng — cùng mảng với câu hỏi Q5 mà chiến lược của tôi thắng.

| # | Loại cặp | Câu A | Câu B | Dự đoán | Thực tế | Đúng? |
|---|---|---|---|---|---:|---|
| 1 | Rõ ràng giống | "Học bổng khuyến khích học tập cấp cho sinh viên có kết quả tốt." | "Sinh viên đạt thành tích cao được nhận học bổng." | Cao | **0.6980** | Đúng |
| 2 | Paraphrase sát nghĩa | "Kết quả học tập từ loại khá trở lên." | "Điểm trung bình đạt mức khá hoặc cao hơn." | Cao | **0.4561** | **Sai** |
| 3 | Diễn đạt lại có số | "Học bổng loại giỏi bằng 1,2 lần mức học bổng loại khá." | "Mức học bổng giỏi cao hơn mức khá 20 phần trăm." | Cao | **0.7319** | Đúng |
| 4 | Rõ ràng khác | "Sinh viên bị kỷ luật không được xét học bổng." | "Máy mượn tự động có tia laser màu đỏ." | Thấp | **0.2561** | Đúng |
| 5 | Khác ngôn ngữ, cùng ý | "Scholarship requires good academic results." | "Học bổng yêu cầu kết quả học tập tốt." | Cao | **0.4473** | **Sai** |

**Kết quả: 3/5 dự đoán đúng.**

**Điều khiến tôi ngạc nhiên nhất:**

Cặp 2. Hai câu gần như đồng nghĩa hoàn toàn ("từ loại khá trở lên" và "đạt mức khá hoặc cao hơn") mà chỉ được **0.4561**, thấp hơn hẳn cặp 3 (**0.7319**) vốn diễn đạt lệch nhau nhiều hơn (còn đổi cả "1,2 lần" thành "20 phần trăm"). Khác biệt nằm ở **độ dài và mật độ thông tin**: hai câu ở cặp 2 rất ngắn và gần như chỉ có một khái niệm, nên một thay đổi từ vựng nhỏ đã làm lệch hướng vector đáng kể; còn cặp 3 dài hơn, có nhiều thực thể trùng nhau ("học bổng", "loại giỏi", "loại khá") nên vector ổn định hơn.

Điều này rất liên quan tới chiến lược chunking của tôi: chunk **quá ngắn thì vector dễ bị nhiễu**, chunk có đủ ngữ cảnh thì điểm ổn định hơn. Đó là lý do tôi đặt `min_chunk_size=200` để gộp các mục quá ngắn thay vì để chúng đứng riêng.

Điểm thứ hai: cặp 5 (Anh–Việt cùng ý) chỉ đạt **0.4473**, thấp hơn cặp 3 cùng tiếng Việt. Kết quả này khớp với bạn Bằng (0.3270) nhưng khác bạn Tâm (0.5533) — cho thấy khả năng liên kết chéo ngôn ngữ của model là **có nhưng không ổn định**, phụ thuộc độ song song của câu. Không nên dựa vào nó khi thiết kế corpus.

---

## Phần 5 — Kết quả truy xuất của tôi (Bài 3.4)

> **Embedder:** `text-embedding-3-small` (OpenAI, `EMBEDDING_PROVIDER=openai`), 1536 chiều.
> **Agent:** `llm_fn` gọi `gpt-4o-mini`, temperature 0.
> Toàn bộ số liệu dưới đây là **lần chạy thật của chiến lược tôi phụ trách** trên corpus nhóm 7 tài liệu.

### Chiến lược tôi chọn

- **Chunker:** `HeadingChunker(chunk_size=500, min_chunk_size=200)` — custom (xem `NguyenDuyHaiBang_2A202601225/custom_chunkers.py`)
- **Tổng số chunk:** **119** — nhiều nhất nhóm
- **Lý do chọn:** Corpus K3 là văn bản quy định, gần như luôn đánh số theo `Điều N / Mục N / I)`. Mỗi điều khoản là một đơn vị ngữ nghĩa trọn vẹn. Tôi chọn tham số **chunk ngắn (500)** thay vì 900 như bạn Việt để trả lời một câu hỏi cụ thể của nhóm: *lợi thế của chiến lược này đến từ việc giữ tiêu đề, hay chỉ đến từ việc chunk dài hơn?*
- **Có dùng metadata_filter không?** Có — Q5 chạy kèm `metadata_filter={"audience": "student"}`.

### Kết quả top-1 và điểm từng câu

| # | Câu hỏi | Top-1 chunk | Score | Hạng của chunk chứa đáp án | Agent trả lời | Điểm |
|---:|---|---|---:|---|---|---:|
| 1 | Đăng ký học phần + xử lý chưa đóng học phí | `ueh-dang-ky-huy-hoc-phan::chunk_12` | 0.6649 | ngoài top-3 | Trả lời theo Điều 6 (nộp phiếu) — sai điều khoản | **0** |
| 2 | Hạn nộp học phí HK I / HK II | `ftu-quy-dinh-thu-nop-hoc-phi::chunk_1` | 0.6684 | **hạng 1** | "30 tháng 11 và 31 tháng 05" — đúng | **2** |
| 3 | Bước đầu tiên khi mượn tài liệu | `hanu-muon-tra-tai-lieu::chunk_1` | 0.5936 | hạng 2 | "Đưa thẻ vào đầu đọc mã vạch" — đúng | **1** |
| 4 | Giờ đóng cửa / tắt đèn ký túc xá | `iubh-noi-quy-ky-tuc-xa::chunk_1` | 0.5394 | hạng 1 và 3 | "Đóng cửa 23h00, tắt đèn 22h30" — trộn hai trường | **1** |
| 5 | Điều kiện xét học bổng *(có filter)* | `ueh-hoc-bong-khuyen-khich::chunk_11` | 0.6616 | **hạng 1** | Nêu đúng "loại khá trở lên" + phân biệt mức khá/giỏi | **2** |

**Tổng: 6/10. Chunk liên quan trong top-3: 4/5.**

### Nhận xét cá nhân

**Câu tốt nhất — Q2 và Q5, mỗi câu 2/2 điểm.** Đây chính là điều tôi muốn kiểm chứng: chiến lược của tôi vừa thắng Q2 (câu cần mốc số, vốn là thế mạnh của chunk ngắn) **vừa** thắng Q5 (câu tra cứu điều khoản, vốn là thế mạnh của chunk theo tiêu đề). Bạn Việt dùng `HeadingChunker(900)` thắng Q5 nhưng thua Q2 (chỉ 1đ, tụt hạng 3) vì chunk 789 ký tự làm loãng hai con số ngày tháng.

**Kết luận từ thí nghiệm có kiểm soát:** `Heading500` của tôi có **119 chunk**, `Heading900` của bạn Việt có **86 chunk** — chênh lệch lớn về độ dài, nhưng **cả hai đều thắng Q5**, trong khi `RecursiveChunker(500)` của bạn Bằng cùng cỡ chunk lại tụt xuống hạng 7/100. Vậy lợi thế đến từ **việc giữ dòng tiêu đề dính với nội dung**, không phải từ độ dài chunk. Đây là câu trả lời mà nhóm không tách bạch được nếu chỉ chạy một biến thể `HeadingChunker`.

**Câu kém nhất — Q1 (0 điểm).** Không phải lỗi chunking: câu hỏi hỏi hai ý cùng lúc nên vector bị pha loãng giữa hai chủ đề. Với `HeadingChunker(900)`, chunk đáp án nằm hạng 4; với chiến lược của tôi thì rơi ra ngoài top-3.

**Q3 chỉ được 1 điểm** vì `min_chunk_size=200` gộp tiêu đề "MƯỢN TÀI LIỆU" vào một chunk khác, làm giảm trọng số của từ "mượn". Đây là mặt trái của tham số mà tôi chọn: gộp mục ngắn giúp vector ổn định (xem Phần 4) nhưng có thể làm mất ranh giới tiêu đề mà chính chiến lược này dựa vào.

**Metadata filtering có giúp ích không?** Với Q5 (`audience=student`): top-3 **không đổi** so với khi không lọc, vì corpus chỉ có 1 tài liệu học bổng và nó đã áp đảo — bộ lọc chỉ đóng vai trò bảo hiểm. Nhóm phải thử thêm một câu hỏi ngoài benchmark ("Phải xuất trình thẻ sinh viên khi nào?") mới đo được giá trị thật của bộ lọc: không lọc thì top-3 toàn tài liệu học phí, lọc `audience=all` thì tài liệu thư viện đúng lên hạng 1 dù điểm thấp hơn. Nguyên nhân Q5 không đo được là **6/7 tài liệu đều có `audience=student`**, nên bộ lọc đó không phân biệt được gì.

**Nếu làm lại, tôi sẽ thay đổi gì?**
1. Thêm trường `institution` vào metadata để phân biệt quy định từng trường — giải quyết lỗi Q4 mà **cả 5 thành viên đều mắc**.
2. Tăng `top_k` từ 3 lên 5 cho các chiến lược có chunk đáp án ở hạng 4–6; riêng chiến lược của tôi ở Q1 thì cần hơn thế.
3. Tách câu hỏi đa ý (Q1) thành hai truy vấn đơn rồi hợp kết quả.
4. Bổ sung tài liệu có `audience=faculty` hoặc `staff` để bộ lọc `audience` có ý nghĩa thực sự, đúng tinh thần yêu cầu K3.

---

## Tự đánh giá

| Tiêu chí | Điểm |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận | 9 / 10 |
| Hoàn thiện code (tests) | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất | 6 / 10 |
| **Tổng** | **55 / 60** |

Trừ 1 điểm phần hướng tiếp cận vì nhánh ChromaDB chưa thực sự được `search` sử dụng.
