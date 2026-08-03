# Bộ Markdown Sổ tay sinh viên USTH

> Nguồn chính: mục [Công tác sinh viên](https://usth.edu.vn/cong-tac-sinh-vien/) trên [usth.edu.vn](https://usth.edu.vn/), cùng trang [Thư viện](https://usth.edu.vn/thu-vien-8449/) và [Hướng dẫn đăng ký học phần](https://usth.edu.vn/huong-dan-dang-ky-hoc-phan-block-3-28717/)
> Phương pháp thu thập: crawl thủ công các trang công khai bằng công cụ tìm nạp trang web (WebFetch), có kiểm tra `robots.txt` trước khi truy cập (chỉ chặn `*.php`, `/wp-admin/`, `*comment-page*` — không ảnh hưởng các trang nội dung dưới đây)
> Ngày truy cập: 2026-08-03
> Tổng số tài liệu: 9

## Danh mục tài liệu

| STT | Tài liệu | Chủ đề | Nguồn |
|---:|---|---|---|
| 1 | [Học phí và phí](01-hoc-phi-va-phi.md) | Học phí | [Xem](https://usth.edu.vn/cong-tac-sinh-vien/hoc-bong-hoc-phi-cong-tac-sinh-vien/hoc-phi-va-phi/) |
| 2 | [Học bổng USTH](02-hoc-bong-usth.md) | Học bổng nội bộ | [Xem](https://usth.edu.vn/cong-tac-sinh-vien/hoc-bong-hoc-phi-cong-tac-sinh-vien/hoc-bong-usth/) |
| 3 | [Học bổng khác](03-hoc-bong-khac.md) | Học bổng bên ngoài | [Xem](https://usth.edu.vn/cong-tac-sinh-vien/hoc-bong-hoc-phi-cong-tac-sinh-vien/hoc-bong-khac/) |
| 4 | [Thủ tục hành chính công tác sinh viên](04-thu-tuc-hanh-chinh.md) | Thủ tục hành chính | [Xem](https://usth.edu.vn/cong-tac-sinh-vien/dich-vu-ho-tro-cong-tac-sinh-vien/thu-tuc-hanh-chinh-dich-vu-ho-tro/) |
| 5 | [Quy định – Quy chế công tác sinh viên](05-quy-dinh-quy-che.md) | Quy định | [Xem](https://usth.edu.vn/cong-tac-sinh-vien/dich-vu-ho-tro-cong-tac-sinh-vien/quy-dinh-quy-che/) |
| 6 | [Thông tin khu lưu trú (ký túc xá) sinh viên](06-ky-tuc-xa-sinh-vien.md) | Ký túc xá | [Xem](https://usth.edu.vn/cong-tac-sinh-vien/dich-vu-ho-tro-cong-tac-sinh-vien/ky-tuc-xa-sinh-vien/) |
| 7 | [Chăm sóc sức khỏe sinh viên](07-cham-soc-suc-khoe.md) | Y tế, BHYT | [Xem](https://usth.edu.vn/cong-tac-sinh-vien/dich-vu-ho-tro-cong-tac-sinh-vien/cham-soc-suc-khoe/) |
| 8 | [Thư viện USTH](08-thu-vien.md) | Thư viện | [Xem](https://usth.edu.vn/thu-vien-8449/) |
| 9 | [Hướng dẫn đăng ký học phần (Block 3)](09-huong-dan-dang-ky-hoc-phan.md) | Đăng ký học phần | [Xem](https://usth.edu.vn/huong-dan-dang-ky-hoc-phan-block-3-28717/) |

## Quy ước cấu trúc

- Mỗi file `.md` có YAML front matter (`doc_id`, `title`, `audience`, `department`, `category`, `language`, `source_url`, `retrieved_at`, `document_version`) để nạp trực tiếp bằng `build_knowledge_base()` trong `ingest.py`.
- `#`: tên tài liệu; `##`: phần lớn (Nội dung, Thông tin liên hệ, Ghi chú); `###`/`####`: mục và tiểu mục.

## Lưu ý dữ liệu

- USTH (Trường Đại học Khoa học và Công nghệ Hà Nội) là một cơ sở giáo dục **khác** với HUST (Đại học Bách khoa Hà Nội) — hai bộ dữ liệu `usth-so-tay-sv/` và `hust-so-tay-sv-21-markdown/` không nên bị trộn lẫn khi phân tích/so sánh theo trường.
- Nội dung mỗi tài liệu là bản tổng hợp, làm sạch từ trang công khai tương ứng tại thời điểm truy cập (2026-08-03), không phải bản sao HTML nguyên văn.
- Học phí, số suất học bổng, lịch đăng ký học phần và các mốc thời gian có thể đã thay đổi so với thời điểm truy cập — cần đối chiếu lại trang usth.edu.vn trước khi dùng cho quyết định hiện tại.
