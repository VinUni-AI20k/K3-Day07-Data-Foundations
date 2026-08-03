from statistics import mean

from ingest import load_documents
from src.chunking import (
    ChunkingStrategyComparator,
    MarkdownHeadingRecursiveChunker,
    RecursiveChunker,
)

DATA_DIR = "data/k3_university"
TARGET_DOCS = {"thuvien", "dangkymonhoc", "totnghiep"}
CHUNK_SIZE = 700


def summarize(chunks: list[str]) -> tuple[int, float]:
    if not chunks:
        return 0, 0.0
    return len(chunks), mean(len(chunk) for chunk in chunks)


documents = load_documents(DATA_DIR)

for document in documents:
    if document.id not in TARGET_DOCS:
        continue

    print(f"\n=== {document.id} ===")

    baseline = ChunkingStrategyComparator().compare(
        document.content,
        chunk_size=CHUNK_SIZE,
    )

    for strategy_name, result in baseline.items():
        print(
            f"{strategy_name:20} "
            f"count={result['count']:3} "
            f"avg_length={result['avg_length']:.1f}"
        )

    recursive_chunks = RecursiveChunker(
        chunk_size=CHUNK_SIZE
    ).chunk(document.content)

    custom_chunks = MarkdownHeadingRecursiveChunker(
        chunk_size=CHUNK_SIZE
    ).chunk(document.content)

    recursive_count, recursive_avg = summarize(recursive_chunks)
    custom_count, custom_avg = summarize(custom_chunks)

    print(
        f"{'recursive_tuned':20} "
        f"count={recursive_count:3} "
        f"avg_length={recursive_avg:.1f}"
    )
    print(
        f"{'heading_recursive':20} "
        f"count={custom_count:3} "
        f"avg_length={custom_avg:.1f}"
    )

    print("\nVí dụ custom chunk đầu tiên:")
    print(custom_chunks[0][:500])