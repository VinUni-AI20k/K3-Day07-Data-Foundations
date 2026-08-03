# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** B05
**Thành viên:** Dương Ngọc Tiến-2A202601401, Thiều Văn Long-2A202601489, Ngô Phương Nam- 2A202601231, Nguyễn Minh Huy-2A202601303, Đặng Hoàng Hải-2A202601303,Nguyễn Mạnh Hiệp-2A202601319
**Ngày:** 2026-08-03

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
Quy chế, quy trình sử dụng dịch vụ và nội quy tại Thư viện Tạ Quang Bửu - Đại học Bách khoa Hà Nội (HUST).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu                             | Nguồn (Source URL)                                                                                      | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán                                                                                                        |
| - | ------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| 1 | Giờ phục vụ Thư viện                   | https://library.hust.edu.vn/vi/node/416                                                                  | 2026-08-03 / 2026.1      | 932         | `doc_id`, `title`, `audience`, `category`, `department`, `source_url`, `retrieved_at`, `document_version` |
| 2 | Nội quy Thư viện HUST                    | https://library.hust.edu.vn/vi/node/210                                                                  | 2026-08-03 / 2026.1      | 1768        | `doc_id`, `title`, `audience`, `category`, `department`, `source_url`, `retrieved_at`, `document_version` |
| 3 | Quy định làm thẻ bạn đọc             | https://library.hust.edu.vn/vi/node/305                                                                  | 2026-08-03 / 2026.1      | 1735        | `doc_id`, `title`, `audience`, `category`, `department`, `source_url`, `retrieved_at`, `document_version` |
| 4 | Quy trình mượn trả sách tại P.111     | https://library.hust.edu.vn/vi/node/483                                                                  | 2026-08-03 / 2026.1      | 2636        | `doc_id`, `title`, `audience`, `category`, `department`, `source_url`, `retrieved_at`, `document_version` |
| 5 | Nội dung tài liệu tại các phòng đọc | https://library.hust.edu.vn/sites/default/files/4-LC-theophong-2019%20OK.pdf                             | 2026-08-03 / 2019        | 3025        | `doc_id`, `title`, `audience`, `category`, `department`, `source_url`, `retrieved_at`, `document_version` |
| 6 | Phương pháp sắp xếp kho mở            | https://library.hust.edu.vn/sites/default/files/cach%20xep%20gia-2014.pdf                                | 2026-08-03 / 2014        | 4110        | `doc_id`, `title`, `audience`, `category`, `department`, `source_url`, `retrieved_at`, `document_version` |
| 7 | Danh mục giáo trình năm 2023            | https://library.hust.edu.vn/sites/default/files/6-Danh%20mục%20tài%20liệu%20giáo%20trình%202023.pdf | 2026-08-03 / 2023        | 7577        | `doc_id`, `title`, `audience`, `category`, `department`, `source_url`, `retrieved_at`, `document_version` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [X] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [X] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu   | Ví dụ giá trị                           | Tại sao hữu ích cho truy xuất (retrieval)?                                                          |
| -------------------- | ------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `doc_id`           | `str` | `hust-noi-quy-thu-vien`                   | Nhận dạng duy nhất từng tài liệu gốc trong cơ sở dữ liệu.                                    |
| `title`            | `str` | `Nội quy Thư viện HUST`                | Lưu tiêu đề tài liệu để hiển thị trong kết quả trả về của Agent.                         |
| `audience`         | `str` | `student`                                 | Lọc đối tượng (student, all) để tránh lấy nhầm các tài liệu dành cho đối tượng khác. |
| `category`         | `str` | `rules`                                   | Phân loại thể loại quy định để tìm kiếm và gom nhóm chính xác hơn.                       |
| `department`       | `str` | `library`                                 | Lọc theo đơn vị ban hành / bộ phận phụ trách tài liệu.                                       |
| `source_url`       | `str` | `https://library.hust.edu.vn/vi/node/210` | Truy vết nguồn gốc chính thống để kiểm chứng thông tin.                                       |
| `retrieved_at`     | `str` | `2026-08-03`                              | Quản lý vòng đời dữ liệu, biết thời điểm cào dữ liệu để kiểm tra độ mới.            |
| `document_version` | `str` | `2026.1`                                  | Đảm bảo tính cập nhật của tài liệu quy định, hỗ trợ kiểm tra phiên bản.                 |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên các tài liệu:

