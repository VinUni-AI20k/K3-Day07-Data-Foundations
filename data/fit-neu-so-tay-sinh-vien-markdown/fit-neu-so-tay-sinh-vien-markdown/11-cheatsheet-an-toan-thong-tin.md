# An toàn thông tin — Cheatsheet sinh viên

## Thông tin tài liệu

- **Nguồn:** https://fit.neu.edu.vn/cheatsheets/an-toan-thong-tin
- **Loại tài liệu:** Cheatsheet chuyên ngành
- **Thời điểm đối chiếu:** 2026-08-03T11:24:00+07:00
- **Phương pháp:** Tóm lược có cấu trúc từ nội dung công khai; giữ các điều kiện, mốc, ngưỡng, quy trình và thuật ngữ quan trọng.

## Nội dung

### Phạm vi ngành

- Ngành An toàn thông tin, mã ngành 7480202.
- Đơn vị: Khoa Công nghệ thông tin, Trường Công nghệ, Đại học Kinh tế Quốc dân.

### 1. Kiến thức nền tảng CNTT

#### Lập trình C/C++

- Các rủi ro bộ nhớ cần nhận diện:
  + Tràn bộ đệm ở stack hoặc heap.
  + Chuỗi định dạng không an toàn.
  + Tràn số nguyên.
  + Rò rỉ bộ nhớ, dùng sau khi giải phóng và giải phóng hai lần.
  + Điều kiện tranh chấp và TOCTOU.
- Không sử dụng `gets()`; dùng hàm đọc có giới hạn kích thước như `fgets()`.

#### OOP và mẫu thiết kế

- Bốn tính chất: đóng gói, kế thừa, đa hình, trừu tượng.
- Mẫu thường gặp: Singleton, Factory, Observer, Strategy, MVC.
- Áp dụng SOLID cùng nguyên tắc quyền tối thiểu và kiểm soát bề mặt tấn công.

#### Python, Java và Web

- Python: các thư viện được gợi ý gồm Scapy, Paramiko, Cryptography, Requests và BeautifulSoup.
- Java:
  + Dùng `PreparedStatement` để giảm SQL injection.
  + Hiểu JCE, quản lý quyền và rủi ro giải tuần tự đối tượng.
- Web:
  + Frontend: HTML, CSS, JavaScript và các framework phổ biến.
  + Backend: Node.js, PHP, Python hoặc Java.
  + Bảo mật: XSS, CSRF, SQL injection, session, cookie, JWT và OAuth.

#### Cơ sở dữ liệu và cấu trúc dữ liệu

- Truy vấn SQL phải được tham số hóa hoặc đóng gói trong thủ tục lưu trữ.
- Cấu trúc cơ bản: mảng, danh sách liên kết, stack, queue, cây.
- Thuật toán chính: sắp xếp nhanh/trộn/vun đống, tìm kiếm nhị phân, DFS và BFS.

### 2. Hệ điều hành và Linux

#### Nguyên lý hệ điều hành

- Trạng thái tiến trình: mới, sẵn sàng, chạy, đợi, kết thúc.
- Lập lịch: FCFS, SJF, Round Robin, ưu tiên và hàng đợi đa cấp.
- Bộ nhớ: phân trang, phân đoạn, bộ nhớ ảo và thay thế trang.
- Hệ thống tệp: FAT32, NTFS, ext4, journaling và quyền.
- Deadlock liên quan đến bốn điều kiện: loại trừ lẫn nhau, giữ và đợi, không cưỡng đoạt và chờ vòng.

#### Quản trị Linux

- Hiểu quyền `rwx`, SUID, SGID và sticky bit.
- Tệp quan trọng: `/etc/passwd`, `/etc/shadow`, `/etc/sudoers`, `/var/log/*`.
- Công việc quản trị:
  + Xem tiến trình, cổng lắng nghe và dịch vụ.
  + Quản lý `systemd` và nhật ký `journalctl`.
  + Viết shell script để tự động hóa tác vụ lặp lại.

#### Tăng cường bảo mật

