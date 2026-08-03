
# BÁO CÁO CÁ NHÂN — LAB 7: EMBEDDING & VECTOR STORE

**Họ tên:** Nguyễn Duy Hải Bằng
**MSSV:** 2A202601225
**Nhóm:** B2
**Ngày:** 03/08/2026

---

## 1. Khởi động

### Cosine similarity

Cosine similarity dùng để đo mức độ giống nhau giữa hai vector. Điểm càng cao thì hai đoạn văn bản càng gần nhau về nội dung.

Ví dụ tương đồng cao:

- “Sinh viên đăng ký học phần trên cổng học vụ.”
- “Việc đăng ký môn học được thực hiện trên hệ thống học vụ.”

Hai câu dùng từ khác nhau nhưng cùng nói về một việc.

Ví dụ tương đồng thấp:

- “Hạn nộp học phí là ngày 30 tháng 9.”
- “Đội bóng của trường thắng trận chung kết.”

Hai câu gần như không liên quan về chủ đề.

Cosine similarity phù hợp với text embedding vì nó quan tâm đến hướng của vector hơn là độ dài. Nhờ vậy, một câu hỏi ngắn vẫn có thể được so sánh với một đoạn tài liệu dài.

### Bài toán chunking

Với tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:

```text
step = 500 - 50 = 450
số chunk = ceil((10000 - 50) / 450) = 23
```

Nếu tăng overlap lên 100:

```text
step = 500 - 100 = 400
số chunk = ceil((10000 - 100) / 400) = 25
```

Overlap lớn hơn giúp hạn chế việc câu hoặc điều khoản bị cắt ngang, nhưng cũng làm tăng số chunk và chi phí tạo embedding.

---

## 2. Cách làm

### `SentenceChunker`

Tôi dùng regex:

```python
r"(?<=[.!?])\s+"
```

để tách câu theo dấu `.`, `!`, `?`. Sau đó loại bỏ phần rỗng và gom các câu theo `max_sentences_per_chunk`.

### `RecursiveChunker`

Chunker này ưu tiên chia theo:

```python
["\n\n", "\n", ". ", " ", ""]
```

Nó cố giữ nguyên đoạn văn và câu trước. Nếu đoạn vẫn quá dài thì mới chia tiếp theo từ hoặc ký tự.

### `EmbeddingStore`

Mỗi tài liệu được lưu gồm:

- `id`
- `content`
- `metadata`
- `embedding`

Khi tìm kiếm, hệ thống tạo embedding cho câu hỏi, tính độ tương tự với các chunk đã lưu, sắp xếp giảm dần rồi lấy `top_k`.

Với `search_with_filter`, tôi lọc metadata trước rồi mới tính similarity. Cách này giúp kết quả đúng đối tượng hơn và giảm số phép tính.

Với `delete_document`, tôi dựng lại danh sách chỉ gồm các chunk có `metadata['doc_id']` khác `doc_id` cần xóa, rồi so độ dài trước và sau để trả về `True` hoặc `False`. Cách này chỉ duyệt một lượt và không cần đếm riêng. `doc_id` luôn tồn tại vì khi lưu, nếu tài liệu không có metadata thì tôi tự gán `doc_id` bằng chính `id` của tài liệu.

### `KnowledgeBaseAgent`

Quy trình trả lời gồm ba bước:

```text
Tìm top-k chunk → đưa chunk vào prompt → gọi LLM
```

Prompt yêu cầu mô hình chỉ trả lời theo context, không tự đoán và ghi rõ context đã sử dụng. Nếu không tìm thấy dữ liệu phù hợp, agent trả về thông báo không có ngữ cảnh liên quan.

---

## 3. Kết quả kiểm thử

Lệnh chạy:

```bash
python -m pytest tests/ -v
```

Kết quả:

```text
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 21%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences            PASSED [ 33%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 40%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string          PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0           PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive     PASSED [ 80%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.10s =============================
```

**Tổng số test vượt qua: 42/42.**

Ngoài ra, `ingest.py` và `main.py` đều chạy được đầy đủ luồng nạp dữ liệu, tìm kiếm và tạo câu trả lời.

---

## 4. Dự đoán độ tương tự

