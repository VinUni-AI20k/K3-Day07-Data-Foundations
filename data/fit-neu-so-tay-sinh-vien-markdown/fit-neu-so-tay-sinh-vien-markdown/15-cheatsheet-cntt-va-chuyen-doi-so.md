# Công nghệ thông tin và Chuyển đổi số — Cheatsheet sinh viên

## Thông tin tài liệu

- **Nguồn:** https://fit.neu.edu.vn/cheatsheets/cong-nghe-thong-tin-va-chuyen-doi-so
- **Loại tài liệu:** Cheatsheet chuyên ngành
- **Thời điểm đối chiếu:** 2026-08-03T11:24:00+07:00
- **Phương pháp:** Tóm lược có cấu trúc từ nội dung công khai; giữ các điều kiện, mốc, ngưỡng, quy trình và thuật ngữ quan trọng.

## Nội dung

### 1. Nền tảng lập trình

- Dữ liệu số, kiến trúc máy tính, thuật toán và độ phức tạp.
- C: kiểu dữ liệu, flow control, hàm, con trỏ, cấp phát bộ nhớ và file I/O.
- CTDL–GT: array, linked list, BST, hash table, stack, queue, tree, heap và sorting.
- OOP: đóng gói, kế thừa, đa hình, trừu tượng, constructor/destructor và virtual function.

### 2. Hệ thống máy tính và hạ tầng

- Hệ điều hành: process, thread, scheduling, race, mutex, semaphore, deadlock, paging và virtual memory.
- Kiến trúc: register/cache/RAM, pipeline IF–ID–EX–MEM–WB, hazard, RISC/CISC, SIMD, superscalar và out-of-order.
- Ảo hóa: hypervisor loại 1/2, Docker, Kubernetes, image, volume, pod, service, deployment và ingress.
- Cloud: IaaS, PaaS, SaaS; EC2, S3, RDS; auto-scaling, load balancing, CDN và multi-region.

### 3. Mạng và bảo mật

- OSI/TCP-IP với HTTP/S, FTP, SMTP, DNS, SSL/TLS, TCP/UDP/SCTP/QUIC, IP/ICMP/ARP/OSPF và Ethernet/Wi-Fi.
- CIDR, IPv4/IPv6, private IP, TCP flow/congestion control, RIP/OSPF/EIGRP/BGP/IS-IS và QoS.
- Mật mã: AES/ChaCha20, RSA/ECC, SHA-256/512, Argon2, HMAC/CMAC/Poly1305.
- Tấn công: SQLi, XSS, CSRF, XXE, DDoS, MitM, ARP spoofing, buffer overflow, ROP và social engineering.
- Phòng thủ: WAF, IDS/IPS, SIEM, SOC, SOAR, EDR/XDR và Zero Trust.
- An ninh mạng: NIST CSF, ISO 27001/27002, CIS Controls, MITRE ATT&CK, threat intelligence và incident response.
- Cloud security: shared responsibility, federation, HSM/KMS và compliance.
- IoT: MQTT, CoAP, LoRaWAN, Zigbee, BLE, NB-IoT, Arduino/ESP/Raspberry Pi/STM32; edge–fog–cloud và digital twin.

### 4. Cơ sở dữ liệu và quản trị dữ liệu

- ER, relational model, key, SQL DDL/DML/DCL, normalization 1NF–BCNF và join.
- ACID, B-tree/B+tree/hash/bitmap/GiST/GIN, 2PL, timestamp, optimistic và MVCC.
- Recovery bằng log, checkpoint, ARIES và query optimization.
- KDD: cleaning, integration, mining và evaluation; classification, clustering, association và regression.
- Phân tích dữ liệu với pandas, NumPy, Matplotlib, Seaborn và scikit-learn.

### 5. Phát triển ứng dụng web và mobile

- Python: dynamic typing, comprehension, decorator, generator, NumPy/Pandas/Requests/BeautifulSoup, Django/Flask/FastAPI/Celery/SQLAlchemy.
- Java: Spring Boot, REST controller, service/repository, JPA, Security, DI, AOP, microservices, lambda, stream và testing.
- Web: HTML5, CSS Grid/Flexbox, JavaScript ES6+, React/Vue/Angular/Next/Nuxt, Node/Laravel/Django, REST, GraphQL và WebSocket.
- Kiến trúc web: PWA, SPA, SSR, SSG, micro-frontend và Web Components.
- Security: XSS, CSRF, SQLi, HTTPS, JWT, OAuth 2.0, CSP và CORS.
- SOA/Microservices: discovery, API gateway, circuit breaker, saga, REST/gRPC, RabbitMQ/Kafka và service mesh.