| Tài liệu                      | Chiến lược (Strategy)           | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?                                                         |
| ------------------------------- | ---------------------------------- | ----------------- | --------------------- | --------------------------------------------------------------------------------------- |
| `hust-danh-muc-giao-trinh.md` | FixedSizeChunker (`fixed_size`)  | 31                | 292.8                 | Kém (mất cấu trúc bảng)                                                            |
|                                 | SentenceChunker (`by_sentences`) | 1                 | 7576.0                | Tệ (cả file gộp vào một chunk lớn do thiếu dấu câu ngắt câu chuẩn)          |
|                                 | RecursiveChunker (`recursive`)   | 34                | 221.6                 | Tốt (giữ khối dữ liệu cùng tầng)                                                 |
| `hust-gio-phuc-vu.md`         | FixedSizeChunker (`fixed_size`)  | 4                 | 270.5                 | Trung bình (cắt ngang từ ở rìa)                                                    |
|                                 | SentenceChunker (`by_sentences`) | 2                 | 464.0                 | Tốt (giữ nguyên câu văn hoàn chỉnh)                                              |
|                                 | RecursiveChunker (`recursive`)   | 4                 | 231.5                 | Rất tốt (cố gắng ngắt ở newline trước)                                          |
| `hust-noi-quy-thu-vien.md`    | FixedSizeChunker (`fixed_size`)  | 7                 | 295.4                 | Trung bình                                                                             |
|                                 | SentenceChunker (`by_sentences`) | 6                 | 292.0                 | Tốt (giữ nguyên vẹn câu văn nội quy)                                             |
|                                 | RecursiveChunker (`recursive`)   | 7                 | 250.9                 | Tốt (chia đoạn rõ ràng theo các điều khoản)                                    |
| `hust-quy-dinh-lam-the.md`    | FixedSizeChunker (`fixed_size`)  | 7                 | 290.7                 | Trung bình                                                                             |
|                                 | SentenceChunker (`by_sentences`) | 4                 | 431.5                 | Tốt (bảo toàn các câu quy định)                                                  |
|                                 | RecursiveChunker (`recursive`)   | 7                 | 246.1                 | Tốt (tách bạch từng bước làm thẻ)                                               |
| `hust-quy-trinh-muon-tra.md`  | FixedSizeChunker (`fixed_size`)  | 11                | 285.1                 | Trung bình                                                                             |
|                                 | SentenceChunker (`by_sentences`) | 6                 | 431.8                 | Khá (văn bản quy trình đọc liền mạch)                                           |
|                                 | RecursiveChunker (`recursive`)   | 11                | 237.8                 | Rất tốt (giữ luồng các bước thực hiện tuần tự)                               |
| `hust-sap-xep-kho-mo.md`      | FixedSizeChunker (`fixed_size`)  | 17                | 288.8                 | Kém (cắt ngang các cấp bậc phân loại sách)                                      |
|                                 | SentenceChunker (`by_sentences`) | 7                 | 584.3                 | Khá (có thể gộp nhiều mục do thiếu dấu câu)                                    |
|                                 | RecursiveChunker (`recursive`)   | 18                | 227.2                 | Tốt (duy trì cấu trúc cây phân loại DDC)                                         |
| `hust-tai-lieu-phong-doc.md`  | FixedSizeChunker (`fixed_size`)  | 12                | 297.9                 | Trung bình                                                                             |
|                                 | SentenceChunker (`by_sentences`) | 3                 | 1000.3                | Kém (gộp chunk quá lớn do danh sách dạng bullet không có dấu chấm cuối câu) |
|                                 | RecursiveChunker (`recursive`)   | 15                | 200.5                 | Tốt (giữ phân tầng thông tin của từng phòng đọc)                              |

