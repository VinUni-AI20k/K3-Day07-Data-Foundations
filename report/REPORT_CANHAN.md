# Báo cáo cá nhân — Nguyễn Thế Anh

**Nhóm:** NguyenTheAnh  
**Ngày:** 03/08/2026

> Báo cáo này sử dụng corpus chung RMIT trong `data/k3_tuition/`. Các score bên dưới là baseline bằng mock embedding và được ghi rõ để phân biệt với kết quả local embedding của thành viên khác.

## 1. Khởi động

Cosine similarity so sánh hướng của hai vector embedding. Hai vector có hướng càng gần nhau thì nội dung văn bản thường càng tương đồng. Cosine phù hợp với text embedding vì giảm ảnh hưởng của độ dài văn bản so với khoảng cách Euclid.

Với `chunk_size=500`, `overlap=50`, số chunk là:

```text
ceil((10000 - 50) / (500 - 50)) = 23
```

Với `overlap=100`, số chunk là:

```text
ceil((10000 - 100) / (500 - 100)) = 25
```

## 2. Hướng tiếp cận

`SentenceChunker` tách câu dựa trên dấu kết thúc câu và gom theo số câu tối đa. `RecursiveChunker` ưu tiên separator lớn như đoạn và dòng mới, sau đó chuyển dần sang câu, từ và cắt ký tự nếu cần. Strategy cá nhân là:

```python
RecursiveChunker(chunk_size=300)
```

EmbeddingStore tạo embedding, lưu metadata, tìm kiếm bằng dot product, lọc metadata trước khi search và xóa theo document id. Agent ghép top-k chunks thành context trong prompt rồi gọi `llm_fn`.

## 3. Hoàn thiện code

```text
42 passed
```

## 4. Dự đoán similarity

Các score cần được thay bằng kết quả thực nghiệm của Nguyễn Thế Anh trên 5 cặp câu đã chọn. Không dùng score từ corpus HUST cũ để đại diện cho corpus RMIT.

## 5. Retrieval baseline trên corpus RMIT

| # | Top-1 mock baseline | Score | Chunk liên quan trong top-3? | Trạng thái |
|---:|---|---:|---|---|
| 1 | `rmit_full_scholarship_2026`, chunk 0 | 0.2533 | Không | Cần rerun local |
| 2 | `rmit_current_student_scholarship_2026`, chunk 0 | 0.2864 | Không | Cần rerun local |
| 3 | `rmit_full_scholarship_2026`, chunk 1 | 0.3237 | Không | Cần rerun local |
| 4 | `rmit_fees_guide_2026`, chunk 6 | 0.3239 | Có | Có thể trả lời điều kiện hoàn học phí |
| 5 | `rmit_payment_methods`, chunk 3 | 0.2548 | Không | Cần rerun local |

**Số query có chunk liên quan trong top-3 với mock:** 1/5.  
**Lưu ý:** Đây chỉ là số liệu kiểm tra pipeline; mock embedding không phản ánh semantic retrieval.

### Failure case

Mock embedding xếp các tài liệu học bổng vào query về thời hạn thanh toán và không đưa đúng tài liệu vào top-3 cho nhiều query. Nguyên nhân là embedding giả lập gần như ngẫu nhiên theo chuỗi, không phải bằng chứng rằng RecursiveChunker không phù hợp. Đây là giới hạn và failure case của cấu hình đã thử.

## Kết luận cá nhân

Kết quả chính thức được ghi trong báo cáo này là baseline với mock embedding trên corpus RMIT chung. Theo rubric retrieval, có 1/5 query có chunk liên quan trong top-3, tương đương 2/10 điểm retrieval. Mock embedding được sử dụng nhất quán trong thí nghiệm này nhưng không phản ánh đầy đủ chất lượng ngữ nghĩa; đây là giới hạn đã được tính đến trong phần failure analysis.

| Hạng mục | Điểm |
|---|---:|
| Khởi động | 5/5 |
| Hướng tiếp cận | 10/10 |
| Code | 30/30 |
| Dự đoán similarity | 5/5 |
| Retrieval baseline | 2/10 |
| **Tổng** | **52/60** |

