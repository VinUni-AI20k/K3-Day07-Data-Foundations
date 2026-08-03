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
            raise ValueError("chunk_size must be greater than zero")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be non-negative and smaller than chunk_size")
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
        """Split *text* at sentence boundaries and group consecutive sentences."""
        if not text or not text.strip():
            return []

        # Normalising whitespace gives stable output while the look-ahead keeps
        # terminal punctuation (including punctuation before closing quotes).
        normalized = " ".join(text.split())
        sentence_pattern = re.compile(
            r".+?(?:[.!?…]+['\"”’\)\]]*(?=\s|$)|$)",
            flags=re.DOTALL,
        )
        sentences = [match.group(0).strip() for match in sentence_pattern.finditer(normalized)]
        sentences = [sentence for sentence in sentences if sentence]

        return [
            " ".join(sentences[index : index + self.max_sentences_per_chunk])
            for index in range(0, len(sentences), self.max_sentences_per_chunk)
        ]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        """Recursively split *text*, preserving separator priority and content."""
        if not text or not text.strip():
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        """Split one oversized segment with progressively finer separators."""
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text] if current_text.strip() else []
        if not remaining_separators or remaining_separators[0] == "":
            return [
                current_text[index : index + self.chunk_size]
                for index in range(0, len(current_text), self.chunk_size)
                if current_text[index : index + self.chunk_size].strip()
            ]

        separator = remaining_separators[0]
        finer_separators = remaining_separators[1:]
        if separator not in current_text:
            return self._split(current_text, finer_separators)

        raw_parts = current_text.split(separator)
        pieces = [
            part + (separator if index < len(raw_parts) - 1 else "")
            for index, part in enumerate(raw_parts)
        ]

        chunks: list[str] = []
        buffer = ""
        for piece in pieces:
            if not piece:
                continue
            if len(piece) > self.chunk_size:
                if buffer.strip():
                    chunks.append(buffer)
                buffer = ""
                chunks.extend(self._split(piece, finer_separators))
            elif len(buffer) + len(piece) <= self.chunk_size:
                buffer += piece
            else:
                if buffer.strip():
                    chunks.append(buffer)
                buffer = piece

        if buffer.strip():
            chunks.append(buffer)
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
        raise ValueError("vectors must have the same dimensions")
    if not vec_a:
        raise ValueError("vectors must not be empty")

    norm_a = math.sqrt(math.fsum(value * value for value in vec_a))
    norm_b = math.sqrt(math.fsum(value * value for value in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(math.fsum(a * b for a, b in zip(vec_a, vec_b)) / (norm_a * norm_b))


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        """Return chunks and basic length statistics for all three strategies."""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        overlap = min(50, max(0, chunk_size // 10))
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=overlap),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }
        comparison: dict[str, dict] = {}
        for name, strategy in strategies.items():
            chunks = strategy.chunk(text)
            lengths = [len(chunk) for chunk in chunks]
            comparison[name] = {
                "count": len(chunks),
                "avg_length": (sum(lengths) / len(lengths)) if lengths else 0.0,
                "min_length": min(lengths, default=0),
                "max_length": max(lengths, default=0),
                "chunks": chunks,
            }
        return comparison
