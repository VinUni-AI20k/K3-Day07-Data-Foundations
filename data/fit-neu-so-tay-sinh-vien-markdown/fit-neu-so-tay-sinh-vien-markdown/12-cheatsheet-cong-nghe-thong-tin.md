# Công nghệ thông tin — Cheatsheet sinh viên

## Thông tin tài liệu

- **Nguồn:** https://fit.neu.edu.vn/cheatsheets/cong-nghe-thong-tin
- **Loại tài liệu:** Cheatsheet chuyên ngành
- **Thời điểm đối chiếu:** 2026-08-03T11:24:00+07:00
- **Phương pháp:** Tóm lược có cấu trúc từ nội dung công khai; giữ các điều kiện, mốc, ngưỡng, quy trình và thuật ngữ quan trọng.

## Nội dung

### 1. Nền tảng lập trình

#### Nhập môn CNTT và C

- Biểu diễn dữ liệu: nhị phân, bát phân, thập lục phân, bù hai, IEEE 754 và Unicode.
- Tổ chức máy tính: CPU, ALU, CU, thanh ghi, phân cấp bộ nhớ, bus và kiến trúc Von Neumann.
- Thuật toán cần đảm bảo tính đúng, dừng, xác định, phổ dụng và được phân tích độ phức tạp.
- C:
  + Kiểu số, ký tự, mảng và chuỗi.
  + Rẽ nhánh, vòng lặp và hàm.
  + Con trỏ, cấp phát/giải phóng bộ nhớ.
  + Tránh buffer overflow, memory leak và dangling pointer.

#### Cấu trúc dữ liệu và giải thuật

- Mảng: truy cập nhanh nhưng chèn/xóa thường O(n).
- Danh sách liên kết: chèn/xóa đầu O(1), tìm kiếm O(n).
- BST cân bằng: thao tác trung bình O(log n).
- Hash table: trung bình O(1) cho tra cứu bằng khóa.
- Cấu trúc: stack, queue, deque, cây nhị phân, AVL, red-black, B-tree và heap.
- Sắp xếp: nhóm O(n²) và nhóm O(n log n) như quick/merge/heap sort.

#### OOP

- Đóng gói, kế thừa, đa hình và trừu tượng.
- Constructor/destructor, static member và virtual function.
- Nguyên tắc SOLID, DRY, KISS và YAGNI.

### 2. Hệ thống máy tính và hạ tầng

#### Hệ điều hành

- Process, thread, PCB, thread pool và mô hình ánh xạ luồng.
- Lập lịch FCFS, SJF, Round Robin, ưu tiên và đa cấp.
- Đồng bộ bằng mutex, semaphore, monitor; nhận diện race condition và deadlock.
- Bộ nhớ: paging, segmentation, virtual memory và page replacement.

#### Kiến trúc máy tính

- Phân cấp: register → L1 → L2 → RAM; càng gần CPU càng nhanh và nhỏ.
- Pipeline 5 giai đoạn: IF, ID, EX, MEM, WB.
- Hazard: structural, data RAW/WAR/WAW và control.

#### Ảo hóa và cloud

- Ảo hóa đầy đủ, para-virtualization, hỗ trợ phần cứng và container.
- Hypervisor loại 1 và loại 2.
- Docker, Kubernetes, image, volume, pod, service, deployment, config map và ingress.
- Dịch vụ cloud:
  + IaaS: máy ảo và lưu trữ.
  + PaaS: runtime/nền tảng.
  + SaaS: ứng dụng hoàn chỉnh.
- AWS được dùng làm ví dụ với EC2, S3 và RDS; mẫu vận hành gồm auto-scaling, load balancing, CDN và multi-region.

### 3. Mạng máy tính và bảo mật

- OSI/TCP-IP: application, transport, internet/network access; giao thức HTTP, FTP, DNS, TCP, UDP, IP, ICMP, ARP và Ethernet.
- Dải IP riêng: 10/8, 172.16/12 và 192.168/16.
- TCP tin cậy và có kiểm soát luồng; UDP nhanh, không đảm bảo, phù hợp DNS/DHCP/VoIP.
- Routing: static, RIP, OSPF và BGP.
- Quản trị mạng:
  + VLAN, trunk, STP, VTP và EtherChannel.
  + OSPF area, BGP AS, EIGRP và policy route.
  + SNMP, NetFlow, Syslog, Nagios, Zabbix.
  + QoS, shaping, policing, DSCP và priority queue.
- Bảo mật:
  + AES/RSA/ECC, SHA-256/bcrypt và PKI.
  + SQLi, XSS, CSRF, DDoS, MitM, buffer overflow và phishing.
  + Firewall, IDS/IPS, WAF, SIEM và Zero Trust.
  + Chuẩn ISO 27001, NIST, OWASP Top 10 và PCI DSS.
- IoT: MQTT, CoAP, LoRaWAN, Zigbee, BLE, NB-IoT, Arduino, ESP và Raspberry Pi; kiến trúc edge/fog/cloud và digital twin.

### 4. Cơ sở dữ liệu và quản trị dữ liệu

