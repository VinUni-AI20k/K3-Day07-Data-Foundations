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
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

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
            current_chunk = text[start : start + self.chunk_size]
            chunks.append(current_chunk)

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
        if not text or not text.strip():
            return []

        # Split after sentence-ending punctuation when followed by whitespace.
        # The punctuation is retained in the sentence.
        sentences = re.split(r"(?<=[.!?])(?:[ \t]+|\n+)", text.strip())

        sentences = [
            re.sub(r"\s+", " ", sentence).strip()
            for sentence in sentences
            if sentence.strip()
        ]

        chunks: list[str] = []

        for start in range(0, len(sentences), self.max_sentences_per_chunk):
            sentence_group = sentences[
                start : start + self.max_sentences_per_chunk
            ]
            chunks.append(" ".join(sentence_group).strip())

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(
        self,
        separators: list[str] | None = None,
        chunk_size: int = 500,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        self.separators = (
            self.DEFAULT_SEPARATORS.copy()
            if separators is None
            else list(separators)
        )
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        return [
            chunk.strip()
            for chunk in self._split(text.strip(), self.separators)
            if chunk.strip()
        ]

    def _split(
        self,
        current_text: str,
        remaining_separators: list[str],
    ) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Empty separator is the final fallback: split by characters.
        if separator == "":
            return [
                current_text[start : start + self.chunk_size]
                for start in range(0, len(current_text), self.chunk_size)
            ]

        # If the separator does not occur, try the next separator.
        if separator not in current_text:
            return self._split(current_text, next_separators)

        raw_parts = current_text.split(separator)

        # Restore separators so punctuation and paragraph boundaries are not lost.
        parts: list[str] = []
        for index, part in enumerate(raw_parts):
            if not part:
                continue

            if index < len(raw_parts) - 1:
                part += separator

            parts.append(part)

        chunks: list[str] = []
        buffer = ""

        for part in parts:
            if len(part) > self.chunk_size:
                if buffer.strip():
                    chunks.append(buffer.strip())
                    buffer = ""

                chunks.extend(self._split(part.strip(), next_separators))
                continue

            candidate = buffer + part

            if len(candidate) <= self.chunk_size:
                buffer = candidate
            else:
                if buffer.strip():
                    chunks.append(buffer.strip())
                buffer = part

        if buffer.strip():
            chunks.append(buffer.strip())

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must have the same number of dimensions")

    magnitude_a = math.sqrt(sum(value**2 for value in vec_a))
    magnitude_b = math.sqrt(sum(value**2 for value in vec_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        overlap = min(50, chunk_size - 1)

        strategies = {
            "fixed_size": FixedSizeChunker(
                chunk_size=chunk_size,
                overlap=overlap,
            ),
            "by_sentences": SentenceChunker(
                max_sentences_per_chunk=3,
            ),
            "recursive": RecursiveChunker(
                chunk_size=chunk_size,
            ),
        }

        result: dict[str, dict] = {}

        for strategy_name, chunker in strategies.items():
            chunks = chunker.chunk(text)

            result[strategy_name] = {
                "count": len(chunks),
                "avg_length": (
                    sum(len(chunk) for chunk in chunks) / len(chunks)
                    if chunks
                    else 0.0
                ),
                "chunks": chunks,
            }

        return result