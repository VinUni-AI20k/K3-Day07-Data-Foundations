# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

> Ghi chú audit 2026-08-03: các bảng dùng mock ở mục 4–5 được giữ như baseline lịch sử, không dùng kết luận semantic. Kết quả chính thức bằng local multilingual embedding nằm ở mục 6.

**Họ tên:** Diêm Công Thành
**Mã học viên:** 2A202601689
**Nhóm:** B1-3
**Vai trò trong nhóm:** Thành viên
**Ngày:** 2026-08-03

## 1. Khởi động (Warm-up)

### Độ tương tự Cosine

Độ tương tự cosine cao nghĩa là hai vector embedding cùng hướng hoặc gần cùng hướng, nên hai đoạn văn bản thường nói về nội dung giống nhau dù độ dài câu khác nhau. Điểm gần 1 là rất giống, gần 0 là ít liên quan, và âm là hướng biểu diễn trái ngược.

**Ví dụ độ tương tự cao:**
- Câu A: Sinh viên đăng ký học phần trên cổng học vụ.
- Câu B: Sinh viên xác nhận môn học qua hệ thống đăng ký học phần.
- Tương đồng vì cả hai đều nói về thao tác đăng ký học phần của sinh viên.

**Ví dụ độ tương tự thấp:**
- Câu A: Thư viện cho phép sinh viên mượn sách.
- Câu B: Thời tiết hôm nay có mưa lớn.
- Khác vì một câu nói về dịch vụ thư viện, câu còn lại nói về thời tiết.

Cosine similarity thường phù hợp hơn khoảng cách Euclid cho text embeddings vì nó tập trung vào hướng ngữ nghĩa của vector, ít bị ảnh hưởng bởi độ lớn vector. Với văn bản, hướng vector thường quan trọng hơn độ dài tuyệt đối.