- ER: entity, attribute và quan hệ 1:1, 1:N, M:N.
- Mô hình quan hệ: bảng và các loại khóa.
- SQL: DDL, DML, DCL, join và truy vấn nhóm/tổng hợp.
- Chuẩn hóa 1NF, 2NF, 3NF và BCNF.
- ACID:
  + Atomicity: toàn bộ hoặc không.
  + Consistency: trạng thái hợp lệ.
  + Isolation: kiểm soát đồng thời.
  + Durability: dữ liệu bền vững.
- Index: B-tree/B+tree, hash, bitmap, GiST và GIN.
- Concurrency: 2PL, timestamp, optimistic và MVCC.
- Recovery: log, shadow paging, ARIES và checkpoint.
- Khai phá dữ liệu: KDD, classification, clustering, association và regression; thuật toán decision tree, k-means, Apriori và neural network.
- Phân tích với pandas, NumPy, Matplotlib, Seaborn và scikit-learn.

### 5. Phát triển ứng dụng web

- HTML5, CSS3 Flexbox/Grid, JavaScript ES6+, DOM, Promise và async/await.
- Thiết kế responsive theo mobile-first.
- Backend: Node/Express, PHP/Laravel, Python/Django/FastAPI, Java/Spring Boot, Ruby/Rails và ASP.NET Core.
- API: REST, GraphQL, WebSocket, gRPC và OpenAPI.
- Xác thực: session, JWT, OAuth 2.0, OpenID Connect, SAML và MFA.
- CSDL: MySQL, PostgreSQL, MSSQL, MongoDB, Redis, Cassandra và ORM/ODM.
- Bảo mật: xác thực đầu vào, chống XSS/CSRF và HTTPS.
- Thương mại điện tử: B2C, B2B, C2C, O2O, subscription; catalog, cart, payment, order tracking, PCI DSS và chống gian lận.
- Java/Spring: controller, JPA, Maven và microservices.

### 6. Ứng dụng di động và đa phương tiện

- Android: Kotlin/Java, Activity, Fragment, Service, lifecycle và Room.
- iOS: Swift, UIViewController/SwiftUI, Auto Layout và Core Data.
- Cross-platform: Flutter và React Native.
- Lưu trữ: preferences, SQLite, Room/Core Data, Firebase và Realm.
- Networking: Retrofit, Alamofire, REST và WebSocket.
- Kiểm thử và phát hành qua Google Play/App Store.
- Đa phương tiện:
  + Audio: sampling rate, bit depth, lossless/lossy codec.
  + Video: frame rate, độ phân giải, H.264/H.265, VP9, AV1, MP4/MKV/WebM.
  + Streaming: HLS, MPEG-DASH, CDN, DRM và live protocol.
- Xử lý ảnh: filtering, edge detection, morphology, histogram, SIFT/SURF/ORB/HOG; ứng dụng nhận diện mặt, OCR và tracking.

### 7. Phân tích, thiết kế và quản lý dự án

- UML cấu trúc và hành vi; use case, class, sequence, activity, state, component và deployment.
- Design pattern: Singleton, Factory, Builder, Adapter, Decorator, Facade, Observer, Strategy và Command.
- SDLC: Waterfall, Iterative, Spiral, Agile và DevOps.
- Yêu cầu chức năng/phi chức năng, user story và use case.
- Thiết kế hệ thống: module, coupling thấp, cohesion cao, separation of concerns và SOLID.
- Phân tích nghiệp vụ: SWOT, BPMN, DFD và use case; tài liệu BRD, FRD, TRD, SRS.
- Quản lý dự án: khởi tạo, lập kế hoạch, thực hiện, giám sát, kết thúc; phạm vi, lịch, chi phí, chất lượng, nguồn lực, truyền thông và rủi ro.
- Ước lượng: expert, analogous, parametric, three-point, function point và story point.
- Scrum: backlog, sprint, daily, review, retrospective và velocity.
- Công cụ: MS Project, Jira, Trello, Gantt, burndown và Kanban.

### 8. Trí tuệ nhân tạo và công nghệ mới

- Machine learning:
  + Supervised: regression, SVM, random forest.
  + Unsupervised: k-means, DBSCAN, PCA.
  + Reinforcement: Q-learning, DQN, PPO.
  + Deep learning: CNN, RNN và Transformer.
- Pipeline: feature engineering, train/test, accuracy, precision, recall, F1, ROC-AUC và cross-validation.
- Tối ưu mô hình: grid search, random search và Bayesian optimization.
- Framework: TensorFlow, PyTorch và scikit-learn.
- Deep learning: CNN cho ảnh, RNN/LSTM cho chuỗi, Transformer/BERT/GPT/ViT cho NLP và vision.
- Blockchain/Web3: ledger phân tán, PoW/PoS, smart contract, Ethereum, Solidity, IPFS, DeFi, NFT và DAO.
- Big Data: Hadoop, Spark, Kafka và data lake; 5V gồm volume, velocity, variety, veracity và value.
- Công nghệ mới: cloud AI, AutoML, quantum computing, AR/VR, edge AI và 6G.