---

## Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Mạnh Hiệp, Đặng Hoàng Hải**

- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Log cho thấy các chunk giữ nguyên tiêu đề Markdown (`# Giờ phục vụ Thư viện`, `# Nội quy Thư viện HUST`...) cùng đoạn nội dung theo sau, phù hợp với cắt đệ quy theo separator từ lớn đến nhỏ (`\n\n`, `\n`, `. `). Cách này giữ liền mạch ngữ cảnh giữa tiêu đề và nội dung.
- **Điểm top-1 trung bình:** Hiệp 0.6261 / Hải 0.6046 → trung bình cặp **0.6154**
  **Thành viên 2 — Dương Ngọc Tiến, Thiều Văn Long**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn:** Chia tài liệu thành các đoạn kích thước cố định, giúp mô hình embedding nhận lượng token đồng nhất. Điểm top-1 khá cao ở 4/5 câu, riêng câu 5 ("mượn giáo trình về nhà") điểm rơi mạnh (Long 0.407, Tiến 0.427) do câu trả lời phụ thuộc vào chunk danh mục/quy trình mượn trả tách rời nhau, ranh giới chunk cố định cắt ngang ngữ nghĩa.
- **Điểm top-1 trung bình:** Tiến 0.6048 / Long 0.6456 → trung bình cặp **0.6252**
  **Thành viên 3 — Nguyễn Minh Huy, Ngô Phương Nam**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Phù hợp với các tài liệu nội quy có câu văn ngắn, rõ ràng, giúp giữ trọn vẹn ngữ nghĩa từng quy định nhỏ. Tuy nhiên với câu 3 ("Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng mấy?") cả hai đều lấy nhầm top-1 từ `hust-noi-quy-thu-vien` thay vì `hust-tai-lieu-phong-doc`/`hust-sap-xep-kho-mo`, cho thấy chunk theo câu đôi khi tách rời câu trả lời khỏi ngữ cảnh bảng/tầng.
- **Điểm top-1 trung bình:** Huy 0.6066 / Nam 0.6117 → trung bình cặp **0.6092**

## So sánh giữa các thành viên

| Thành viên        | Chiến lược | Điểm top-1 TB (5 câu) | Điểm mạnh                                       | Điểm yếu                                                                                           |
| ------------------- | ------------- | -----------------------: | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Nguyễn Mạnh Hiệp | Recursive     |                   0.6261 | Giữ cấu trúc tiêu đề + nội dung liền mạch | Có câu (câu 3) vẫn ưu tiên`hust-sap-xep-kho-mo` hơn tài liệu đúng chủ đề phòng đọc |
| Đặng Hoàng Hải  | Recursive     |                   0.6046 | Ổn định qua các câu, giữ ngữ cảnh nội quy | Câu 3, 5 điểm thấp do chunk lẫn nội dung nhiều chủ đề trong 1 file dài                     |
| Dương Ngọc Tiến | FixedSize     |                   0.6048 | Triển khai đơn giản, chunk đều               | Câu 5 tụt mạnh (0.427) vì cắt cứng làm đứt ngữ cảnh giữa quy trình và danh mục         |
| Thiều Văn Long    | FixedSize     |                   0.6456 | Điểm cao nhất nhóm, đặc biệt câu 3, 4      | Câu 5 vẫn là điểm yếu chung của FixedSize (0.407, chỉ đạt hạng 2 khi so bảng đáp án)   |
| Ngô Phương Nam   | Sentence      |                   0.6117 | Giữ trọn câu quy định ngắn (câu 1, 2)       | Câu 3 và 5 tách chunk quá nhỏ, mất ngữ cảnh bảng số liệu                                   |
| Nguyễn Minh Huy    | Sentence      |                   0.6066 | Câu 1, 2 điểm cao, đúng chủ đề             | Câu 3 lấy nhầm nguồn (nội quy thay vì tài liệu phòng đọc)                                  |