### 6. Phân tích dữ liệu và trực quan hóa

- KDD mở rộng: selection, preprocessing, transformation, mining và interpretation.
- Classification: ID3/C4.5/CART, random forest, SVM, neural network và Naive Bayes.
- Clustering: k-means, DBSCAN, hierarchical, GMM, mean shift và spectral.
- Association: Apriori, FP-Growth, Eclat và sequential pattern.
- Data cleaning: missing value, outlier, duplicate, datatype và encoding.
- Feature engineering: scaling, encoding, binning, polynomial và interaction.
- Thư viện: pandas, NumPy, SciPy, statsmodels, scikit-learn, Polars và Dask.
- Time series:
  + Trend, seasonality, cycle, irregular và stationarity.
  + ARIMA/SARIMA/VAR/GARCH/exponential smoothing.
  + Prophet, LSTM, GRU, Transformer, N-BEATS và Temporal Fusion Transformer.
- Trực quan hóa: bar, line, scatter, heatmap, box, violin, Sankey và treemap; Matplotlib, Seaborn, Plotly, D3, Tableau, Power BI và Grafana.
- Nguyên tắc: data-ink ratio, lý thuyết màu, Gestalt và accessibility; dashboard với Streamlit, Dash hoặc Panel.

### 7. Phân tích, thiết kế và quản lý dự án

- UML structure/behavior, design pattern và SDLC Waterfall/Iterative/Spiral/Agile/DevOps.
- Functional/NFR, use case và user story.
- System design: modularity, loose coupling, high cohesion, separation of concerns và SOLID.
- BA: SWOT, BPMN, DFD, use case; elicitation và tài liệu BRD/FRD/TRD/SRS.
- Quản lý dự án: initiation, planning, execution, monitoring/control và closing; 10 vùng kiến thức.
- Ước lượng expert, analogous, parametric, three-point, function point và story point.
- Scrum, Critical Path, Gantt, burndown, Kanban, Jira và Trello.

### 8. Chuyển đổi số và trí tuệ nhân tạo

#### Chuyển đổi số

- Trụ cột: chiến lược, văn hóa, quy trình, công nghệ, dữ liệu và khách hàng.
- Công nghệ: cloud, IoT, AI/ML, blockchain, RPA, AR/VR, 5G, API economy và edge.
- Maturity model: initial → managed → defined → quantified → optimizing.
- Change management: cam kết lãnh đạo, đào tạo, truyền thông, quick win và cải tiến liên tục.
- KPI được trang nguồn gợi ý: adoption rate, ROI, CAC, CLV và NPS.
- Framework: TOGAF, Zachman, McKinsey 7S, Business Model Canvas, Value Chain và Digital Maturity Assessment.

#### Chiến lược số

- Vision → assessment → roadmap → implementation → monitoring.
- Mô hình kinh doanh: platform, subscription, freemium, marketplace và ecosystem.
- Đổi mới: disruptive, sustaining, open innovation và design thinking.
- Yếu tố thành công: leadership, agility, customer-centric, data-driven và continuous learning.

#### AI trong kinh doanh

- Customer service: chatbot/NLP để hỗ trợ 24/7 và giảm chi phí.
- Sales forecast: time series/ML để tăng độ chính xác và giảm tồn kho.
- Fraud detection: anomaly detection để giảm rủi ro.
- Recommendation: collaborative filtering để tăng doanh thu và tương tác.
- Ví dụ bài toán: dự đoán churn và xác suất rời bỏ khách hàng.

#### Tài chính số

- FinTech: digital banking, mobile payment, P2P lending và robo-advisor.
- Blockchain: cryptocurrency, smart contract, DeFi, NFT và CBDC.
- Open banking API, RegTech, InsurTech và xác thực sinh trắc.
- Quy định/chuẩn được nêu: PSD2, GDPR, KYC/AML, Basel III và các chuẩn an ninh mạng.
