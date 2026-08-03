# Kết Quả Bước 6 — Phân Công & Thiết Kế Chiến Lược Chunking Cho Từng Thành Viên

**Ngày thực hiện:** 03/08/2026  
**Nhóm:** K3 Day 07  

---

## 1. Nguyên Tắc Phân Công Chiến Lược

Để đáp ứng tiêu chí so sánh đa dạng chiến lược trên cùng một bộ corpus quy định đại học (VinUniversity), các thành viên được phân công 3 chiến lược khác biệt hoàn toàn:

| Thành viên | Tên thành viên | Mã sinh viên | Chiến lược Chunking | Mô tả ngắn & Tham số |
|---|---|---|---|---|
| **Thành viên 1** | Nhóm trưởng (Nguyễn Xuân Phượng) | 2A202601874 | **SentenceChunker** *(Built-in)* | Tách theo ranh giới câu (`. `, `! `, `? `), ghép nhóm `max_sentences_per_chunk=3`. |
| **Thành viên 2** | Lê Nguyễn Minh Đức | 2A202601013 | **RecursiveChunker** *(Built-in)* | Đệ quy theo thứ tự ưu tiên dấu phân cách: `["\n\n", "\n", ". ", " ", ""]` với `chunk_size=400`. |
| **Thành viên 3** | Phụ trách Retrieval & Benchmark (Nguyễn Đào Nam Hải) | 2A202601037 | **CustomSectionHeaderChunker** *(Tùy chỉnh)* | Tách văn bản theo cấu trúc tiêu đề (Header `#`, `##`), giữ nguyên vẹn trọn một mục quy định. |

---

## 2. Chi Tiết Chiến Lược Của Thành Viên 3 (Nguyễn Đào Nam Hải - 2A202601037)

### Lý do thiết kế chiến lược `CustomSectionHeaderChunker`:
Tài liệu quy định đại học (đăng ký môn học, học phí, học phần tiên quyết...) luôn có cấu trúc phân tầng rõ ràng theo các tiêu đề mục (Header `## 1.`, `## 2.`). Nếu sử dụng cắt theo kích thước cố định (`FixedSize`), một điều khoản quy định có thể bị cắt làm đôi khiến ngữ cảnh bị rời rạc. 

Chiến lược `CustomSectionHeaderChunker` giúp:
1. Giữ nguyên vẹn toàn bộ nội dung của từng điều khoản/quy định trong 1 chunk.
2. Bảo toàn tiêu đề mục gắn liền với nội dung bên dưới, giúp Embedding Model đại diện ngữ nghĩa chính xác hơn.

### Code Snippet triển khai chiến lược Custom:

```python
import re

class CustomSectionHeaderChunker:
    """
    Chiến lược chia nhỏ tùy chỉnh cho văn bản quy định đại học.
    Tách văn bản dựa trên các tiêu đề Markdown (# hoặc ##).
    """

    def __init__(self, max_chunk_size: int = 600) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []

        # Tách dựa trên tiêu đề Markdown (Header 1 hoặc Header 2)
        pattern = r'(?=\n##?\s+)'
        sections = re.split(pattern, text)
        
        chunks = []
        for sec in sections:
            sec_str = sec.strip()
            if not sec_str:
                continue
            
            # Nếu section vượt quá max_chunk_size, tiếp tục tách theo đoạn (\n\n)
            if len(sec_str) > self.max_chunk_size:
                sub_parts = sec_str.split("\n\n")
                curr = ""
                for part in sub_parts:
                    if len(curr) + len(part) + 2 <= self.max_chunk_size:
                        curr = f"{curr}\n\n{part}".strip()
                    else:
                        if curr:
                            chunks.append(curr)
                        curr = part.strip()
                if curr:
                    chunks.append(curr)
            else:
                chunks.append(sec_str)

        return chunks
```

---

## 3. Kế Hoạch Chạy Benchmark Tiếp Theo (Bước 7)

Tất cả 3 thành viên sẽ cùng sử dụng bộ dữ liệu `data/k3_university/` và 5 câu hỏi benchmark đã chốt ở Bước 5 để chạy kiểm thử và so sánh hiệu năng truy xuất ở Bước 7.