**Trung bình theo nhóm chiến lược:**

| Chiến lược           | Điểm top-1 TB |
| ----------------------- | --------------: |
| FixedSize (Tiến, Long) |          0.6252 |
| Recursive (Hiệp, Hải) |          0.6154 |
| Sentence (Huy, Nam)     |          0.6092 |

## Chiến lược nào tốt nhất cho chủ đề này? Tại sao?

Trên dữ liệu thực tế, chênh lệch giữa 3 chiến lược khá nhỏ (0.609 – 0.625), nên không có chiến lược nào vượt trội rõ rệt về điểm số trung bình. Tuy nhiên xét theo hành vi từng câu:

- **FixedSizeChunker** cho điểm top-1 cao nhất ở đa số câu hỏi đơn giản, ngắn gọn (câu 1–4), nhưng **thất bại rõ nhất ở câu 5** (câu hỏi cần nối thông tin giữa "quy trình mượn" và "danh mục giáo trình" — hai phần thường nằm ở các đoạn xa nhau trong tài liệu gốc), cho thấy nhược điểm của việc cắt theo độ dài cố định mà không quan tâm ranh giới ngữ nghĩa.
- **RecursiveChunker** ổn định hơn ở việc giữ tiêu đề đi kèm nội dung, phù hợp với tài liệu Markdown phân cấp như nội quy/giờ phục vụ, nhưng vẫn có câu bị lẫn chủ đề khi một file dài chứa nhiều mục.
- **SentenceChunker** giữ trọn vẹn từng câu quy định nên tốt cho câu hỏi trực tiếp trích một câu (câu 1, 2), nhưng dễ mất ngữ cảnh với dữ liệu dạng bảng/tầng (câu 3), vì bảng không có cấu trúc câu rõ ràng để cắt.
  **Kết luận:** Với chủ đề "quy định thư viện" — nơi tài liệu có cả văn bản nội quy dạng câu lẫn bảng danh mục/tầng — **RecursiveChunker** là lựa chọn cân bằng nhất vì nó không phụ thuộc hoàn toàn vào dấu câu (khác Sentence) và không cắt cứng theo độ dài bất kể ngữ cảnh (khác FixedSize). Câu 5 (mượn giáo trình về nhà) là điểm yếu chung của cả 3 chiến lược, gợi ý nhóm nên thử **tăng kích thước overlap giữa các chunk** hoặc **gộp file quy trình mượn trả với danh mục giáo trình** để cải thiện truy xuất cho các câu hỏi cần nối thông tin liên file.


## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query)                                                      | Câu trả lời chuẩn (Gold Answer)                                                                                                                                                                                | Chunk nào chứa thông tin?                                     |
| - | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| 1 | Thư viện mở cửa lúc mấy giờ vào cuối tuần?                   | Vào cuối tuần (Thứ 7, Chủ nhật), phòng tự học mở cửa từ 8h00 đến 19h00.                                                                                                                              | `hust-gio-phuc-vu.md`                                          |
| 2 | Để làm thẻ thư viện cần mang theo giấy tờ gì?                | Cần xuất trình thẻ hợp lệ (thẻ cán bộ, thẻ sinh viên, thẻ học viên cao học/nghiên cứu sinh) theo quy định làm thẻ.                                                                            | `hust-noi-quy-thu-vien.md` + `hust-quy-dinh-lam-the.md`      |
| 3 | Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng mấy?                | Phòng đọc Kinh tế - Ngoại ngữ (P.402) nằm ở tầng 4.                                                                                                                                                       | `hust-tai-lieu-phong-doc.md`                                   |
| 4 | Hệ thống phân loại sách nào được sử dụng trong thư viện?  | Thư viện Tạ Quang Bửu phân loại theo khung DDC (Dewey Decimal Classification), xếp giá theo mã Cutter.                                                                                                    | `hust-sap-xep-kho-mo.md`                                       |
| 5 | Có được phép mượn giáo trình Cơ lý thuyết về nhà không? | Có — giáo trình được mượn về nhà tại Phòng mượn giáo trình (P.111) theo quy trình mượn trả riêng; tài liệu ở các phòng đọc chuyên ngành thì chỉ đọc tại chỗ, không mang về. | `hust-quy-trinh-muon-tra.md` + `hust-danh-muc-giao-trinh.md` |