### Bài toán tính toán Chunking

Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks`.

Nếu tăng overlap lên 100:

`ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks`.

Số chunk tăng vì mỗi bước trượt ngắn hơn. Overlap cao hơn giúp giữ ngữ cảnh giữa hai chunk liền kề, nhất là khi câu trả lời nằm gần ranh giới cắt.

## 2. Hướng tiếp cận của tôi

Trong nhóm, tôi phụ trách thu thập và làm sạch nhóm tài liệu liên quan đến học phí, học bổng, đồng thời thử chiến lược `FixedSizeChunker(chunk_size=450, overlap=50)` làm baseline. Tôi phối hợp với Khoa để kiểm tra code core và với Huy để thống nhất bộ câu hỏi benchmark.

**`SentenceChunker.chunk`:** Tôi kiểm tra cách tách câu bằng regex tại các dấu `.`, `!`, `?` và xuống dòng sau dấu chấm. Cách này giúp nhóm có baseline chunk theo câu để so sánh với fixed-size.

**`RecursiveChunker.chunk` / `_split`:** Tôi dùng kết quả recursive của nhóm làm mốc so sánh với fixed-size. Recursive ưu tiên tách theo đoạn/câu, còn fixed-size của tôi kiểm tra xem overlap có đủ giữ ngữ cảnh ở biên chunk hay không.

**`EmbeddingStore`:** Store lưu in-memory các record gồm `id`, `content`, `metadata`, `embedding` và index. Khi tìm kiếm, query được embed rồi tính dot product với từng embedding, sau đó sắp xếp giảm dần theo score.

**`search_with_filter` và `delete_document`:** Metadata được lọc trước khi tính similarity để giảm nhiễu và hỗ trợ các câu hỏi cần scope rõ ràng. Tôi chú ý nhất tới filter `category=tuition` và `category=scholarship` vì đây là hai nhóm tài liệu tôi phụ trách.

**`KnowledgeBaseAgent.answer`:** Agent lấy top-k chunk từ store, dựng prompt gồm câu hỏi, các chunk truy xuất, nguồn và score. Sau đó agent gọi `llm_fn(prompt)` để tạo câu trả lời dựa trên ngữ cảnh truy xuất.

## 3. Hoàn thiện code

Kết quả kiểm thử:

```text
pytest tests/ -v
collected 42 items
42 passed in 0.05s
```

**Số lượng bài test vượt qua:** 42 / 42

## 4. Dự đoán độ tương tự

Các điểm thực tế dùng `compute_similarity(_mock_embed(A), _mock_embed(B))`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần trên cổng học vụ. | Sinh viên xác nhận môn học qua hệ thống đăng ký học phần. | cao | 0.2186 | Có |
| 2 | Thư viện cho phép sinh viên mượn sách. | Ký túc xá gửi kết quả đăng ký qua email. | thấp | -0.1051 | Có |
| 3 | Học bổng BCU có mức 3.500.000 đồng cho sinh viên đứng đầu. | Sinh viên xếp hạng cao có thể nhận học bổng chương trình BCU. | cao | -0.2061 | Không |
| 4 | Sinh viên phải đóng bảo hiểm y tế năm 2026. | Mức đóng BHYT của sinh viên là 631.800 đồng. | cao | -0.2832 | Không |
| 5 | Python là ngôn ngữ lập trình. | Thời tiết hôm nay có mưa lớn. | thấp | -0.0651 | Có |

Kết quả bất ngờ nhất là cặp học bổng có điểm âm dù hai câu cùng nói về BCU và học bổng. Điều này cho thấy mock embedder chỉ tạo vector ổn định để test kỹ thuật, không đủ để đánh giá chất lượng ngữ nghĩa tiếng Việt.

## 5. Kết quả truy xuất của tôi

Chiến lược cá nhân của tôi dùng `FixedSizeChunker(chunk_size=450, overlap=50)` và mock embedder. Tôi chọn fixed-size để có baseline đơn giản, dễ so sánh với recursive và sentence chunking.

| # | Câu hỏi | Top-1 Chunk truy xuất được | Score | Relevant | Câu trả lời Agent tóm tắt |
|---|-------|-----------------------------|-------|----------|---------------------------|
| 1 | Sinh viên xác nhận đăng ký học phần ở hệ thống nào? | `k3-course-registration::chunk_0` về quy trình đăng ký học phần | 0.2597 | Có | Sinh viên xác nhận trên `dkhp.uit.edu.vn`. |
| 2 | Sinh viên được gia hạn học phí phải hoàn thành trước ngày nào? | `k3-tuition-extension::chunk_1` về thời gian đăng ký và theo dõi đơn | 0.1260 | Có, chi tiết hạn nằm trong nhóm chunk học phí | Trước ngày 17/04/2026. |
| 3 | Học bổng BCU cho sinh viên đứng đầu là bao nhiêu? | `k3-bcu-scholarship-2026::chunk_0` về học bổng BCU | 0.3333 | Có | Mức 3.500.000 đồng. |
| 4 | Tân sinh viên đăng ký ký túc xá trong bao nhiêu ngày sau nhập học? | `k3-dormitory-registration::chunk_1` về phản hồi và thủ tục KTX | 0.1246 | Có | Trong 07 ngày kể từ ngày hoàn tất thủ tục nhập học. |
| 5 | Sinh viên phải đóng bao nhiêu tiền bảo hiểm y tế năm 2026? | `k3-health-insurance-2026::chunk_2` về theo dõi hướng dẫn BHYT | 0.0453 | Có, chi tiết mức tiền ở top-3 | Sinh viên đóng 631.800 đồng. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

Điều tôi học được từ phần của Trương Đình Khoa là recursive chunking giữ ranh giới đoạn tốt hơn fixed-size khi văn bản có cấu trúc rõ. Từ phần của Nguyễn Quang Huy, tôi thấy sentence chunking hữu ích khi cần đọc và giải thích từng chunk cho báo cáo.

## Tự Đánh Giá

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 9 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán độ tương tự | 4 / 5 |
| Kết quả truy xuất của tôi | 8 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |

## 6. Benchmark semantic chính thức

- Strategy: `S2_FIXED_450_50`, `chunk_size=450`, `overlap=50`, top_k=3.
- Corpus chung: 6 tài liệu, 17 chunks.
- Backend: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 chiều, không fallback.
- Python: 3.11.15; 42/42 test pass trong 0.08s.

| Query | Top-1 đúng | Top-3 evidence | Rank đúng | Score evidence |
|---|---:|---:|---:|---:|
| Q1 | 1 | 1 | 1 | 0.679393 |
| Q2 | 0 | 1 | 2 | 0.702119 |
| Q3 | 1 | 1 | 1 | 0.816587 |
| Q4 | 1 | 1 | 1 | 0.778972 |
| Q5 | 0 | 1 | 2 | 0.634148 |

| Hit@1 | Hit@3 | MRR | Precision@3 | Coherence | Grounding |
|---:|---:|---:|---:|---:|---:|
| 0.6000 | 1.0000 | **0.8000** | 0.3333 | 1.0000 | 1.6000 |

Failure Top-1: Q2 và Q5 đúng ở rank 2. Overlap giúp không mất evidence nhưng tạo các chunk gần nhau cạnh tranh; fixed-size cũng có thể cắt giữa câu nên coherence thấp hơn hai strategy còn lại. Hướng cải thiện là giảm overlap có kiểm soát hoặc rerank theo ngày/số tiền.

Bằng chứng chi tiết: `evaluation/benchmark_results.json` và `evaluation/benchmark_summary.md`.
