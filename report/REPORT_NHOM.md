# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Sổ tay sinh viên Đại học Phenikaa — 5 quy định vận hành thường gặp nhất với sinh viên: đăng ký học phần, thanh toán học phí, học bổng khuyến khích học tập, ký túc xá, dịch vụ thư viện.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký khối lượng học tập và rút bớt học phần | [sotaysv.phenikaa-uni.edu.vn/.../1.5-dang-ky-khoi-luong-hoc-tap-va-rut-bot-hoc-phan-da-dang-ky](https://sotaysv.phenikaa-uni.edu.vn/home/1.-hoat-dong-dao-tao-tai-truong-dai-hoc-phenikaa/1.5-dang-ky-khoi-luong-hoc-tap-va-rut-bot-hoc-phan-da-dang-ky) | 2026-08-03 / not-stated | 1197 | audience=student, department=academic-affairs, category=course-registration |
| 2 | Dịch vụ Trung tâm Thông tin - Thư viện | [sotaysv.phenikaa-uni.edu.vn/.../4.-trung-tam-thong-tin-thu-vien](https://sotaysv.phenikaa-uni.edu.vn/home/4.-trung-tam-thong-tin-thu-vien) | 2026-08-03 / not-stated | 1153 | audience=all, department=library, category=library-services |
| 3 | Các quy định về thanh toán học phí | [sotaysv.phenikaa-uni.edu.vn/.../5.-cac-quy-dinh-ve-thanh-toan-hoc-phi](https://sotaysv.phenikaa-uni.edu.vn/home/5.-cac-quy-dinh-ve-thanh-toan-hoc-phi) | 2026-08-03 / not-stated | 970 | audience=student, department=finance, category=tuition |
| 4 | Ký túc xá sinh viên | [sotaysv.phenikaa-uni.edu.vn/.../7.-ky-tuc-xa-sinh-vien](https://sotaysv.phenikaa-uni.edu.vn/home/7.-ky-tuc-xa-sinh-vien) | 2026-08-03 / not-stated | 1121 | audience=student, department=dormitory-management, category=dormitory |
| 5 | Học bổng KKHT, rèn luyện, khen thưởng, kỷ luật sinh viên | [sotaysv.phenikaa-uni.edu.vn/.../2.3-hoc-bong-khuyen-khich-hoc-tap...](https://sotaysv.phenikaa-uni.edu.vn/home/2.-hoat-dong-cong-tac-sinh-vien/2.3-hoc-bong-khuyen-khich-hoc-tap-ren-luyen-khen-thuong-ky-luat-sinh-vien) | 2026-08-03 / not-stated | 3869 | audience=student, department=student-affairs, category=scholarship |

> Nguồn `document_version` không nêu rõ trên trang gốc nên ghi `not-stated` theo quy ước trong `docs/DATA_COLLECTION.md`.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng (Sổ tay sinh viên công khai của Đại học Phenikaa) và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string (enum) | `student`, `all` | Bắt buộc theo K3 — lọc để tránh trả lời sai đối tượng (vd. loại tài liệu không dành cho sinh viên khỏi kết quả). |
| `department` | string | `academic-affairs`, `library`, `finance`, `dormitory-management`, `student-affairs` | Cho phép thu hẹp truy xuất theo đơn vị phụ trách khi câu hỏi nêu rõ phòng/ban. |
| `category` | string | `course-registration`, `tuition`, `scholarship`, `dormitory`, `library-services` | Phân loại chủ đề mịn hơn `department`, hữu ích khi một phòng ban quản lý nhiều loại quy định. |
| `language` | string | `vi` | Chuẩn bị cho trường hợp corpus đa ngôn ngữ trong tương lai. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| k3_university (5 docs) | FixedSizeChunker (`fixed_size`) | 21 | ~475 ký tự | Có, nhưng có thể cắt giữa câu |
| k3_university (5 docs) | SentenceChunker (`by_sentences`) | N/A | Tùy số câu | Có, giữ ranh giới câu |
| k3_university (5 docs) | RecursiveChunker (`recursive`) | 83 | ~130 ký tự | Có, tôn trọng cấu trúc (\n\n, \n, .) |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Minh Thu (01631)**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn cho chủ đề này:** RecursiveChunker chia lần lượt theo dấu phân cách (đoạn "\n\n", dòng "\n", câu ". ", từ " ", cuối cùng ký tự). Với tài liệu quy định đại học có cấu trúc rõ ràng (tiêu đề → mục → dòng), chiến lược này tôn trọng ngữ pháp markdown và giữ ngữ cảnh tốt hơn FixedSize. Tạo nhiều chunks nhỏ (83 vs 21) giúp tìm kiếm dễ chính xác hơn khi đặt câu hỏi cụ thể.
- **Code snippet (nếu custom):**
```python
from src.src_NguyenMinhThu_01631.chunking import RecursiveChunker

# Sử dụng mặc định với separators = ["\n\n", "\n", ". ", " ", ""]
chunker = RecursiveChunker(chunk_size=500)
chunks = chunker.chunk(text)
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Minh Thu | RecursiveChunker | 2 (1/5 with mock) | Tôn trọng cấu trúc tài liệu; nhiều chunks giúp dễ tìm thông tin chi tiết | Tạo quá nhiều chunks nhỏ; có thể làm tăng chi phí embedding khi dùng API |
| [Thành viên 2] | [Chiến lược] | / | | |
| [Thành viên 3] | [Chiến lược] | / | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Với dữ liệu quy định đại học có cấu trúc rõ ràng, RecursiveChunker cho kết quả tốt hơn vì tôn trọng ranh giới tự nhiên (đoạn, dòng, câu). Tuy nhiên, kết quả đánh giá hiện tại (với mock embeddings) không phản ánh chất lượng thực; cần chạy lại với local multilingual embedder để so sánh công bằng giữa các chiến lược.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy. Vị trí "Chunk nào chứa thông tin" được xác định bằng chiến lược `FixedSizeChunker(chunk_size=500, overlap=50)` (Người 1) — các thành viên khác dùng chiến lược riêng có thể ra chunk id khác, nhưng nội dung nguồn tham chiếu là như nhau.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Mỗi học kỳ, sinh viên được đăng ký tối thiểu và tối đa bao nhiêu tín chỉ? | Tối thiểu 08 tín chỉ, tối đa 16 tín chỉ mỗi học kỳ (mục 1.5.3). | `k3-course-registration::chunk_1` |
| 2 | Nếu sinh viên còn nợ học phí của học kỳ trước thì điều gì xảy ra khi đăng ký học kỳ tiếp theo? | Sinh viên còn nợ học phí của các học kỳ trước sẽ **không được đăng ký học phần** của học kỳ tiếp theo. | `k3-tuition-payment::chunk_2` (bối cảnh liên quan nằm ở `chunk_1`) |
| 3 | *(cần metadata_filter audience=student)* Sinh viên đạt học bổng khuyến khích học tập Loại A được nhận mức học bổng bằng bao nhiêu phần trăm số học phí đã nộp? | Loại A = 50% mức học bổng (Mức HB = Loại HB × số học phí sinh viên đã nộp trong năm học). | `k3-scholarship-policy::chunk_2` |
| 4 | Chi phí ở ký túc xá phòng 8 sinh viên là bao nhiêu mỗi tháng? | 350.000 VNĐ/sinh viên/tháng. | `k3-dormitory-policy::chunk_0` |
| 5 | Khu tự học ở tầng 6 của thư viện mở cửa vào những khung giờ nào? | Thứ 2 đến Chủ nhật, 6h30–22h. | `k3-library-services::chunk_2` |

**Vì sao câu 3 cần `metadata_filter={"audience": "student"}`:** tài liệu thư viện (`k3-library-services`) gắn `audience=all` và cũng nhắc tới cụm "sinh viên" nhiều lần, có thể bị truy xuất chung với câu hỏi có từ khóa "sinh viên"/"khuyến khích" nếu tìm kiếm không lọc theo đối tượng. Lọc `audience=student` giúp loại các tài liệu không dành riêng cho sinh viên khỏi top-k trước khi tính điểm tương đồng.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mỗi học kỳ đăng ký tối thiểu/tối đa bao nhiêu tín chỉ? | FixedSizeChunker | Không (Q1 thất bại cả 2 chiến lược với mock) | Cần local embedder; mock không hiểu ngữ nghĩa tương đương |
| 2 | Sinh viên nợ học phí kỳ trước → kỳ tiếp theo? | RecursiveChunker (chưa tìm được) | Không (Q2 thất bại cả 2 chiến lược) | Cần địa chỉ cụ thể mục trong tài liệu |
| 3 | Học bổng Loại A bao nhiêu %? | FixedSizeChunker | Có (✓) | FixedSizeChunker tìm được Q3 |
| 4 | Phòng 8 sinh viên ký túc xá bao nhiêu? | RecursiveChunker | Có (✓) | RecursiveChunker tìm được Q4 |
| 5 | Khu tự học tầng 6 mở cửa khi nào? | RecursiveChunker (chưa tìm được) | Không (Q5 thất bại cả 2 chiến lược) | Thông tin nằm trong phần "Giờ mở cửa", cần embedding tốt hơn |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Q3 có dùng `metadata_filter={"audience": "student"}` nhưng vẫn thất bại vì kết quả truy xuất không phù hợp từ đầu. Metadata filtering sẽ hữu ích hơn khi kết hợp với embedding chất lượng cao; hiện tại với mock embedder, điểm similarity đã sai nên lọc metadata cũng không cứu vãn được.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Mock vs Real embeddings**: Kết quả với mock embedder không phản ánh chất lượng thực vì nó không hiểu ngữ cảnh/ngữ nghĩa. Chất lượng embedder là yếu tố quyết định kết quả truy xuất, quan trọng hơn cả chiến lược chunking.
> 2. **Chunk size trade-off**: RecursiveChunker tạo 83 chunks (vs 21 của FixedSize) → chi phí cao hơn nhưng có thể tìm thông tin chi tiết hơn; FixedSize tiết kiệm chi phí nhưng có thể mất ngữ cảnh ở ranh giới chunk.
> 3. **Cấu trúc dữ liệu quan trọng**: Tài liệu quy định đại học có cấu trúc rõ ràng (markdown heading, mục) → RecursiveChunker tôn trọng cấu trúc này tốt hơn.

**Bài học rút ra khi so sánh trong nhóm:**
> Cả hai chiến lược (FixedSize vs Recursive) đều cho kết quả tương đương (1/5 điểm) với mock embedder, nhưng chúng thành công ở các câu hỏi khác nhau (Q3 vs Q4). Điều này chứng minh rằng với mock, kết quả gần như ngẫu nhiên. Để so sánh công bằng, nhóm cần chạy lại bằng `EMBEDDING_PROVIDER=local` với multilingual embedder; lúc đó sẽ thấy rõ ưu/nhược điểm của từng chiến lược trên dữ liệu tiếng Việt.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> 1. Thu thập tài liệu với metadata richer (ví dụ: tiêu đề mục, từ khóa chính) để hỗ trợ truy xuất.
> 2. Thiết kế câu hỏi đánh giá sao cho có thể trích trực tiếp từ tài liệu (giảm phụ thuộc vào embedding quality).
> 3. Sử dụng local multilingual embedder từ đầu để có feedback có ý nghĩa trong quá trình thiết kế chiến lược.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
