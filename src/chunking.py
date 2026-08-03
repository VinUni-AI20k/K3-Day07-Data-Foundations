from __future__ import annotations

import math
import re

# Mẫu cho cách xử lý text rỗng, text ngắn, overlap và list kết quả.
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

    _SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        limit = self.max_sentences_per_chunk
        sentences = [s.strip() for s in self._SENTENCE_BOUNDARY.split(text) if s.strip()]
        return [" ".join(sentences[index : index + limit]) for index in range(0, len(sentences), limit)]


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
        pieces = self._split(text, self.separators)
        return [piece.strip() for piece in pieces if piece.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators or remaining_separators[0] == "":
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        separator, rest = remaining_separators[0], remaining_separators[1:]
        parts = current_text.split(separator)
        if len(parts) == 1:
            return self._split(current_text, rest)

        chunks: list[str] = []
        buffer = ""
        for part in parts:
            candidate = f"{buffer}{separator}{part}" if buffer else part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.append(buffer)
                buffer = ""
            if len(part) <= self.chunk_size:
                buffer = part
            else:
                chunks.extend(self._split(part, rest))
        if buffer:
            chunks.append(buffer)
        return chunks


class HeadingChunker:
    """
    Split text into chunks aligned to Markdown heading boundaries.

    Each section (a heading line plus everything up to the next heading) is
    kept whole when it fits within chunk_size. A section too long to keep
    whole is recursively split, and its heading is re-attached to every
    resulting piece so pieces after the first don't lose their context.
    """

    HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.M)

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        chunks: list[str] = []
        for heading, body in self._split_sections(text):
            section = f"{heading}\n{body}".strip() if heading else body.strip()
            if not section:
                continue
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            for piece in RecursiveChunker(chunk_size=self.chunk_size).chunk(body):
                labeled = f"{heading}\n{piece}".strip() if heading else piece
                chunks.append(labeled)
        return chunks

    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        headings = list(self.HEADING_PATTERN.finditer(text))
        if not headings:
            return [("", text)]

        sections: list[tuple[str, str]] = []
        if headings[0].start() > 0:
            sections.append(("", text[: headings[0].start()]))

        for index, match in enumerate(headings):
            body_start = match.end()
            body_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            sections.append((match.group().strip(), text[body_start:body_end]))
        return sections


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=chunk_size // 10).chunk(text),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3).chunk(text),
            "recursive": RecursiveChunker(chunk_size=chunk_size).chunk(text),
        }

        result: dict = {}
        for name, chunks in strategies.items():
            lengths = [len(c) for c in chunks]
            avg_length = sum(lengths) / len(lengths) if lengths else 0.0
            result[name] = {"count": len(chunks), "avg_length": avg_length, "chunks": chunks}
        return result
