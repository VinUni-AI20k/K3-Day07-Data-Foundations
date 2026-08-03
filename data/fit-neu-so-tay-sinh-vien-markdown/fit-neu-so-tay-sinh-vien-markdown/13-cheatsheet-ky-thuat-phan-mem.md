# Kỹ thuật phần mềm — Cheatsheet sinh viên

## Thông tin tài liệu

- **Nguồn:** https://fit.neu.edu.vn/cheatsheets/ky-thuat-phan-mem
- **Loại tài liệu:** Cheatsheet chuyên ngành
- **Thời điểm đối chiếu:** 2026-08-03T11:24:00+07:00
- **Phương pháp:** Tóm lược có cấu trúc từ nội dung công khai; giữ các điều kiện, mốc, ngưỡng, quy trình và thuật ngữ quan trọng.

## Nội dung

### 1. Kiến thức nền tảng

- Dữ liệu số, kiến trúc máy tính, thuật toán, C/Java/Python, biên dịch và IDE.
- AI nhập môn: dataset, train/test, mô hình ML/DL đơn giản.
- CTDL: mảng, linked list, stack, queue, tree và graph.
- Hệ điều hành: process, thread, memory, file system và scheduling.
- Mạng: TCP/IP, IP, DNS, HTTP/HTTPS, LAN/WAN.
- Kỹ năng công cụ: Office, debug, Git và command line.
- CTDL–GT: độ phức tạp thao tác trên array, linked list, BST và hash table; sort O(n²) và O(n log n).
- OOP: bốn tính chất, virtual function, SOLID, DRY, KISS và YAGNI.

### 2. Cơ sở lập trình và phương pháp tính

#### Cơ sở lập trình C

- Kiểu dữ liệu, biến, toán tử và ép kiểu.
- I/O có kiểm tra lỗi.
- Rẽ nhánh, vòng lặp, hàm và đệ quy.
- Con trỏ, mảng 1D/2D, chuỗi kết thúc null.
- Struct/union và file I/O.

#### Phương pháp tính

- Sai số tuyệt đối, tương đối và quy tròn.
- Nội suy Lagrange/Newton.
- Bình phương tối thiểu.
- Đạo hàm số bằng sai phân.
- Tích phân hình thang và Simpson.
- Giải phương trình bằng chia đôi/Newton.
- Hệ tuyến tính bằng khử Gauss và pivoting.
- ODE bằng Euler và RK4.

### 3. OOP và hệ điều hành

#### OOP nâng cao

- Lớp, đối tượng và phạm vi truy cập.
- Constructor/destructor, static và friend.
- Interface/implementation, kế thừa và đa hình.
- Template, stream/file và exception.

#### Hệ điều hành

- Dịch vụ hệ điều hành và system call.
- Process, thread, PCB/TCB và lập lịch CPU.
- IPC: pipe, shared memory và socket.
- Đồng bộ: mutex, semaphore và monitor.
- Deadlock, paging, virtual memory, TLB, inode và quản lý I/O/RAID.
- Bảo vệ bằng quyền, ACL và sandbox.

### 4. Bảo mật phần mềm, CSDL và cloud

#### Bảo mật phần mềm và cơ sở dữ liệu

- CIA, quyền tối thiểu và phân tách nhiệm vụ.
- Role, view, row-level security, audit và masking.
- Mã hóa TDE/cột; mật khẩu với bcrypt hoặc Argon2.
- OWASP Top 10 và prepared statement.
- Log, SIEM, cảnh báo và phát hiện bất thường.
- IRP, BCP, DRP, RPO và RTO.
- Zero Trust, micro-segmentation, IDS/IPS, CSRF token, CSP và quản lý secrets.

#### Điện toán đám mây

- IaaS/PaaS/SaaS và public/private/hybrid.
- Hadoop/HDFS/YARN; object storage và block storage.
- Docker/Kubernetes: deployment, service và ingress.
- Observability: log, metric và trace.
- Tối ưu chi phí: lifecycle, spot/savings và right-sizing.
- Bảo mật: IAM, VPC, security group, KMS và mã hóa.

### 5. Hệ quản trị CSDL và kiểm thử chất lượng

#### Hệ quản trị CSDL

