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
        # Split on sentence boundaries preserving trailing punctuation
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk_text = " ".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
            if chunk_text:
                chunks.append(chunk_text)
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
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            # Fallback when no separators left: split by length
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if sep == "":
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        if sep in current_text:
            pieces = current_text.split(sep)
            final_chunks: list[str] = []
            good_splits: list[str] = []

            for piece in pieces:
                if len(piece) > self.chunk_size:
                    if good_splits:
                        final_chunks.append(sep.join(good_splits))
                        good_splits = []
                    sub_chunks = self._split(piece, next_separators)
                    final_chunks.extend(sub_chunks)
                else:
                    test_group = good_splits + [piece]
                    joined_test = sep.join(test_group)
                    if len(joined_test) <= self.chunk_size:
                        good_splits.append(piece)
                    else:
                        if good_splits:
                            final_chunks.append(sep.join(good_splits))
                        good_splits = [piece]

            if good_splits:
                final_chunks.append(sep.join(good_splits))

            return [c for c in final_chunks if c]
        else:
            return self._split(current_text, next_separators)


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(y * y for y in vec_b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed_chunks = FixedSizeChunker(chunk_size=chunk_size, overlap=50).chunk(text)
        sentence_chunks = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive_chunks = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def _stats(chunks: list[str]) -> dict:
            cnt = len(chunks)
            avg_l = sum(len(c) for c in chunks) / cnt if cnt > 0 else 0.0
            return {
                "count": cnt,
                "avg_length": avg_l,
                "chunks": chunks,
            }

        return {
            "fixed_size": _stats(fixed_chunks),
            "by_sentences": _stats(sentence_chunks),
            "recursive": _stats(recursive_chunks),
        }

class HeadingChunker:
    """
    Custom strategy: Split markdown text by headers (e.g., '# ', '## ').
    Useful for policy documents where each section represents a distinct topic.
    """
    def __init__(self, max_chunk_size: int = 1000) -> None:
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        
        # Regex to split by markdown headers
        # Use lookahead to keep the header in the chunk
        pieces = re.split(r'(?=\n#{1,6}\s+)', text)
        
        chunks = []
        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            # If a section is still too large, we could fallback to recursive chunker
            # For simplicity, we just keep it or split by size if absolutely necessary
            if len(piece) > self.max_chunk_size:
                fallback_chunks = RecursiveChunker(chunk_size=self.max_chunk_size).chunk(piece)
                chunks.extend(fallback_chunks)
            else:
                chunks.append(piece)
        return chunks


