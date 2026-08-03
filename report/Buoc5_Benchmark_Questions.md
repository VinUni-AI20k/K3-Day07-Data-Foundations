# Kết Quả Bước 5 - Chốt 5 Câu Hỏi Benchmark

**Ngày thực hiện:** 03/08/2026  
**Nhóm:** K3 Day 07  
**Thành viên phụ trách:** Nguyễn Đào Nam Hải và Nhóm trưởng Nguyễn Xuân Phượng

## Mục tiêu

Chốt 5 câu hỏi benchmark đa dạng, có thể kiểm chứng từ corpus `data/k3_university/`, đồng thời đảm bảo có ít nhất 1 câu cần lọc metadata để tăng độ chính xác.

## 5 câu hỏi benchmark

| # | Loại câu hỏi | Query | Gold answer | File chứa thông tin | Filter gợi ý |
|---|---|---|---|---|---|
| 1 | Quy trình | Sinh viên đăng ký học phần ở hệ thống nào và cần kiểm tra gì sau khi hoàn tất? | Sinh viên đăng ký học phần trên SIS và sau khi hoàn tất cần kiểm tra lại trạng thái đăng ký trong thời khóa biểu cá nhân. | `vinuni-course-registration` | `audience: student` |
| 2 | Xử lý lỗi | Nếu một môn chưa hiển thị, có xung đột lịch hoặc báo lỗi tiên quyết, sinh viên cần làm gì? | Sinh viên cần kiểm tra điều kiện môn học và liên hệ Văn phòng Đăng ký nếu mình đủ điều kiện nhưng hệ thống vẫn chặn; các trường hợp đặc biệt phải gửi yêu cầu riêng theo hướng dẫn của Registrar. | `vinuni-course-registration` | `audience: student` |
| 3 | Thời hạn | Đến ngày làm việc thứ mấy của học kỳ chính sinh viên còn được thêm học phần? | Sinh viên được phép thêm học phần chậm nhất đến hết ngày làm việc thứ 10 của học kỳ chính. | `vinuni-academic-regulations-add-drop` | `audience: student` |
| 4 | Số lượng / điều kiện | Sinh viên bậc đại học được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn như thế nào? | Sinh viên bậc đại học được mượn tối đa 3 tài liệu, mỗi tài liệu trong 2 tuần; sách có thể được gia hạn một lần thêm 1 tuần nếu chưa quá hạn và chưa có người khác đặt giữ. | `vinuni-library-borrowing-undergraduate` | `audience: student` |
| 5 | Chính sách truy cập | Quy định truy cập thư viện cho biết ai được vào thư viện và sử dụng tài nguyên điện tử? | Chỉ sinh viên, giảng viên và nhân viên có thẻ VinUni hợp lệ mới được vào thư viện, mượn tài liệu và sử dụng tài nguyên điện tử. | `vinuni-library-access-policy` | `audience: all` |

## Kết luận

Benchmark này đủ đa dạng để kiểm tra:
- truy xuất theo quy trình
- truy xuất theo điều kiện / lỗi
- truy xuất theo số lượng và thời hạn
- truy xuất theo chính sách truy cập

Ít nhất 1 câu hỏi có thể dùng metadata filtering để tăng độ chính xác, đặc biệt là câu 2 với `audience: student`.

