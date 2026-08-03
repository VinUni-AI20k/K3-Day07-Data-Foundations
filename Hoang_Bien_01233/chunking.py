from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        raw_sentences = re.split(r'(?<=[.!?])\s+|\.\n', text)
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk_sentences = sentences[i : i + self.max_sentences_per_chunk]
            chunks.append(" ".join(chunk_sentences))
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []

        chunk_size = max(1, self.chunk_size)
        if len(current_text) <= chunk_size:
            return [current_text]

        separator = ""
        next_separators: list[str] = []
        for index, candidate in enumerate(remaining_separators):
            if candidate == "" or candidate in current_text:
                separator = candidate
                next_separators = remaining_separators[index + 1 :]
                break

        if not separator:
            return [
                current_text[start : start + chunk_size]
                for start in range(0, len(current_text), chunk_size)
            ]

        raw_parts = current_text.split(separator)
        parts = [
            part + separator if index < len(raw_parts) - 1 else part
            for index, part in enumerate(raw_parts)
            if part or index < len(raw_parts) - 1
        ]

        chunks: list[str] = []
        pending: list[str] = []
        pending_length = 0

        for part in parts:
            part_length = len(part)
            if part_length > chunk_size:
                if pending:
                    chunks.append("".join(pending))
                    pending = []
                    pending_length = 0
                chunks.extend(self._split(part, next_separators))
            elif pending_length + part_length <= chunk_size:
                pending.append(part)
                pending_length += part_length
            else:
                chunks.append("".join(pending))
                pending = [part]
                pending_length = part_length

        if pending:
            chunks.append("".join(pending))
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size).chunk(text)
        sentence = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)
        
        return {
            "fixed_size": {
                "count": len(fixed),
                "avg_length": sum(len(c) for c in fixed) / len(fixed) if fixed else 0,
                "chunks": fixed
            },
            "by_sentences": {
                "count": len(sentence),
                "avg_length": sum(len(c) for c in sentence) / len(sentence) if sentence else 0,
                "chunks": sentence
            },
            "recursive": {
                "count": len(recursive),
                "avg_length": sum(len(c) for c in recursive) / len(recursive) if recursive else 0,
                "chunks": recursive
            }
        }

class MarkdownHeadingRecursiveChunker:
    """
    Chia tài liệu theo Markdown heading trước.
    Nếu một section quá dài, tiếp tục chia bằng RecursiveChunker.
    Heading được lặp lại trong từng chunk con để giữ ngữ cảnh.
    """

    HEADING_PATTERN = re.compile(r"(?m)^#{1,6}\s+.+$")

    def __init__(self, chunk_size: int = 700) -> None:
        self.chunk_size = max(100, chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        matches = list(self.HEADING_PATTERN.finditer(text))

        # Tài liệu không có heading: dùng recursive thông thường.
        if not matches:
            return RecursiveChunker(
                separators=["\n\n", "\n", ". ", " ", ""],
                chunk_size=self.chunk_size,
            ).chunk(text.strip())

        chunks: list[str] = []

        # Giữ phần nội dung đứng trước heading đầu tiên nếu có.
        preamble = text[: matches[0].start()].strip()
        if preamble:
            chunks.extend(
                RecursiveChunker(
                    chunk_size=self.chunk_size
                ).chunk(preamble)
            )

        for index, match in enumerate(matches):
            section_end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )

            heading = match.group(0).strip()
            body = text[match.end() : section_end].strip()

            if not body:
                chunks.append(heading)
                continue

            # Trừ chỗ dành cho heading được gắn vào từng chunk.
            body_chunk_size = max(
                100,
                self.chunk_size - len(heading) - 2,
            )

            body_chunks = RecursiveChunker(
                separators=["\n\n", "\n", ". ", " ", ""],
                chunk_size=body_chunk_size,
            ).chunk(body)

            for body_chunk in body_chunks:
                body_chunk = body_chunk.strip()
                if body_chunk:
                    chunks.append(f"{heading}\n\n{body_chunk}")

        return chunks