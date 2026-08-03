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
        if not text or not text.strip():
            return []

        # Keep the sentence-ending punctuation in the resulting chunks.  The
        # whitespace look-behind avoids losing punctuation while handling
        # spaces and newlines between sentences.
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
            if sentence.strip()
        ]

        return [
            " ".join(sentences[index : index + self.max_sentences_per_chunk]).strip()
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
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        return self._split(text, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        text = current_text.strip()
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        # If no useful separator remains, split at the hard size boundary.
        if not remaining_separators:
            return [
                text[start : start + self.chunk_size].strip()
                for start in range(0, len(text), self.chunk_size)
                if text[start : start + self.chunk_size].strip()
            ]

        separator = remaining_separators[0]
        if separator == "":
            return [
                text[start : start + self.chunk_size].strip()
                for start in range(0, len(text), self.chunk_size)
                if text[start : start + self.chunk_size].strip()
            ]

        pieces = text.split(separator)
        if len(pieces) == 1:
            return self._split(text, remaining_separators[1:])

        chunks: list[str] = []
        pending = ""
        lower_priority = remaining_separators[1:]

        for raw_piece in pieces:
            piece = raw_piece.strip()
            if not piece:
                continue

            candidate = piece if not pending else f"{pending}{separator}{piece}"
            if len(candidate) <= self.chunk_size:
                pending = candidate
                continue

            if pending:
                chunks.append(pending.strip())
                pending = ""

            if len(piece) <= self.chunk_size:
                pending = piece
            else:
                chunks.extend(self._split(piece, lower_priority))

        if pending:
            chunks.append(pending.strip())

        return [chunk for chunk in chunks if chunk]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    magnitude_a = math.sqrt(sum(value * value for value in vec_a))
    magnitude_b = math.sqrt(sum(value * value for value in vec_b))
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (magnitude_a * magnitude_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison: dict = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            comparison[name] = {
                "count": len(chunks),
                "avg_length": (
                    sum(len(chunk) for chunk in chunks) / len(chunks)
                    if chunks
                    else 0.0
                ),
                "chunks": chunks,
            }
        return comparison
