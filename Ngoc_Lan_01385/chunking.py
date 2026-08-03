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

        normalized = text.replace(".\n", ". ").strip()
        sentences = re.split(r'(?<=[.!?])\s+', normalized)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk_sentences = sentences[i : i + self.max_sentences_per_chunk]
            chunks.append(" ".join(chunk_sentences).strip())

        return chunks

class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]

    When the input looks like Markdown, headings are preserved with the
    content that follows them so the resulting chunks remain meaningful.
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(
        self,
        separators: list[str] | None = None,
        chunk_size: int = 500,
        preserve_markdown_headings: bool = True,
    ) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size
        self.preserve_markdown_headings = preserve_markdown_headings

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        cleaned_text = text.strip()
        if not cleaned_text:
            return []
        if len(cleaned_text) <= self.chunk_size:
            return [cleaned_text]

        return self._split(cleaned_text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []

        if self.preserve_markdown_headings:
            markdown_sections = self._split_markdown_sections(current_text)
            if len(markdown_sections) > 1:
                return self._merge_sections(markdown_sections, remaining_separators)

        if not remaining_separators:
            return [current_text]

        separator = remaining_separators[0]
        parts = current_text.split(separator)

        chunks: list[str] = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if len(part) <= self.chunk_size:
                chunks.append(part)
            else:
                sub_chunks = self._split(part, remaining_separators[1:])
                chunks.extend(sub_chunks)

        return [chunk for chunk in chunks if chunk]

    def _split_markdown_sections(self, text: str) -> list[str]:
        lines = text.splitlines()
        sections: list[str] = []
        current_lines: list[str] = []

        for line in lines:
            heading_match = re.match(r"^(#{1,6})\s+.+$", line)
            if heading_match and current_lines:
                section = "\n".join(current_lines).strip()
                if section:
                    sections.append(section)
                current_lines = [line]
            else:
                if heading_match:
                    current_lines = [line]
                else:
                    current_lines.append(line)

        if current_lines:
            section = "\n".join(current_lines).strip()
            if section:
                sections.append(section)

        return [section for section in sections if section]

    def _merge_sections(self, sections: list[str], remaining_separators: list[str]) -> list[str]:
        chunks: list[str] = []
        pending: list[str] = []
        pending_length = 0

        for section in sections:
            section_length = len(section)
            if section_length > self.chunk_size:
                if pending:
                    chunks.append("\n\n".join(pending).strip())
                    pending = []
                    pending_length = 0
                chunks.extend(self._split(section, remaining_separators))
            elif pending_length + section_length <= self.chunk_size:
                pending.append(section)
                pending_length += section_length
            else:
                chunks.append("\n\n".join(pending).strip())
                pending = [section]
                pending_length = section_length

        if pending:
            chunks.append("\n\n".join(pending).strip())

        return [chunk for chunk in chunks if chunk]

def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)
    magnitude_a = math.sqrt(_dot(vec_a, vec_a))
    magnitude_b = math.sqrt(_dot(vec_b, vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        """
        Compare chunking strategies on the given text.

        Returns a dictionary with strategy names as keys and their chunked results as values.
        """
        fixed_chunker = FixedSizeChunker(chunk_size=chunk_size)
        sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)
        recursive_chunker = RecursiveChunker(chunk_size=chunk_size)

        strategies = {
            "fixed_size": fixed_chunker.chunk(text),
            "by_sentences": sentence_chunker.chunk(text),
            "recursive": recursive_chunker.chunk(text),
        }

        return {
            name: {
                "count": len(chunks),
                "avg_length": sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
                "chunks": chunks,
            }
            for name, chunks in strategies.items()
        }