Kết quả chạy bằng `text-embedding-3-small`:

| Cặp | Câu A | Câu B | Dự đoán | Điểm | Kết quả |
| ---- | ------- | ------- | ---------- | -----: | --------- |
| 1 | "Sinh viên đăng ký học phần trong cổng học vụ." | "Việc đăng ký môn học được thực hiện trên cổng thông tin học vụ." | Cao | 0.7047 | Đúng |
| 2 | "Thư viện cho mượn tài liệu và không gian học tập." | "Sinh viên có thể mượn sách và ngồi học tại thư viện." | Cao | 0.5843 | Đúng |
| 3 | "Học phần tiên quyết phải được kiểm tra trước khi đăng ký." | "Cần mang thẻ định danh hợp lệ khi mượn tài liệu." | Thấp | 0.4276 | Đúng |
| 4 | "Hạn nộp học phí của học kỳ này là ngày 30 tháng 9." | "Đội bóng đá của trường thắng trận chung kết hôm qua." | Thấp | 0.2819 | Đúng |
| 5 | "Course registration opens each semester." | "Sinh viên đăng ký học phần theo lịch của từng học kỳ." | Cao | 0.3270 | Sai |

**Kết quả: 4/5 dự đoán đúng.**

Điểm đáng chú ý nhất là cặp tiếng Anh – tiếng Việt dù cùng ý nhưng điểm không cao. Điều này cho thấy ngôn ngữ sử dụng có thể ảnh hưởng đến retrieval. Vì vậy, dữ liệu và câu hỏi nên thống nhất ngôn ngữ hoặc dùng model đa ngữ phù hợp.

Một điểm nữa là điểm số không bao giờ về gần 0. Cặp không liên quan nhất vẫn được 0.2819. Do đó nên đọc điểm theo thứ hạng thay vì đặt ngưỡng tuyệt đối.

---

## 5. Kết quả truy xuất

Cấu hình chạy (đã đồng bộ với `REPORT_NHOM.md`):

- Corpus nhóm: 7 tài liệu công khai, 41.241 ký tự
- Chiến lược của tôi: `RecursiveChunker(chunk_size=500)` → 100 chunk
- 5 câu hỏi benchmark chung của nhóm
- `top_k=3`, embedding `text-embedding-3-small`, `llm_fn` gọi `gpt-4o-mini`

| # | Câu hỏi | Top-1 chunk | Điểm | Liên quan? | Câu trả lời của agent | Điểm chấm |
| -: | --------- | ------------- | -----: | ----------- | ----------------------- | ---------: |
| 1 | Đăng ký học phần bằng hình thức nào, chưa đóng học phí bị xử lý ra sao? | `ueh-dang-ky-huy-hoc-phan::c18` | 0.7253 | Không có trong top-3 | Trả lời theo Điều 6 (nộp phiếu đăng ký) — sai điều khoản | 0 |
| 2 | Hạn nộp học phí HK I và HK II? | `ftu-quy-dinh-thu-nop-hoc-phi::c1` | 0.6741 | Đúng, hạng 1 | "30 tháng 11 và 31 tháng 05" — đúng | 2 |
| 3 | Bước đầu tiên khi mượn tài liệu tự động? | `hanu-muon-tra-tai-lieu::c1` | 0.6269 | Đúng, hạng 2 | "Đưa thẻ vào đầu đọc mã vạch" — đúng | 1 |
| 4 | Ký túc xá đóng cửa và tắt đèn lúc mấy giờ? | `tdtu-noi-tru-ky-tuc-xa::c1` | 0.4945 | Đúng, hạng 2 và 3 | "Đóng cửa 23:00, tắt đèn 22:30" — trộn hai trường | 1 |
| 5 | Điều kiện xét học bổng khuyến khích học tập? | `ueh-hoc-bong-khuyen-khich::c8` | 0.6841 | Không có trong top-3 | Chỉ nêu điều kiện số tín chỉ, thiếu điều kiện chính | 0 |

**Chunk liên quan trong top-3: 3/5. Điểm truy xuất: 4/10.**

So với các thành viên khác trong nhóm (`REPORT_NHOM.md`), chiến lược của tôi thấp nhất: bốn bạn còn lại đều đạt 6/10.

