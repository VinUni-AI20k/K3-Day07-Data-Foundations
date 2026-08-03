# Khoa học máy tính — Cheatsheet sinh viên

## Thông tin tài liệu

- **Nguồn:** https://fit.neu.edu.vn/cheatsheets/khoa-hoc-may-tinh
- **Loại tài liệu:** Cheatsheet chuyên ngành
- **Thời điểm đối chiếu:** 2026-08-03T11:24:00+07:00
- **Phương pháp:** Tóm lược có cấu trúc từ nội dung công khai; giữ các điều kiện, mốc, ngưỡng, quy trình và thuật ngữ quan trọng.

## Nội dung

### 1. Nền tảng lập trình

- Biểu diễn dữ liệu, IEEE 754, ASCII/Unicode và kiến trúc Von Neumann.
- C: kiểu dữ liệu, điều khiển, con trỏ, cấp phát bộ nhớ và lỗi bộ nhớ.
- CTDL–GT: array, linked list, BST, hash table, stack, queue, AVL, red-black, B-tree, heap và các nhóm sort.
- OOP: đóng gói, kế thừa, đa hình, trừu tượng, constructor/destructor, virtual function, SOLID/DRY/KISS/YAGNI.
- Python cơ bản và đệ quy.

### 2. Hệ điều hành và kiến trúc máy tính

- Process tạo bằng fork/exec/wait; trạng thái từ new đến terminated.
- Lập lịch FCFS, SJF, Round Robin và priority; thread chia sẻ code/data.
- Đồng bộ semaphore/mutex; deadlock và các phương án ngăn ngừa, tránh, phát hiện, phục hồi.
- Virtual memory, page, offset, TLB, page fault; FIFO, LRU và Clock.
- Pipeline IF–ID–EX–MEM–WB; cache L1/L2/L3/RAM và locality.
- RISC/CISC, Amdahl, CPI, clock và instruction count.
- File permission, SUID, inode, polling, interrupt và DMA.

### 3. Mạng máy tính và bảo mật mạng

- TCP/IP và OSI; HTTP, DNS, SMTP, TCP, UDP, IP, ICMP, ARP, Ethernet và Wi-Fi.
- Truyền dữ liệu: Shannon, CRC, NRZ, Manchester, ASK, FSK, PSK và QAM.
- IPv4/IPv6, subnet, VLSM và các dải private IP.
- Mật mã: không dùng DES/MD5; ưu tiên AES, SHA-256 và RSA 2048+.
- Chữ ký số: hash, ký bằng private key và xác minh bằng public key.
- TLS, PKI, CA, certificate chain và VPN IPSec/OpenVPN/WireGuard.

### 4. Cơ sở dữ liệu và quản trị dữ liệu

- Mô hình quan hệ, khóa chính/ngoại/ứng viên/tổng hợp/siêu khóa.
- Quan hệ 1:1, 1:N, N:N, đệ quy và ISA.
- Phụ thuộc hàm và ràng buộc thực thể, tham chiếu, miền và kiểm tra.
- Chuẩn hóa 1NF, 2NF, 3NF, BCNF; denormalization khi tối ưu đọc.
- Index B-tree, hash, bitmap, full-text, GiST, GIN; composite và covering index; partition.
- SQL processing, join algorithm, cost-based optimization, statistics và cardinality.
- ACID, isolation, lock S/X, 2PL, timestamp và MVCC; dị thường dirty/non-repeatable/phantom/lost update.
- NoSQL:
  + Document như MongoDB.
  + Key-value như Redis.
  + Wide-column như Cassandra.
- CAP, BASE, sharding, replication, eventual consistency và quorum.

### 5. Phát triển web và mobile

- Frontend hiện đại: SPA, PWA, SSR, SSG, ISR và Jamstack.
- State management: Context, Redux, MobX, Zustand, Recoil và Jotai.
- Hiệu năng: lazy loading, code splitting, tree shaking, CDN và service worker.
- Backend: MVC, clean/hexagonal architecture, REST, GraphQL, gRPC, WebSocket, SSE và WebRTC.
- Middleware: auth, logging, rate limit, CORS, compression và cache.
- Microservices, serverless, BFF, API gateway và event-driven.
- Security: session/JWT/OAuth/SAML/OIDC/passkey; CSP, HSTS và chống XSS/CSRF/SQLi/XXE/SSRF/RCE/path traversal.
- Mobile: native và cross-platform; React Native, Flutter, push notification và deep link.
- DevOps: Jenkins, GitLab CI, GitHub Actions, ArgoCD, Prometheus, Grafana, ELK, blue-green, canary và GitOps.

### 6. Phân tích và thiết kế hệ thống

- Waterfall, Agile/Scrum và DevOps; Scrum role/artifact/event, Kanban WIP và continuous flow.
- UML: cấu trúc, hành vi và các quan hệ association/aggregation/composition/generalization.
- SDLC từ yêu cầu đến bảo trì.
- Design pattern: Singleton, Factory, Adapter, Decorator, Observer và Strategy.
- Nguyên tắc SOLID, DRY, KISS, YAGNI, composition over inheritance, IoC và DI.
- Quản lý dự án: scope–time–cost–quality, risk matrix, EMV, Monte Carlo, PERT, Function Point, COCOMO II, WBS, Gantt và Critical Path.
- Kiểm thử: unit, integration, system, UAT, alpha/beta; black/white/grey box; test pyramid 70/20/10, TDD, BDD và mutation/contract testing.

### 7. Trí tuệ nhân tạo và khoa học dữ liệu

- Supervised, unsupervised và reinforcement learning.
- Vấn đề overfitting/underfitting; regularization, cross-validation, dropout và feature engineering.
- Thuật toán: linear/logistic/ridge/lasso, SVM, Naive Bayes, tree, random forest, XGBoost, LightGBM, k-NN, k-means, DBSCAN và GMM.
- Metrics: accuracy, precision, recall, F1, ROC-AUC, MSE, MAE và R².
- KDD/CRISP-DM/SEMMA; association, classification, clustering và prediction.
- Deep learning:
  + CNN cho computer vision.
  + RNN/LSTM cho dữ liệu chuỗi.
  + Transformer cho NLP và vision.
- Optimizer: SGD, Adam, AdamW, RMSprop; regularization L1/L2, batch norm và augmentation.
- Big Data: Hadoop, Spark, Kafka, Flink và Storm; 5V; Lambda và Kappa architecture.

### 8. Công nghệ hiện đại và nâng cao

- Cloud: IaaS/PaaS/SaaS, Docker, Kubernetes, OpenShift, Rancher, K3s, Terraform, Ansible, Helm, operator và GitOps.
- Microservices/SOA: API gateway, service mesh, saga, CQRS, Event Sourcing, REST/gRPC/message queue/event bus, discovery và circuit breaker.
- Computer graphics: transform, MVP matrix, rasterization, ray tracing, WebGL, Three.js, Unity/Unreal và shader.
- Computer vision: detection, classification, segmentation, tracking và OCR; YOLO, Faster R-CNN, U-Net, ViT, CLIP, OpenCV và MediaPipe.
- BI/DSS: ETL, data warehouse, OLAP, dashboard, descriptive/diagnostic/predictive/prescriptive analytics, star/snowflake, KPI, Balanced Scorecard, Power BI và Tableau.
