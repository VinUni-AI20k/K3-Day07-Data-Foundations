"""
Demo script: HeadingChunker trên tài liệu quy định học vụ UEH.

Chạy:
    python scripts/demo_heading_chunker.py

Script này minh hoạ chiến lược chunking theo tiêu đề/mục (heading/section)
được yêu cầu trong K3_VARIANT.md (dòng 10), so sánh kết quả với các chiến
lược built-in (FixedSize, Sentence, Recursive).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest import parse_front_matter
from src.chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    HeadingChunker,
    RecursiveChunker,
)


def main() -> None:
    # --- Load a real UEH regulation document ---
    doc_path = Path(__file__).resolve().parent.parent / "data" / "ueh_university" / "ueh-academic-advising-regulation.md"
    raw_text = doc_path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(raw_text)

    print("=" * 70)
    print("DEMO: HeadingChunker — Chunking theo tiêu đề/mục")
    print(f"Tài liệu: {metadata.get('title', doc_path.name)}")
    print(f"Độ dài body: {len(body):,} ký tự")
    print("=" * 70)

    # --- 1. HeadingChunker ---
    heading_chunker = HeadingChunker(max_chunk_size=1500, include_parents=True)
    heading_chunks = heading_chunker.chunk(body)

    print(f"\n📑 HeadingChunker: {len(heading_chunks)} chunks")
    print("-" * 60)
    for i, chunk in enumerate(heading_chunks):
        # Find the "own" heading: the deepest heading marker in the chunk
        lines = chunk.split("\n")
        own_heading = lines[0]
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Check if this line is a heading
            if (stripped.startswith("#") or
                stripped.startswith("Chương ") or
                stripped.startswith("Điều ")):
                own_heading = stripped
        print(f"  [{i:2d}] ({len(chunk):4d} chars) {own_heading[:70]}")

    # --- 2. Baseline comparison ---
    print("\n" + "=" * 70)
    print("SO SÁNH VỚI CÁC CHIẾN LƯỢC BUILT-IN")
    print("=" * 70)

    comparator = ChunkingStrategyComparator()
    baseline = comparator.compare(body, chunk_size=500)

    heading_stats = {
        "count": len(heading_chunks),
        "avg_length": sum(len(c) for c in heading_chunks) / len(heading_chunks) if heading_chunks else 0,
    }

    print(f"\n{'Chiến lược':<20} {'Số chunk':>10} {'Avg length':>12}")
    print("-" * 45)
    for name, stats in baseline.items():
        print(f"  {name:<18} {stats['count']:>10} {stats['avg_length']:>12.0f}")
    print(f"  {'heading_section':<18} {heading_stats['count']:>10} {heading_stats['avg_length']:>12.0f}")

    # --- 3. Show a sample chunk in detail ---
    print("\n" + "=" * 70)
    print("MẪU CHUNK CHI TIẾT (chunk chứa 'Điều')")
    print("=" * 70)
    shown = 0
    for i, chunk in enumerate(heading_chunks):
        if "Điều" in chunk and shown < 2:
            print(f"\n--- Chunk [{i}] ({len(chunk)} chars) ---")
            print(chunk[:600])
            if len(chunk) > 600:
                print(f"... (còn {len(chunk) - 600} chars nữa)")
            shown += 1

    print("\n✅ Demo hoàn tất!")


if __name__ == "__main__":
    main()
