"""Benchmark chung để so sánh các chiến lược chunking của nhóm C11.

Ví dụ chạy chiến lược Heading Chunking của Lê Trung Hiếu:

    python benchmark.py `
        --package src.LeTrungHieu_2A202601917 `
        --chunker HeadingChunker `
        --chunk-size 500 `
        --provider openai `
        --embedding-model text-embedding-3-small `
        --output report/benchmark_2A202601917.json

Mỗi thành viên chỉ thay ``--package``, ``--chunker`` và tham số chunker. Corpus,
embedding, top-k, câu hỏi và cách đánh giá phải giữ giống nhau để so sánh công bằng.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import os
import re
import sys
import unicodedata
import uuid
from pathlib import Path
from typing import Any, Callable

DEFAULT_DATA_DIR = "data/k3_university"
GROUP_EMBEDDING_MODEL = "text-embedding-3-small"
TEXT_EXTENSIONS = {".md", ".txt"}

# Một chunk chỉ được tính là liên quan khi vừa thuộc đúng tài liệu, vừa tự nó
# chứa đủ các mốc cần thiết để trả lời. Không ghép từ khóa từ nhiều chunk.
BENCHMARK_QUERIES: list[dict[str, Any]] = [
    {
        "id": 1,
        "query": (
            "Mỗi học kỳ, sinh viên được đăng ký tối thiểu và tối đa "
            "bao nhiêu tín chỉ?"
        ),
        "gold_answer": "Tối thiểu 08 tín chỉ và tối đa 16 tín chỉ mỗi học kỳ.",
        "gold_doc": "k3-course-registration",
        "markers": [["08 tín chỉ", "8 tín chỉ"], ["16 tín chỉ"]],
    },
    {
        "id": 2,
        "query": (
            "Nếu sinh viên còn nợ học phí của học kỳ trước thì điều gì xảy ra "
            "khi đăng ký học kỳ tiếp theo?"
        ),
        "gold_answer": (
            "Sinh viên còn nợ học phí sẽ không được đăng ký học phần của "
            "học kỳ tiếp theo."
        ),
        "gold_doc": "k3-tuition-payment",
        "markers": [["không được đăng ký học phần"]],
    },
    {
        "id": 3,
        "query": (
            "Sinh viên đạt học bổng khuyến khích học tập Loại A được nhận "
            "mức học bổng bằng bao nhiêu phần trăm số học phí đã nộp?"
        ),
        "gold_answer": "Loại A bằng 50% số học phí sinh viên đã nộp.",
        "gold_doc": "k3-scholarship-policy",
        "markers": [["50%", "50 %"]],
        "filter": {"audience": "student"},
    },
    {
        "id": 4,
        "query": "Chi phí ở ký túc xá phòng 8 sinh viên là bao nhiêu mỗi tháng?",
        "gold_answer": "350.000 VNĐ mỗi sinh viên mỗi tháng.",
        "gold_doc": "k3-dormitory-policy",
        "markers": [["350.000", "350,000"], ["tháng"]],
    },
    {
        "id": 5,
        "query": (
            "Khu tự học ở tầng 6 của thư viện mở cửa vào những khung giờ nào?"
        ),
        "gold_answer": "Thứ 2 đến Chủ nhật, từ 6h30 đến 22h.",
        "gold_doc": "k3-library-services",
        "markers": [["6h30", "6:30"], ["22h", "22:00"]],
    },
]


class CachedEmbedder:
    """Cache embedding trong một lần benchmark để tránh gọi lại cùng văn bản."""

    def __init__(self, embedder: Callable[[str], list[float]]) -> None:
        self.embedder = embedder
        self.cache: dict[str, list[float]] = {}
        self._backend_name = getattr(
            embedder, "_backend_name", embedder.__class__.__name__
        )

    def __call__(self, text: str) -> list[float]:
        if text not in self.cache:
            self.cache[text] = [float(value) for value in self.embedder(text)]
        return self.cache[text]


class SharedLocalEmbedder:
    """Local multilingual embedder không phụ thuộc pandas/datasets.

    ``SentenceTransformer`` của một số môi trường Windows import thêm
    ``datasets`` và ``pandas`` ngay lúc khởi động. Benchmark chỉ cần inference,
    nên dùng trực tiếp AutoModel và mean pooling của đúng checkpoint MiniLM.
    Tất cả thành viên vì vậy vẫn dùng cùng model và cùng cách tạo vector.
    """

    def __init__(self, model_name: str) -> None:
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.model_name = model_name
        self._backend_name = f"{model_name} (transformers mean pooling)"
        self._torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def __call__(self, text: str) -> list[float]:
        encoded = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt",
        )
        with self._torch.no_grad():
            token_embeddings = self.model(**encoded).last_hidden_state

        attention_mask = encoded["attention_mask"].unsqueeze(-1)
        attention_mask = attention_mask.expand(token_embeddings.size()).float()
        summed = (token_embeddings * attention_mask).sum(dim=1)
        counts = attention_mask.sum(dim=1).clamp(min=1e-9)
        embedding = summed / counts
        embedding = self._torch.nn.functional.normalize(embedding, p=2, dim=1)
        return [float(value) for value in embedding[0].tolist()]


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFC", str(text)).casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def _load_valid_env(path: Path) -> None:
    """Nạp các dòng KEY=VALUE hợp lệ và bỏ qua tiêu đề sai cú pháp trong .env."""
    if not path.is_file():
        return

    pattern = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(raw_line)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _contains_markers(text: str, marker_groups: list[list[str]]) -> bool:
    """Mỗi nhóm cần khớp ít nhất một cách viết thay thế."""
    normalized_text = _normalize(text)
    return all(
        any(_normalize(marker) in normalized_text for marker in alternatives)
        for alternatives in marker_groups
    )


def _parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    closing = next(
        (index for index in range(1, len(lines)) if lines[index].strip() == "---"),
        None,
    )
    if closing is None:
        return {}, text

    block = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1 :]).lstrip("\n")

    try:
        import yaml

        loaded = yaml.safe_load(block) or {}
        if isinstance(loaded, dict):
            return {str(key): value for key, value in loaded.items()}, body
    except Exception:
        pass

    metadata: dict[str, Any] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.split(" #", 1)[0].strip().strip('"').strip("'")
        metadata[key.strip()] = value
    return metadata, body


def _load_package(package_name: str) -> dict[str, Any]:
    try:
        package = importlib.import_module(package_name)
        chunking_module = importlib.import_module(f"{package_name}.chunking")
        store_module = importlib.import_module(f"{package_name}.store")
        embeddings_module = importlib.import_module(f"{package_name}.embeddings")
        models_module = importlib.import_module(f"{package_name}.models")
    except ImportError as exc:
        raise RuntimeError(
            f"Không import được package '{package_name}': {exc}"
        ) from exc

    return {
        "package": package,
        "chunking": chunking_module,
        "store_class": getattr(store_module, "EmbeddingStore"),
        "document_class": getattr(models_module, "Document"),
        "embeddings": embeddings_module,
    }


def _make_embedder(
    embeddings_module: Any,
    provider: str,
    model_name: str | None,
) -> CachedEmbedder:
    if provider == "local":
        default_model = getattr(embeddings_module, "LOCAL_EMBEDDING_MODEL")
        selected_model = model_name or default_model
        try:
            return CachedEmbedder(SharedLocalEmbedder(selected_model))
        except Exception as exc:
            raise RuntimeError(
                "Không khởi tạo được local embedder bằng transformers. "
                "Hãy kiểm tra kết nối tải model và các gói transformers/torch."
            ) from exc
    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("Thiếu OPENAI_API_KEY cho provider=openai.")
        embedder_class = getattr(embeddings_module, "OpenAIEmbedder")
        default_model = GROUP_EMBEDDING_MODEL
    else:
        raise RuntimeError(
            "Benchmark chính thức chỉ dùng provider 'local' hoặc 'openai', không dùng mock."
        )

    selected_model = model_name or default_model
    return CachedEmbedder(embedder_class(model_name=selected_model))


def _parse_chunker_args(raw_values: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for raw in raw_values:
        if "=" not in raw:
            raise ValueError(
                f"Tham số chunker không hợp lệ '{raw}'; dùng dạng key=value."
            )
        key, value = raw.split("=", 1)
        key = key.strip()
        try:
            parsed[key] = json.loads(value)
        except json.JSONDecodeError:
            parsed[key] = value
    return parsed


def _make_chunker(
    chunking_module: Any,
    class_name: str,
    args: argparse.Namespace,
    embedder: CachedEmbedder,
) -> tuple[Any, dict[str, Any]]:
    try:
        chunker_class = getattr(chunking_module, class_name)
    except AttributeError as exc:
        available = sorted(
            name
            for name, value in vars(chunking_module).items()
            if inspect.isclass(value) and hasattr(value, "chunk")
        )
        raise RuntimeError(
            f"Không có chunker '{class_name}'. Các lớp tìm thấy: {available}"
        ) from exc

    signature = inspect.signature(chunker_class)
    kwargs = _parse_chunker_args(args.chunker_arg)
    common_values = {
        "chunk_size": args.chunk_size,
        "overlap": args.overlap,
        "max_sentences_per_chunk": args.max_sentences,
        "embedding_fn": embedder,
        "embedder": embedder,
    }
    for name, value in common_values.items():
        if name in signature.parameters and name not in kwargs:
            kwargs[name] = value

    try:
        return chunker_class(**kwargs), kwargs
    except TypeError as exc:
        raise RuntimeError(
            f"Không tạo được {class_name}{kwargs}: {exc}. "
            "Thêm tham số riêng bằng --chunker-arg key=value."
        ) from exc


def _build_store(
    data_dir: Path,
    document_class: type,
    store_class: type,
    chunker: Any,
    embedder: CachedEmbedder,
    collection_name: str,
) -> tuple[Any, list[dict[str, Any]]]:
    if not data_dir.is_dir():
        raise RuntimeError(f"Không tìm thấy thư mục dữ liệu: {data_dir}")

    chunk_documents: list[Any] = []
    document_stats: list[dict[str, Any]] = []

    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        metadata, body = _parse_front_matter(path.read_text(encoding="utf-8"))
        doc_id = str(metadata.get("doc_id") or path.stem)
        metadata.setdefault("doc_id", doc_id)
        metadata.setdefault("source", str(path))
        pieces = [piece for piece in chunker.chunk(body) if piece and piece.strip()]

        document_stats.append(
            {
                "doc_id": doc_id,
                "characters": len(body),
                "chunks": len(pieces),
            }
        )

        for index, piece in enumerate(pieces):
            chunk_metadata = dict(metadata)
            chunk_metadata["doc_id"] = doc_id
            chunk_metadata["chunk_index"] = index
            chunk_documents.append(
                document_class(
                    id=f"{doc_id}::chunk_{index}",
                    content=piece.strip(),
                    metadata=chunk_metadata,
                )
            )

    if not chunk_documents:
        raise RuntimeError(f"Không tạo được chunk nào từ {data_dir}.")

    store = store_class(collection_name=collection_name, embedding_fn=embedder)
    store.add_documents(chunk_documents)
    return store, document_stats


def _relevant_rank(
    results: list[dict[str, Any]],
    gold_doc: str,
    markers: list[list[str]],
) -> int | None:
    for rank, result in enumerate(results, start=1):
        metadata = result.get("metadata") or {}
        if (
            metadata.get("doc_id") == gold_doc
            and _contains_markers(result.get("content", ""), markers)
        ):
            return rank
    return None


def _make_openai_llm(model_name: str | None) -> Callable[[str], str] | None:
    if not model_name:
        return None
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Thiếu OPENAI_API_KEY để chạy Agent với OpenAI.")

    from openai import OpenAI

    client = OpenAI()

    def call_llm(prompt: str) -> str:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return (response.choices[0].message.content or "").strip()

    return call_llm


def _answer_from_results(
    question: str,
    results: list[dict[str, Any]],
    llm_fn: Callable[[str], str],
) -> str:
    contexts: list[str] = []
    for rank, result in enumerate(results, start=1):
        metadata = result.get("metadata") or {}
        source = metadata.get("source_url") or metadata.get("doc_id") or "unknown"
        contexts.append(f"[Nguồn {rank}: {source}]\n{result.get('content', '')}")

    context_text = "\n\n".join(contexts)
    prompt = (
        "Bạn là trợ lý hỏi đáp về quy định đại học. Chỉ trả lời bằng thông tin "
        "trong ngữ cảnh. Nếu thiếu dữ liệu, hãy nói không đủ thông tin. Trả lời "
        "ngắn gọn bằng tiếng Việt và không suy đoán.\n\n"
        f"NGỮ CẢNH:\n{context_text}\n\n"
        f"CÂU HỎI:\n{question}\n\nTRẢ LỜI:"
    )
    return llm_fn(prompt)


def _serializable_result(result: dict[str, Any], relevant: bool) -> dict[str, Any]:
    return {
        "id": result.get("id"),
        "score": float(result.get("score", 0.0)),
        "doc_id": (result.get("metadata") or {}).get("doc_id"),
        "chunk_index": (result.get("metadata") or {}).get("chunk_index"),
        "content": result.get("content", ""),
        "relevant_answer_chunk": relevant,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark công bằng các chiến lược chunking của nhóm C11."
    )
    parser.add_argument(
        "--package",
        required=True,
        help="Package cá nhân, ví dụ src.LeTrungHieu_2A202601917",
    )
    parser.add_argument(
        "--chunker",
        required=True,
        help="Tên lớp chunker, ví dụ HeadingChunker hoặc FixedSizeChunker",
    )
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--provider", choices=["local", "openai"], default="openai")
    parser.add_argument("--embedding-model", default=None)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    parser.add_argument("--max-sentences", type=int, default=3)
    parser.add_argument(
        "--chunker-arg",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Tham số riêng; có thể lặp lại, ví dụ --chunker-arg threshold=0.75",
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--llm-model",
        default=None,
        help="Model OpenAI dùng cho Agent; bỏ trống để chỉ đánh giá retrieval.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Đường dẫn JSON để gửi kết quả cho nhóm.",
    )
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    _load_valid_env(Path(__file__).with_name(".env"))
    args = _build_parser().parse_args()
    if args.top_k < 1:
        raise RuntimeError("--top-k phải lớn hơn 0.")

    modules = _load_package(args.package)
    embedder = _make_embedder(
        modules["embeddings"], args.provider, args.embedding_model
    )
    chunker, chunker_kwargs = _make_chunker(
        modules["chunking"], args.chunker, args, embedder
    )

    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "-", f"{args.chunker}-{uuid.uuid4().hex[:8]}")
    store, document_stats = _build_store(
        Path(args.data_dir),
        modules["document_class"],
        modules["store_class"],
        chunker,
        embedder,
        collection_name=f"bench-{safe_name}"[:63],
    )
    llm_fn = _make_openai_llm(args.llm_model)

    embedding_dimension = len(embedder("kiểm tra số chiều embedding"))
    chunk_count = store.get_collection_size()
    print("=" * 80)
    print(f"Package: {args.package}")
    print(f"Chunker: {args.chunker} {chunker_kwargs}")
    print(f"Embedding: {embedder._backend_name} ({embedding_dimension} chiều)")
    print(f"Data: {args.data_dir}")
    print(f"Collection size: {chunk_count} chunks")
    print("Chunk count/document: " + ", ".join(
        f"{item['doc_id']}={item['chunks']}" for item in document_stats
    ))

    query_outputs: list[dict[str, Any]] = []
    hits = 0
    top1_hits = 0
    reciprocal_rank_sum = 0.0
    official_total = 0

    for item in BENCHMARK_QUERIES:
        unfiltered_results = store.search(item["query"], top_k=args.top_k)
        metadata_filter = item.get("filter")
        if metadata_filter:
            results = store.search_with_filter(
                item["query"],
                top_k=args.top_k,
                metadata_filter=metadata_filter,
            )
        else:
            results = unfiltered_results

        rank = _relevant_rank(results, item["gold_doc"], item["markers"])
        unfiltered_rank = _relevant_rank(
            unfiltered_results, item["gold_doc"], item["markers"]
        )
        hit = rank is not None
        hits += int(hit)
        top1_hits += int(rank == 1)
        reciprocal_rank_sum += 1.0 / rank if rank else 0.0

        answer = None
        answer_correct = None
        official_score = None
        if llm_fn is not None:
            answer = _answer_from_results(item["query"], results, llm_fn)
            answer_correct = _contains_markers(answer, item["markers"])
            if rank is None:
                official_score = 0
            elif rank == 1 and answer_correct:
                official_score = 2
            else:
                official_score = 1
            official_total += official_score

        print("\n" + "=" * 80)
        print(f"Q{item['id']}: {item['query']}")
        print(f"Gold: {item['gold_answer']}")
        print(f"Relevant answer chunk rank: {rank if rank else 'NOT IN TOP-K'}")
        if metadata_filter:
            print(
                f"Metadata A/B: unfiltered rank={unfiltered_rank or 'MISS'}, "
                f"filtered {metadata_filter} rank={rank or 'MISS'}"
            )
        if answer is not None:
            print(f"Agent: {answer}")
            print(
                f"Auto-check answer: {answer_correct}; score={official_score}/2 "
                "(cần kiểm tra thủ công trước khi ghi báo cáo)"
            )

        serialized_results: list[dict[str, Any]] = []
        for result_rank, result in enumerate(results, start=1):
            relevant = (
                (result.get("metadata") or {}).get("doc_id") == item["gold_doc"]
                and _contains_markers(result.get("content", ""), item["markers"])
            )
            marker = "<-- RELEVANT" if relevant else ""
            metadata = result.get("metadata") or {}
            print(
                f"{result_rank}. score={float(result.get('score', 0.0)):.4f}, "
                f"doc={metadata.get('doc_id')}, chunk={metadata.get('chunk_index')} "
                f"{marker}"
            )
            print("   " + result.get("content", "")[:220].replace("\n", " "))
            serialized_results.append(_serializable_result(result, relevant))

        query_outputs.append(
            {
                "id": item["id"],
                "query": item["query"],
                "gold_answer": item["gold_answer"],
                "metadata_filter": metadata_filter,
                "unfiltered_relevant_rank": unfiltered_rank,
                "relevant_rank": rank,
                "hit_at_k": hit,
                "reciprocal_rank": 1.0 / rank if rank else 0.0,
                "agent_answer": answer,
                "answer_auto_check": answer_correct,
                "official_score": official_score,
                "results": serialized_results,
            }
        )

    query_count = len(BENCHMARK_QUERIES)
    summary = {
        "hit_at_k": hits / query_count,
        "hits": hits,
        "top1_accuracy": top1_hits / query_count,
        "top1_hits": top1_hits,
        "mrr": reciprocal_rank_sum / query_count,
        "official_total": official_total if llm_fn is not None else None,
    }

    print("\n" + "=" * 80)
    print(f"RETRIEVAL: Hit@{args.top_k}={hits}/{query_count} ({summary['hit_at_k']:.2%})")
    print(f"TOP-1: {top1_hits}/{query_count} ({summary['top1_accuracy']:.2%})")
    print(f"MRR: {summary['mrr']:.4f}")
    if llm_fn is None:
        print("OFFICIAL /10: chưa tính (thêm --llm-model và kiểm tra câu trả lời Agent).")
    else:
        print(f"OFFICIAL AUTO-CHECK: {official_total}/10 (cần duyệt thủ công).")

    output = {
        "config": {
            "package": args.package,
            "chunker": args.chunker,
            "chunker_kwargs": {
                key: getattr(value, "_backend_name", str(value))
                if callable(value)
                else value
                for key, value in chunker_kwargs.items()
            },
            "provider": args.provider,
            "embedding_backend": embedder._backend_name,
            "embedding_dimension": embedding_dimension,
            "data_dir": args.data_dir,
            "top_k": args.top_k,
            "llm_model": args.llm_model,
        },
        "collection_size": chunk_count,
        "documents": document_stats,
        "queries": query_outputs,
        "summary": summary,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Đã lưu JSON: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
