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
        try:
            import re

            if not text or not text.strip():
                return []

            sentences = re.split(r'(?<=[.!?])\s+|\.\n', text.strip())
            sentences = [s.strip() for s in sentences if s.strip()]

            chunks = []

            for i in range(0, len(sentences), self.max_sentences_per_chunk):
                chunk = " ".join(
                    sentences[i : i + self.max_sentences_per_chunk]
                ).strip()
                if chunk:
                    chunks.append(chunk)

            return chunks

        except:
            raise NotImplementedError("Implement SentenceChunker.chunk")


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
        try:
            if not text:
                return []

            return self._split(text, self.separators)

        except Exception:
            raise NotImplementedError("Implement RecursiveChunker.chunk")

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        try:
            if len(current_text) <= self.chunk_size:
                return [current_text.strip()] if current_text.strip() else []

            if not remaining_separators:
                return [
                    current_text[i : i + self.chunk_size]
                    for i in range(0, len(current_text), self.chunk_size)
                ]

            separator = remaining_separators[0]

            if separator == "":
                return [
                    current_text[i : i + self.chunk_size]
                    for i in range(0, len(current_text), self.chunk_size)
                ]

            pieces = current_text.split(separator)

            chunks = []
            buffer = ""

            for piece in pieces:
                candidate = piece if not buffer else buffer + separator + piece

                if len(candidate) <= self.chunk_size:
                    buffer = candidate
                else:
                    if buffer:
                        chunks.extend(
                            self._split(buffer, remaining_separators[1:])
                        )
                    buffer = piece

            if buffer:
                chunks.extend(
                    self._split(buffer, remaining_separators[1:])
                )

            return chunks

        except Exception:
            raise NotImplementedError("Implement RecursiveChunker._split")


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    try:
        import math

        dot = _dot(vec_a, vec_b)

        norm_a = math.sqrt(sum(x * x for x in vec_a))
        norm_b = math.sqrt(sum(x * x for x in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    except Exception:
        raise NotImplementedError("Implement compute_similarity")


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        try:
            strategies = {
                "fixed_size": FixedSizeChunker(chunk_size=chunk_size),
                "by_sentences": SentenceChunker(),
                "recursive": RecursiveChunker(chunk_size=chunk_size),
            }

            results = {}

            for name, strategy in strategies.items():
                chunks = strategy.chunk(text)

                results[name] = {
                    "chunks": chunks,
                    "count": len(chunks),
                    "avg_length": (
                        sum(len(c) for c in chunks) / len(chunks)
                        if chunks
                        else 0
                    ),
                    "max_chunk_size": (
                        max((len(c) for c in chunks), default=0)
                    ),
                    "min_chunk_size": (
                        min((len(c) for c in chunks), default=0)
                    ),
                }

            return results

        except Exception:
            raise NotImplementedError("Implement ChunkingStrategyComparator.compare")
