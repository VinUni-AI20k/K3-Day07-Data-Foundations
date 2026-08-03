# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Quang Huy
**Mã học viên:** 2A202601873
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

Trong nhóm, tôi phụ trách thu thập và làm sạch nhóm tài liệu về thư viện, ký túc xá và bảo hiểm y tế, đồng thời thử chiến lược `SentenceChunker(max_sentences_per_chunk=3)`. Mục tiêu của tôi là kiểm tra xem chunk theo câu có giúp kết quả retrieval dễ đọc và dễ truy vết hơn không.

**`SentenceChunker.chunk`:** Tôi tập trung vào chiến lược tách theo câu vì tài liệu dịch vụ sinh viên thường được viết thành các câu hướng dẫn rõ. Hàm tách câu bằng regex, bỏ khoảng trắng thừa và gom 3 câu mỗi chunk để giữ ngữ cảnh vừa đủ.

**`RecursiveChunker.chunk` / `_split`:** Tôi so sánh sentence chunking với recursive của Khoa để xem chiến lược nào giữ ngữ cảnh tốt hơn. Recursive linh hoạt hơn khi văn bản có đoạn dài, còn sentence chunking dễ đọc hơn khi câu ngắn và rõ ràng.

**`EmbeddingStore`:** Store lưu in-memory các record gồm `id`, `content`, `metadata`, `embedding` và index. Khi tìm kiếm, query được embed rồi tính dot product với từng embedding, sau đó sắp xếp giảm dần theo score.

**`search_with_filter` và `delete_document`:** Metadata được lọc trước khi tính similarity để giảm nhiễu và hỗ trợ các câu hỏi cần scope rõ ràng. Tôi chú ý tới `category=dormitory`, `category=library-services` và `category=health-insurance` vì đây là nhóm tài liệu tôi phụ trách.

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

Kết quả bất ngờ nhất là cặp bảo hiểm y tế có điểm âm dù hai câu có cùng chủ đề. Điều này cho thấy muốn đánh giá retrieval tiếng Việt có ý nghĩa thì nhóm nên dùng local multilingual embedder thay vì mock embedder.

## 5. Kết quả truy xuất của tôi

Chiến lược cá nhân của tôi dùng `SentenceChunker(max_sentences_per_chunk=3)` và mock embedder. Tôi chọn chiến lược này vì các tài liệu dịch vụ sinh viên thường gồm những câu ngắn, mỗi câu chứa một điều kiện hoặc mốc thời gian cụ thể.

| # | Câu hỏi | Top-1 Chunk truy xuất được | Score | Relevant | Câu trả lời Agent tóm tắt |
|---|-------|-----------------------------|-------|----------|---------------------------|
| 1 | Sinh viên xác nhận đăng ký học phần ở hệ thống nào? | `k3-course-registration::chunk_1` về xác nhận đăng ký học phần | 0.0769 | Có | Sinh viên xác nhận trên `dkhp.uit.edu.vn`. |
| 2 | Sinh viên được gia hạn học phí phải hoàn thành trước ngày nào? | `k3-tuition-extension::chunk_2` về đối tượng và hạn hoàn thành học phí | 0.0627 | Có | Trước ngày 17/04/2026. |
| 3 | Học bổng BCU cho sinh viên đứng đầu là bao nhiêu? | `k3-bcu-scholarship-2026::chunk_0` giới thiệu học bổng BCU | 0.1138 | Có, chi tiết mức tiền ở top-3 | Mức 3.500.000 đồng. |
| 4 | Tân sinh viên đăng ký ký túc xá trong bao nhiêu ngày sau nhập học? | `k3-dormitory-registration::chunk_2` về thời hạn đăng ký KTX | 0.2334 | Có | Trong 07 ngày kể từ ngày hoàn tất thủ tục nhập học. |
| 5 | Sinh viên phải đóng bao nhiêu tiền bảo hiểm y tế năm 2026? | `k3-health-insurance-2026::chunk_0` về đối tượng BHYT | -0.0427 | Có, chi tiết mức tiền ở top-3 | Sinh viên đóng 631.800 đồng. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

Điều tôi học được từ phần của Trương Đình Khoa là recursive chunking cân bằng tốt giữa kích thước và ranh giới tự nhiên của văn bản. Từ phần của Diêm Công Thành, tôi thấy fixed-size có overlap là baseline quan trọng để so sánh, dù đôi khi cắt giữa câu.

## Tự Đánh Giá

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 9 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán độ tương tự | 4 / 5 |
| Kết quả truy xuất của tôi | 8 / 10 |
| **Tổng phần cá nhân** | **56 / 60** |