*(Câu 3 và câu 5 cần **ghép thông tin từ 2 nguồn** — đây chính là lý do điểm truy xuất của cả 3 chiến lược đều thấp hơn hẳn ở hai câu này so với câu 1, 2, 4.)*

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi                                                              | Chiến lược tốt nhất cho câu này                                                                                                                               | Có chunk liên quan trong top-3? | Ghi chú                                                                                                                                                                                                                                                                            |
| - | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Thư viện mở cửa lúc mấy giờ vào cuối tuần?                   | Không phân biệt rõ — cả 3 chiến lược đều đúng top-1 (0.73–0.74)                                                                                        | Có                               | Đạt điểm tối đa, không chiến lược nào vượt trội                                                                                                                                                                                                                       |
| 2 | Để làm thẻ thư viện cần mang theo giấy tờ gì?                | Không phân biệt rõ — cả 3 chiến lược đều đúng top-1, chỉ khác tài liệu cụ thể (nội quy vs. quy định làm thẻ, cả hai đều đúng chủ đề) | Có                               | Đạt điểm tối đa                                                                                                                                                                                                                                                               |
| 3 | Phòng đọc Kinh tế - Ngoại ngữ nằm ở tầng mấy?                | **FixedSize** (Long lấy đúng `hust-tai-lieu-phong-doc` ở top-1, 0.679)                                                                                   | Có, nhưng không đồng đều   | Recursive và Sentence phần lớn lấy nhầm top-1 (`hust-noi-quy-thu-vien`, `hust-sap-xep-kho-mo`); chunk đúng chỉ lọt top-2/3 ở một vài trường hợp (Hiệp). **Không đạt điểm tối đa** cho 2 chiến lược còn lại                                    |
| 4 | Hệ thống phân loại sách nào được sử dụng trong thư viện?  | Không phân biệt rõ — cả 6 log đều đúng top-1`hust-sap-xep-kho-mo` (0.63–0.71)                                                                           | Có                               | Đạt điểm tối đa toàn nhóm                                                                                                                                                                                                                                                   |
| 5 | Có được phép mượn giáo trình Cơ lý thuyết về nhà không? | Không có chiến lược nào tốt rõ rệt                                                                                                                          | Có, nhưng rời rạc             | Điểm top-1 thấp nhất trong cả 5 câu ở mọi chiến lược (0.38–0.48); mỗi log chỉ trả về**một trong hai** nguồn cần thiết (quy trình mượn trả *hoặc* danh mục giáo trình) chứ không ghép được cả hai. **Không đạt điểm tối đa** |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Về mặt thiết kế, lọc theo `audience`/`category` (ví dụ giới hạn phạm vi tìm kiếm vào nhóm tài liệu "giờ phục vụ" hoặc "quy định") có thể giúp giảm nhiễu cho câu 1, 2, 4 — những câu có domain rõ ràng. Tuy nhiên **log hiện tại chưa bật/so sánh metadata filtering**, nên đây là dự đoán dựa trên thiết kế, chưa phải kết quả đã đo được. Với câu 3 và 5, lọc metadata một mình không đủ giải quyết vấn đề vì gốc rễ là thông tin nằm ở **hai tài liệu khác nhau**, cần chunk chồng lấn (overlap) hoặc truy xuất đa bước (multi-hop) chứ không chỉ lọc phạm vi tìm kiếm.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