- Chuẩn hóa 1NF–3NF và cân nhắc denormalization.
- DDL/DML/DQL, view, procedure và trigger.
- B-tree, covering/composite index, clustered/non-clustered.
- ACID, isolation, deadlock, backup và restore.
- EXPLAIN/plan, statistics, partitioning và tối ưu join.
- Role, row-level permission, audit và masking.
- Kỹ thuật SQL mở rộng: CTE, window function và lịch backup full/diff/log.

#### Kiểm thử và đảm bảo chất lượng

- QA xuyên suốt SDLC, test strategy và risk-based testing.
- Black-box, white-box và test pyramid từ unit đến UI.
- Automation trong CI/CD, mock/stub, test data và report.
- Kiểm thử phi chức năng: performance, security, usability và accessibility.
- Quản lý lỗi theo lifecycle, severity, priority và MTTR.
- Boundary/equivalence, API contract, idempotency, P95/P99, authn/authz, XSS và SQLi.
- Unit, integration, regression và end-to-end testing.

### 6. Python và lập trình ứng dụng

#### Python

- Kiểu dữ liệu, flow control, hàm/module và OOP.
- File I/O, NumPy, Pandas và Matplotlib.
- ETL, trực quan hóa và xử lý ngoại lệ.
- List comprehension, async, venv và pytest.

#### Ứng dụng C#/.NET

- Windows Forms và các control.
- Event, binding, ADO.NET/Entity Framework và CRUD.
- Tìm kiếm, lọc và báo cáo.
- Tổ chức solution, namespace và class trong dự án quản lý có giao diện.

### 7. Phân tích nghiệp vụ và thiết kế hệ thống

#### Phân tích nghiệp vụ

- BA làm cầu nối nghiệp vụ–kỹ thuật và quản lý stakeholder.
- Elicitation bằng phỏng vấn, workshop, khảo sát, quan sát, prototype và shadowing.
- Traceability, versioning, change control và impact analysis.
- Functional requirement và NFR về security, performance, UX, accessibility.
- Ưu tiên bằng MoSCoW, Kano hoặc WSJF.
- Tài liệu: BRD, SRS, backlog, story, use case và glossary.
- Acceptance criteria theo Given–When–Then; change request phải nêu lý do, tác động, ước lượng và quyết định.

#### Phân tích và thiết kế hệ thống

- Quy trình khảo sát → phân tích → thiết kế → triển khai → vận hành → bảo trì.
- UML: use case, class, sequence, activity, state, component và deployment.
- Kiến trúc layered, hexagonal, microservices, event-driven; sync và async.
- API REST/OpenAPI, idempotency, pagination và versioning.
- ERD, khóa, index, transaction, isolation và cache.
- SOLID, GRASP, DDD, SLO/SLA/SLI và observability.
- CI/CD, môi trường dev/staging/prod, config, secrets và feature flag.

### 8. Kỹ thuật phần mềm

#### Kiến trúc phần mềm

- Monolith, microservices, event-driven và serverless.
- REST/OpenAPI, idempotency, pagination và versioning.
- CQRS, Event Sourcing, cache TTL/eviction.
- Log/metric/trace và feature flag.
- Scalability, availability, resilience và security.
- Retry/backoff, circuit breaker, bulkhead, saga, outbox/inbox và transaction phân tán.
- IaC, container, orchestrator, blue/green, canary và rollback.

#### Quản lý dự án phần mềm

- WBS, function point, story point và Gantt.
- Burndown, velocity và EVM với PV/EV/AC, CPI/SPI.
- Quản lý rủi ro, RACI, communication plan và stakeholder.
- QA plan, audit và retrospective.
- Backlog ưu tiên bằng MoSCoW/WSJF/Kano; scope baseline và change control.
- Loại hợp đồng: time-and-material, fixed-price và milestone.

#### DevOps và CI/CD

- CI: lint, build, test, static analysis và artifact.
- CD: promotion qua môi trường, blue/green, canary và rollback.
- Container registry, IaC và secret management.
- Observability, alerting và SRE runbook.
- SAST, DAST, SBOM, signing và policy-as-code.
- Artifact bất biến, SemVer, Kubernetes deployment/service/ingress/HPA và FinOps.