- Tắt dịch vụ/cổng không cần thiết.
- Cấu hình firewall, SELinux hoặc AppArmor.
- Dùng fail2ban, auditd và quy trình cập nhật bản vá.
- Mô hình kiểm soát truy cập:
  + DAC: chủ sở hữu quyết định.
  + MAC: hệ thống áp chính sách bắt buộc.
  + RBAC: phân quyền theo vai trò.

### 3. Mạng máy tính và bảo mật mạng

#### TCP/IP và OSI

- Lớp ứng dụng: HTTP, DNS, SMTP; rủi ro injection và lừa đảo.
- Lớp vận chuyển: TCP, UDP; rủi ro SYN flood và quét cổng.
- Lớp mạng: IP, ICMP, ARP; rủi ro giả mạo IP/ARP.
- Lớp liên kết: Ethernet, Wi-Fi; rủi ro MAC flooding.
- TCP dùng bắt tay SYN → SYN-ACK → ACK.

#### Cổng, địa chỉ và VLAN

- Cổng thường gặp: FTP 21, SSH 22, SMTP 25, DNS 53, HTTP 80, HTTPS 443, SMB 445, MSSQL 1433, MySQL 3306, RDP 3389, PostgreSQL 5432.
- Dải IP riêng: 10/8, 172.16/12 và 192.168/16.
- Hiểu subnet CIDR, VLAN 802.1Q, cổng access/trunk, inter-VLAN routing và NAT/PAT.

#### Firewall, IDS/IPS và tấn công mạng

- Firewall:
  + Lọc gói không trạng thái.
  + Theo dõi trạng thái kết nối.
  + Kiểm tra lớp ứng dụng.
  + NGFW tích hợp IPS, chống mã độc và kiểm soát ứng dụng.
- IDS/IPS dùng chữ ký hoặc phát hiện hành vi; công cụ tiêu biểu: Snort, Suricata, Zeek, OSSEC và Wazuh.
- Nhóm tấn công: DoS/DDoS, MitM, giả mạo ARP/DNS, SSL stripping, evil twin và chiếm phiên.
- Phòng thủ: giới hạn tốc độ, SYN cookie, CDN, chống DDoS và phân đoạn mạng.

#### Mạng không dây

- Hiểu WEP, WPA2-PSK, WPA3, WPS, deauthentication, KRACK và evil twin.
- Ưu tiên WPA3 hoặc WPA2 cấu hình mạnh, tắt WPS và giám sát điểm truy cập giả.

### 4. Mật mã học và PKI

#### Mã hóa đối xứng

- DES và 3DES đã lỗi thời.
- AES hỗ trợ khóa 128/192/256 bit; ChaCha20 là lựa chọn hiện đại cho mã dòng.
- Tránh ECB; ưu tiên chế độ có IV và xác thực như GCM hoặc ChaCha20-Poly1305.

#### Mã hóa bất đối xứng

- RSA dựa trên tích hai số nguyên tố; khóa tối thiểu nên từ 2048 bit.
- ECC đạt mức bảo mật tương đương với khóa nhỏ hơn; mức tham khảo 256 bit.
- Diffie–Hellman dùng để thỏa thuận khóa; cần tham số đủ mạnh và xác thực để tránh MitM.

#### Băm, MAC và lưu mật khẩu

- Không dùng MD5 hoặc SHA-1 cho mục đích an toàn.
- Dùng SHA-256/512 cho băm toàn vẹn.
- Dùng HMAC cho xác thực thông điệp.
- Mật khẩu nên dùng bcrypt, scrypt hoặc Argon2id với salt và cost phù hợp.

#### PKI và TLS

- Chứng chỉ X.509 chứa chủ thể, đơn vị cấp, khóa công khai, thuật toán và thời hạn.
- Chuỗi tin cậy gồm CA gốc, CA trung gian và CA phát hành.
- Thu hồi qua CRL hoặc OCSP.
- Ưu tiên TLS 1.2/1.3, bộ mã hiện đại và PFS với ECDHE.

### 5. Bảo mật ứng dụng web

#### OWASP Top 10 năm 2021