### Vì sao chiến lược của tôi thua

Nguyên nhân chính là `RecursiveChunker` cắt tại `\n\n`, nên tiêu đề bị tách khỏi phần nội dung nằm dưới nó.

Rõ nhất là câu 5. Điều kiện xét học bổng nằm trong danh sách gạch đầu dòng dưới tiêu đề "2.2 Điều kiện để sinh viên tham gia xét học bổng". Chiến lược của tôi cắt rời tiêu đề khỏi danh sách, khiến chunk chứa đáp án tụt xuống hạng 7 trên 100. Chiến lược chunk theo tiêu đề của bạn Việt giữ nguyên cả khối nên chunk đó đứng hạng 1 trên 86.

Câu 3 cũng tương tự: "Bước 1" bị tách khỏi tiêu đề "MƯỢN TÀI LIỆU" nên chỉ đứng hạng 2.

### Lỗi của agent

Đây là phần tôi thấy bất ngờ nhất khi nối LLM thật vào.

Câu 1: agent trả lời rằng sinh viên đăng ký bằng cách nộp "Phiếu đăng ký học phần". Câu này **có thật trong tài liệu**, nhưng thuộc Điều 6 nói về trường hợp đăng ký đặc biệt, còn hình thức chung là đăng ký trực tuyến ở Điều 2. Agent không bịa, nó trả lời trung thực theo đúng chunk được đưa vào — nhưng chunk đó sai điều khoản. Retrieval sai thì agent trả lời sai theo, dù vẫn có căn cứ.

Câu 4: agent trả lời "đóng cửa 23:00 và tắt đèn 22:30". Hai con số này lấy từ **hai trường khác nhau** (IUBH đóng cửa 23h00, TDTU tắt đèn 22:30). Đây là hậu quả của việc corpus gom quy định của nhiều trường mà không có trường metadata phân biệt.

Bài học: chunk có mặt trong top-3 chưa đủ. Nếu chunk hơi lệch chủ đề hoặc đến từ tài liệu khác nguồn thì agent vẫn trả lời sai một cách rất thuyết phục.

### Nếu làm lại

- Đổi sang chunk theo tiêu đề, hoặc ít nhất giữ dòng tiêu đề vào đầu mỗi chunk.
- Tăng `top_k` lên 10 — chunk đúng của câu 1 nằm hạng 8 nên `top_k=5` vẫn không với tới. Với chiến lược chunk theo tiêu đề (hạng 4) thì `top_k=5` là đủ.
- Thêm trường metadata cho tên trường để agent không trộn quy định của hai nơi.

**Điều hay nhất tôi học được từ thành viên khác:**

Cùng một corpus và cùng một bộ câu hỏi, chỉ đổi cách cắt chunk mà điểm chênh từ 4/10 lên 6/10. Bạn Việt và bạn Nga cùng dùng chunk theo tiêu đề nhưng khác tham số, và bạn Tiến dùng `SentenceChunker` vẫn đạt 6/10 — cho thấy không có chiến lược nào thắng ở mọi câu hỏi. Điều tôi học được rõ nhất là phải chọn chiến lược theo dạng câu hỏi mà người dùng hay hỏi, chứ không phải chọn chiến lược "tốt nhất" chung chung.

---

## 6. Tự đánh giá

| Tiêu chí                  |          Điểm |
| --------------------------- | --------------: |
| Khởi động                |             5/5 |
| Hướng tiếp cận          |            9/10 |
| Hoàn thiện code           |           30/30 |
| Dự đoán độ tương tự |             5/5 |
| Kết quả truy xuất        |            4/10 |
| **Tổng**             | **53/60** |

Tôi trừ 1 điểm phần hướng tiếp cận vì chưa kiểm thử trực tiếp nhánh ChromaDB (máy không cài gói này nên toàn bộ chạy trên nhánh in-memory).

Phần truy xuất tôi chấm đúng điểm chạy thật là 4/10. Điểm này thấp hơn các bạn trong nhóm, nhưng tôi giữ nguyên thay vì đổi sang chiến lược tốt hơn, vì phần phân tích nguyên nhân thua mới là thứ tôi học được nhiều nhất.
