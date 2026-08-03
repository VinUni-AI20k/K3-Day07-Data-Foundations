# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Đình Khoa
**Mã học viên:** 2A202601297
**Nhóm:** B1-3
**Vai trò trong nhóm:** Nhóm trưởng
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

Trong nhóm, tôi phụ trách điều phối tiến độ, hoàn thiện phần core implementation trong `src`, chạy kiểm thử và tổng hợp kết quả retrieval cho báo cáo. Hai thành viên còn lại phụ trách thu thập/làm sạch dữ liệu và thử nghiệm các chiến lược chunking khác để nhóm có cơ sở so sánh công bằng.

**`SentenceChunker.chunk`:** Tôi dùng regex tách câu tại khoảng trắng sau `.`, `!`, `?` hoặc sau dấu chấm trước xuống dòng, sau đó gom tối đa `max_sentences_per_chunk` câu vào một chunk. Hàm xử lý chuỗi rỗng bằng danh sách rỗng và loại bỏ khoảng trắng thừa để chunk dễ đọc.

**`RecursiveChunker.chunk` / `_split`:** Thuật toán thử các dấu phân cách theo thứ tự ưu tiên `\n\n`, `\n`, `. `, khoảng trắng rồi fallback cắt theo ký tự. Base case là đoạn đã ngắn hơn `chunk_size`; nếu một đoạn vẫn quá dài thì đệ quy với separator tiếp theo.

**`EmbeddingStore`:** Store lưu in-memory các record gồm `id`, `content`, `metadata`, `embedding` và index. Khi tìm kiếm, query được embed rồi tính dot product với từng embedding, sau đó sắp xếp giảm dần theo score.

**`search_with_filter` và `delete_document`:** Metadata được lọc trước khi tính similarity để giảm nhiễu và hỗ trợ các câu hỏi cần scope rõ ràng. `delete_document` xóa mọi chunk có `metadata["doc_id"]` trùng `doc_id`, đồng thời chấp nhận xóa theo `id` trực tiếp.

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

Kết quả bất ngờ nhất là cặp học bổng và bảo hiểm y tế có điểm âm dù con người thấy rất liên quan. Nguyên nhân là mock embedder tạo vector xác định theo chuỗi nhưng không hiểu ngữ nghĩa, nên chỉ phù hợp cho unit test chứ không nên dùng để kết luận chất lượng retrieval tiếng Việt.

## 5. Kết quả truy xuất của tôi

Chiến lược cá nhân của tôi dùng `RecursiveChunker(chunk_size=450)` và mock embedder để chạy được trong môi trường lab hiện tại. Các câu có filter dùng `search_with_filter()`.

| # | Câu hỏi | Top-1 Chunk truy xuất được | Score | Relevant | Câu trả lời Agent tóm tắt |
|---|-------|-----------------------------|-------|----------|---------------------------|
| 1 | Sinh viên xác nhận đăng ký học phần ở hệ thống nào? | `k3-course-registration::chunk_2` về điều chỉnh đăng ký học phần | 0.0984 | Có, nhưng thông tin hệ thống nằm ở top-3 | Sinh viên xác nhận trên `dkhp.uit.edu.vn`. |
| 2 | Sinh viên được gia hạn học phí phải hoàn thành trước ngày nào? | `k3-tuition-extension::chunk_2` về đối tượng và hạn hoàn thành học phí | 0.2144 | Có | Trước ngày 17/04/2026. |
| 3 | Học bổng BCU cho sinh viên đứng đầu là bao nhiêu? | `k3-bcu-scholarship-2026::chunk_0` giới thiệu học bổng BCU | 0.1439 | Có, chi tiết mức tiền ở top-3 | Mức 3.500.000 đồng. |
| 4 | Tân sinh viên đăng ký ký túc xá trong bao nhiêu ngày sau nhập học? | `k3-dormitory-registration::chunk_0` về đăng ký KTX trực tuyến | 0.1692 | Có | Trong 07 ngày kể từ ngày hoàn tất thủ tục nhập học. |
| 5 | Sinh viên phải đóng bao nhiêu tiền bảo hiểm y tế năm 2026? | `k3-health-insurance-2026::chunk_2` về theo dõi hướng dẫn BHYT | 0.1387 | Có, chi tiết mức tiền ở top-3 | Sinh viên đóng 631.800 đồng. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

Điều tôi học được từ phần của Diêm Công Thành là fixed-size chunking có overlap vẫn là baseline tốt để phát hiện nhanh lỗi retrieval. Từ phần của Nguyễn Quang Huy, tôi thấy sentence chunking làm kết quả dễ đọc và dễ giải thích hơn, đặc biệt với tài liệu FAQ/quy trình.

## Tự Đánh Giá

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán độ tương tự | 4 / 5 |
| Kết quả truy xuất của tôi | 9 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