- A01: lỗi kiểm soát truy cập.
- A02: lỗi mật mã.
- A03: injection.
- A04: thiết kế không an toàn.
- A05: cấu hình bảo mật sai.
- A06: thành phần có lỗ hổng.
- A07: lỗi nhận dạng và xác thực.
- A08: lỗi toàn vẹn phần mềm/dữ liệu.
- A09: ghi nhật ký và giám sát không đầy đủ.
- A10: SSRF.

#### Phòng SQL injection và XSS

- SQL injection:
  + Không nối chuỗi trực tiếp từ đầu vào người dùng.
  + Dùng prepared statement, stored procedure và kiểm tra đầu vào.
- XSS:
  + Có ba nhóm chính: reflected, stored và DOM-based.
  + Phòng bằng xác thực đầu vào, mã hóa đầu ra và Content Security Policy.

#### Xác thực, phiên và CSRF

- MFA gồm yếu tố kiến thức, sở hữu, sinh trắc hoặc ngữ cảnh.
- OAuth 2.0 nên dùng authorization code; tránh implicit flow cho thiết kế mới.
- Cookie phiên nên bật `HttpOnly`, `Secure` và `SameSite` phù hợp.
- Bật CSRF token, HSTS, CSP và chống nhúng bằng `X-Frame-Options` hoặc `frame-ancestors`.

### 6. Kiểm thử xâm nhập

#### Phương pháp

- Chỉ thực hiện khi có phạm vi và ủy quyền bằng văn bản.
- Các giai đoạn:
  + Lập kế hoạch và quy tắc tham gia.
  + Trinh sát và OSINT.
  + Quét, liệt kê và đánh giá lỗ hổng.
  + Khai thác có kiểm soát.
  + Hậu khai thác trong phạm vi cho phép.
  + Báo cáo, đánh giá rủi ro và khuyến nghị khắc phục.
- Khung tham khảo: PTES, OWASP Testing Guide, NIST SP 800-115 và OSSTMM.

#### Công cụ và phạm vi học tập

- Quét/liệt kê: Nmap, Masscan, Enum4linux, Gobuster.
- Kiểm thử web: Burp Suite, OWASP ZAP, ffuf, Nuclei, Nikto và SQLMap trong phòng lab được phép.
- Framework khai thác: Metasploit cho môi trường thực hành cô lập.
- Leo thang đặc quyền:
  + Linux: SUID, sudo sai cấu hình, cron yếu, kernel hoặc container.
  + Windows: dịch vụ sai cấu hình, DLL hijacking, token và ACL yếu.
- Đánh giá mật khẩu: Hashcat hoặc Hydra chỉ với dữ liệu/hệ thống được cấp phép.

### 7. Vận hành bảo mật và điều tra số

#### Ứng phó sự cố

- Chuẩn bị → Phát hiện/phân tích → Ngăn chặn → Loại bỏ → Phục hồi → Rút kinh nghiệm.
- Khung tham khảo: NIST SP 800-61, SANS, ISO 27035 và ENISA.

#### Điều tra số

- Thu thập theo thứ tự biến mất nhanh: trạng thái CPU, RAM, swap, đĩa và log từ xa.
- Duy trì chuỗi bảo quản, hash và nhật ký người truy cập bằng chứng.
- Công cụ: FTK, EnCase, Autopsy, Volatility, SIFT và Redline.

#### Log và SIEM

- Sự kiện Windows đáng chú ý:
  + 1102: xóa nhật ký kiểm toán.
  + 4624/4625: đăng nhập thành công/thất bại.
  + 4688: tạo tiến trình.
  + 4672: quyền đặc biệt.
  + 7045: cài dịch vụ.
- Nguồn Linux: auth.log, secure, messages và syslog.
- Nền tảng SIEM: Splunk, ELK, QRadar và ArcSight.

#### Phân tích mã độc và threat intelligence

- Phân tích tĩnh: strings, PE, dịch ngược bằng IDA hoặc Ghidra.
- Phân tích động: sandbox, theo dõi API và lưu lượng mạng.
- Threat intelligence: hash, IP, domain, TTP theo MITRE ATT&CK, YARA, MISP và OTX.

### 8. Đám mây và chủ đề nâng cao

#### Mô hình dịch vụ