* **Khác biệt giữa các chiến lược nhỏ hơn kỳ vọng ban đầu:** Điểm top-1 trung bình của 3 chiến lược chỉ chênh nhau trong khoảng 0.609–0.625 trên thang similarity — không có chiến lược nào "vượt trội" rõ rệt như giả định lúc đầu; sự khác biệt lớn nằm ở *từng câu hỏi cụ thể* chứ không phải ở tổng thể.
* **Câu hỏi cần ghép nhiều nguồn là điểm yếu chung:** Câu 3 (vị trí phòng) và câu 5 (chính sách mượn) đều là loại câu cần nối thông tin từ 2 tài liệu, và cả 3 chiến lược đều tụt điểm rõ rệt ở đây — cho thấy vấn đề nằm ở **cách tổ chức dữ liệu nguồn** (thông tin bị tách rời giữa các file) nhiều hơn là ở thuật toán chunking.
* **Tài liệu dạng bảng/danh mục là thách thức riêng:** SentenceChunker gom nhầm chunk khi thiếu dấu câu chuẩn (câu 3, với `hust-danh-muc-giao-trinh` chỉ là bảng số tầng không có ngữ cảnh câu); FixedSizeChunker lại cắt đứt ranh giới ngữ nghĩa giữa các mục trong bảng dài. RecursiveChunker giảm thiểu được vấn đề này nhờ ưu tiên tách theo đoạn/tiêu đề trước khi mới cắt theo câu.
  **Bài học rút ra khi so sánh trong nhóm:**
  Không có một chiến lược "thắng tuyệt đối" — FixedSize cho điểm cao nhất ở các câu đơn giản (đặc biệt câu 3 với Long), Recursive ổn định nhất qua các câu, còn Sentence tốt cho câu hỏi trích nguyên câu quy định nhưng yếu với dữ liệu bảng. Việc chọn chiến lược nên gắn với **loại tài liệu** (văn bản nội quy dạng câu vs. bảng danh mục) hơn là áp một chiến lược duy nhất cho toàn bộ corpus.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

- Chuẩn hóa các bảng danh mục giáo trình/tầng phòng thành định dạng key-value hoặc CSV phẳng để chunker (đặc biệt Sentence) không bị mất ngữ cảnh cột.
- Với các câu hỏi cần ghép 2 nguồn (câu 3, câu 5), cân nhắc **tăng overlap giữa các chunk** hoặc gộp các file liên quan chặt chẽ (ví dụ `hust-quy-trinh-muon-tra.md` và `hust-danh-muc-giao-trinh.md`) thành một tài liệu, hoặc bổ sung bước truy xuất đa bước (retrieve → re-query) thay vì chỉ dựa vào một lượt top-k.
- Thử nghiệm thực tế việc lọc theo metadata (hiện mới ở mức thiết kế) để có số liệu so sánh trước/sau thay vì chỉ suy luận.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                   | Điểm tự đánh giá | Ghi chú                                                                                                                                                                             |
| -------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10                 | Bộ tài liệu bao phủ tốt các chủ đề nhưng thông tin cho câu 3, 5 bị tách rời giữa nhiều file, gây khó cho truy xuất                                               |
| Thiết kế chiến lược (Strategy Design)   | 13 / 15                | 3 chiến lược có lý do chọn hợp lý, nhưng chưa thử nghiệm biến thể overlap/kích thước chunk khác nhau để khắc phục điểm yếu ở câu 5                        |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10                 | Câu 1, 2, 4 đạt điểm tối đa ở mọi chiến lược; câu 3 chỉ FixedSize đạt; câu 5 không chiến lược nào đạt điểm tối đa (điểm thấp nhất nhóm, 0.38–0.48) |
| Thuyết trình (Demo)                        | 5 / 5                  | Trình bày rõ ràng, có số liệu cụ thể từ log thay vì nhận định chung chung                                                                                              |
| **Tổng phần nhóm**                  | **34 / 40**      | Thấp hơn bản tự chấm ban đầu (40/40) vì đã đối chiếu lại với log thật thay vì giả định tất cả câu đều đạt điểm tối đa                                 |
