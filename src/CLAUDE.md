# src/ — Trạng thái triển khai

Ghi chú cho các TODO đã hoàn thành trong Giai đoạn 1 (cá nhân) của Lab 07. Tất cả 42 test trong `tests/test_solution.py` đều PASS (`pytest tests/ -v`).

## chunking.py

- **`SentenceChunker.chunk`** — tách câu bằng `re.split(r"(?<=[.!?])\s+", ...)` (lookbehind sau `.`/`!`/`?`, khớp mọi khoảng trắng kể cả `\n` nên bao luôn case `.\n`), strip từng câu, rồi gộp theo nhóm `max_sentences_per_chunk` và join bằng `" "`.
- **`RecursiveChunker.chunk` / `_split`** — đệ quy: nếu `current_text` đã vừa `chunk_size` thì trả về nguyên văn; nếu hết separator thì cắt cứng theo `chunk_size`; ngược lại `split()` theo separator đầu tiên, gom các phần vào `buffer` cho tới khi vượt `chunk_size` thì flush, phần nào tự nó đã dài hơn `chunk_size` thì đệ quy tiếp với separator kế tiếp (`rest`).
- **`compute_similarity`** — cosine chuẩn: `dot(a, b) / (norm(a) * norm(b))`, trả `0.0` nếu một trong hai vector có norm bằng 0 (tránh chia 0).
- **`ChunkingStrategyComparator.compare`** — chạy `FixedSizeChunker`, `SentenceChunker`, `RecursiveChunker` trên cùng `text`, trả `dict` với 3 khóa `fixed_size` / `by_sentences` / `recursive`, mỗi khóa có `count`, `avg_length`, `chunks`.

## store.py

- **Schema bản ghi nội bộ** (`_make_record`): `{"id": doc.id, "content": doc.content, "metadata": {**doc.metadata, "doc_id": doc.metadata.get("doc_id", doc.id)}, "embedding": embedding_fn(doc.content)}`. `metadata["doc_id"]` luôn được đảm bảo tồn tại — nếu `ingest.py` đã gắn sẵn (theo doc gốc) thì giữ nguyên, nếu không thì mặc định bằng `doc.id` của chính bản ghi. Đây là khóa mà `delete_document` và `search_with_filter` dùng để lọc.
- **`__init__`** — thử `import chromadb` + `client.get_or_create_collection(...)`; nếu lỗi (chưa cài, hoặc môi trường không hỗ trợ) thì rơi về in-memory (`self._store: list[dict]`). Trong môi trường lab hiện tại `chromadb` **chưa được cài** nên toàn bộ test chạy qua nhánh in-memory.
- **`add_documents` / `search` / `get_collection_size` / `search_with_filter` / `delete_document`** — mỗi hàm có 2 nhánh: Chroma (dùng `collection.add/query/count/delete`) và in-memory (list `dict`, dot-product thủ công qua `_dot` từ `chunking.py`). Điểm số dùng **dot product** (không tự chuẩn hoá lại) — hợp lý vì `MockEmbedder`/`LocalEmbedder` đều trả vector đã chuẩn hoá đơn vị, nên dot product ≈ cosine similarity.
- **`search_with_filter`** — lọc `self._store` theo `metadata_filter` (khớp chính xác từng key) trước, rồi mới gọi `_search_records` trên tập đã lọc.

## agent.py

- **`KnowledgeBaseAgent.__init__`** — lưu `store`, `llm_fn`.
- **`answer`** — `store.search(question, top_k)` → build context đánh số `[1] ... [2] ...` từ `result["content"]` → prompt RAG chuẩn (context + câu hỏi) → gọi `llm_fn(prompt)`.

## Đã xác minh thủ công

```bash
pytest tests/ -v        # 42 passed
python3 ingest.py       # self-check front-matter parser OK
python3 main.py         # chạy hết pipeline ingest → search → agent.answer trên data/k3_university (mock embedder)
```

`main.py` từng lỗi `ModuleNotFoundError: No module named 'dotenv'` vì `.venv` thiếu `python-dotenv` dù có trong `requirements.txt`; đã chạy `uv pip install -r requirements.txt` để đồng bộ lại venv với lockfile của repo.

## Còn lại cho Giai đoạn 2 (nhóm — chưa làm ở đây)

- Thu thập 5–10 tài liệu thật vào `data/` (thay placeholder trong `data/k3_university/`), điền `sources.csv`.
- Viết 5 câu hỏi đánh giá (≥1 câu cần `metadata_filter={"audience": "student"}` theo `K3_VARIANT.md`).
- Thử chiến lược chunking riêng (khuyến khích 1 người theo heading/section) với `EMBEDDING_PROVIDER=local`, so sánh trong nhóm.
- Điền `report/REPORT_CANHAN.md` và `report/REPORT_NHOM.md`.