- IaaS: khách hàng quản lý hệ điều hành, runtime, ứng dụng và dữ liệu.
- PaaS: khách hàng chủ yếu quản lý ứng dụng và dữ liệu.
- SaaS: nhà cung cấp quản lý gần như toàn bộ nền tảng.
- Mô hình triển khai: public, private, hybrid và multi-cloud.

#### Bảo mật cloud

- IAM quyền tối thiểu, MFA, vai trò tạm thời và xoay khóa.
- Mã hóa dữ liệu at-rest bằng KMS và in-transit bằng TLS.
- Phân đoạn VPC, security group, NACL và private subnet.
- Theo dõi bằng CloudTrail/CloudWatch/GuardDuty hoặc dịch vụ tương đương.
- Tuân thủ mô hình trách nhiệm chia sẻ và yêu cầu vị trí dữ liệu.

#### Container, blockchain, AI và DevSecOps

- Container/Kubernetes:
  + Dùng image tối thiểu, người dùng không đặc quyền, filesystem chỉ đọc.
  + Áp dụng RBAC, network policy và chính sách pod.
  + Công cụ quét: Trivy, Clair, Falco và các nền tảng CSPM/CWPP.
- Blockchain: lưu ý 51%, double-spend, reentrancy và front-running.
- AI/ML: adversarial example, data poisoning và model extraction; phòng bằng kiểm tra dữ liệu, hardening và differential privacy.
- DevSecOps:
  + SAST cho mã nguồn.
  + DAST cho ứng dụng chạy.
  + SCA/SBOM cho phụ thuộc.
- Tiêu chuẩn: ISO 27001/27002, NIST CSF, CIS Controls, GDPR, PCI DSS, HIPAA và SOC 2.

### 9. Lộ trình học và chứng chỉ

- Năm 1: C/Python, toán rời rạc, CTDL–GT và Linux.
- Năm 2: mạng, hệ điều hành, CSDL, web và phòng lab ảo.
- Năm 3: mật mã, bảo mật mạng/web, pentest có phép và CTF.
- Năm 4: DFIR, ứng phó sự cố, cloud security, đồ án và thực tập.
- Chứng chỉ gợi ý:
  + Nhập môn: Security+, eJPT, Google Cybersecurity.
  + Tấn công: CEH, OSCP, CPTS, PNPT.
  + Phòng thủ: BTL1, CySA+, GCIH.
  + Nâng cao: OSEP, OSWE, CISSP, OSCE3.
  + Cloud: AWS Security, AZ-500.
- Nền tảng thực hành hợp pháp: TryHackMe, PortSwigger Academy, Hack The Box, VulnHub, Root-Me, OverTheWire, picoCTF và pwn.college.

### 10. Hướng nghề nghiệp

- SOC Analyst.
- Pentester/Red Team có ủy quyền.
- Security Engineer.
- DFIR.
- AppSec/DevSecOps.
- Malware Analyst/Threat Intelligence.
- GRC/Auditor.
- Cloud Security.
- Kỹ năng trọng tâm: Linux, TCP/IP, Python/Bash, đọc log, báo cáo, đạo đức nghề và hồ sơ thực hành công khai phù hợp.

### 11. Pháp luật và đạo đức nghề

- Văn bản được trang nguồn nhắc tới:
  + Luật An toàn thông tin mạng 86/2015/QH13.
  + Luật An ninh mạng 24/2018/QH14.
  + Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân.
  + Bộ luật Hình sự 2015, sửa đổi 2017, các điều về tội phạm mạng.
- Chỉ kiểm thử hệ thống sở hữu hoặc có văn bản cho phép, với phạm vi và quy tắc rõ ràng.
- Không gây thiệt hại, lấy dữ liệu hoặc tiết lộ bí mật.
- Báo cáo lỗ hổng có trách nhiệm; dùng lab cô lập hoặc chương trình bug bounty hợp pháp.
- Nguyên tắc cốt lõi: bí mật, toàn vẹn, sẵn sàng, xác thực, ủy quyền, chống chối bỏ, quyền tối thiểu, phòng thủ nhiều lớp và Zero Trust.
