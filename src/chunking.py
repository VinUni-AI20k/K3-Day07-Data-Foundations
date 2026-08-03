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
        # Split on sentence-ending punctuation followed by whitespace or newline
        sentences = re.split(r'(?<=[.!?])(?:\s|\n)+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunks.append(" ".join(group))
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
        results = self._split(text, self.separators)
        return [c for c in results if c.strip()]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base case: text fits within chunk_size
        if len(current_text) <= self.chunk_size:
            return [current_text]

        # No separators left — return as-is (can't split further)
        if not remaining_separators:
            return [current_text]

        separator = remaining_separators[0]

        # Empty string separator: split character by character into chunk_size pieces
        if separator == "":
            chunks: list[str] = []
            for i in range(0, len(current_text), self.chunk_size):
                chunks.append(current_text[i : i + self.chunk_size])
            return chunks

        parts = current_text.split(separator)

        # If the separator didn't split anything, try the next separator
        if len(parts) == 1:
            return self._split(current_text, remaining_separators[1:])

        # --- Merge up: gom các mảnh nhỏ liền kề lại với nhau ---
        merged: list[str] = []
        current_chunk = ""
        for part in parts:
            if not part:
                continue
            # If adding this part (with separator) would exceed chunk_size, flush
            candidate = (current_chunk + separator + part) if current_chunk else part
            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
            else:
                # Flush the accumulated chunk
                if current_chunk:
                    merged.append(current_chunk)
                current_chunk = part
        if current_chunk:
            merged.append(current_chunk)

        # --- Recurse down: split oversized merged chunks with next separators ---
        result: list[str] = []
        for chunk in merged:
            if len(chunk) <= self.chunk_size:
                result.append(chunk)
            else:
                result.extend(self._split(chunk, remaining_separators[1:]))
        return result


class HeadingChunker:
    """
    Split text into chunks based on headings/sections.

    Designed for Vietnamese university regulations and handbooks that use
    markdown headings (# / ## / ###) and Vietnamese legal structure markers
    (Chương, Điều, MỤC, PHẦN).

    Rules:
        - Each chunk corresponds to one section identified by a heading.
        - If a section is longer than max_chunk_size, it is further split
          at sub-heading boundaries or, as a fallback, by paragraphs.
        - Each chunk is prefixed with its parent heading(s) for context,
          so retrieval results are self-contained.
        - Text before the first heading becomes a "preamble" chunk.

    Design rationale:
        Vietnamese academic regulations (quy định học vụ, sổ tay sinh viên)
        are organized by Chương (Chapter) → Điều (Article) → numbered clauses.
        Splitting at these natural boundaries keeps each chunk semantically
        coherent and avoids cutting mid-regulation, which improves retrieval
        quality for student queries like "Điều kiện xét học bổng là gì?".
    """

    # Regex patterns for heading detection, ordered by priority (highest first).
    # Group 1 captures the full heading line text.
    HEADING_PATTERNS = [
        # Markdown headings: # Title, ## Subtitle, ### Sub-subtitle
        re.compile(r'^(#{1,4})\s+(.+)$', re.MULTILINE),
        # Vietnamese legal chapters: "Chương I", "Chương II", "CHƯƠNG 1"
        re.compile(r'^(Chương\s+[IVXLCDM\d]+.*)$', re.MULTILINE | re.IGNORECASE),
        # Vietnamese legal articles: "Điều 1.", "Điều 12."
        re.compile(r'^(Điều\s+\d+\..*)$', re.MULTILINE),
    ]

    # Combined pattern that matches any heading line
    _SPLIT_PATTERN = re.compile(
        r'^(?=#{1,4}\s|Chương\s+[IVXLCDM\d]|Điều\s+\d+\.)',
        re.MULTILINE | re.IGNORECASE,
    )

    def __init__(self, max_chunk_size: int = 1500, include_parents: bool = True) -> None:
        """
        Args:
            max_chunk_size: Maximum characters per chunk. Sections exceeding
                this are split further by sub-headings or paragraphs.
            include_parents: If True, prefix each chunk with its parent
                heading(s) for context.
        """
        self.max_chunk_size = max_chunk_size
        self.include_parents = include_parents

    def _detect_heading_level(self, line: str) -> int:
        """Return a heading level (lower = higher priority) or 999 for non-headings."""
        stripped = line.strip()
        # Markdown headings: level = number of '#' characters
        md_match = re.match(r'^(#{1,4})\s', stripped)
        if md_match:
            return len(md_match.group(1))
        # Chương = level 2 (chapter-level)
        if re.match(r'^Chương\s+[IVXLCDM\d]', stripped, re.IGNORECASE):
            return 2
        # Điều = level 3 (article-level)
        if re.match(r'^Điều\s+\d+\.', stripped):
            return 3
        return 999

    def _split_at_headings(self, text: str) -> list[tuple[str, str]]:
        """Split text into (heading_line, body) pairs at heading boundaries.

        Returns a list of tuples where:
            - heading_line: the heading text (empty string for preamble)
            - body: the content under that heading
        """
        positions = [m.start() for m in self._SPLIT_PATTERN.finditer(text)]

        if not positions:
            return [("", text)]

        sections: list[tuple[str, str]] = []

        # Preamble: text before the first heading
        if positions[0] > 0:
            preamble = text[: positions[0]].strip()
            if preamble:
                sections.append(("", preamble))

        for i, pos in enumerate(positions):
            end = positions[i + 1] if i + 1 < len(positions) else len(text)
            section_text = text[pos:end].strip()
            if not section_text:
                continue
            # First line is the heading
            first_newline = section_text.find("\n")
            if first_newline == -1:
                heading_line = section_text
                body = ""
            else:
                heading_line = section_text[:first_newline].strip()
                body = section_text[first_newline:].strip()
            sections.append((heading_line, body))

        return sections

    def chunk(self, text: str) -> list[str]:
        """Split text into chunks by headings/sections.

        Each chunk contains one section. Oversized sections are further split
        by paragraphs. Parent headings are prepended for context when
        ``include_parents`` is True.
        """
        if not text:
            return []

        sections = self._split_at_headings(text)
        if not sections:
            return [text] if text.strip() else []

        chunks: list[str] = []
        # Track the current parent headings at each level for context
        parent_headings: dict[int, str] = {}

        for heading_line, body in sections:
            # Update parent heading context
            if heading_line:
                level = self._detect_heading_level(heading_line)
                parent_headings[level] = heading_line
                # Clear deeper levels when a higher-level heading appears
                for lvl in list(parent_headings.keys()):
                    if lvl > level:
                        del parent_headings[lvl]

            # Build the chunk content
            if self.include_parents and heading_line:
                # Collect parent context (headings at levels above current)
                current_level = self._detect_heading_level(heading_line)
                parents = []
                for lvl in sorted(parent_headings.keys()):
                    if lvl < current_level:
                        parents.append(parent_headings[lvl])
                context_prefix = "\n".join(parents)
                if context_prefix:
                    full_section = f"{context_prefix}\n\n{heading_line}\n\n{body}".strip()
                else:
                    full_section = f"{heading_line}\n\n{body}".strip()
            elif heading_line:
                full_section = f"{heading_line}\n\n{body}".strip()
            else:
                full_section = body.strip()

            if not full_section:
                continue

            # If section fits within max_chunk_size, keep as one chunk
            if len(full_section) <= self.max_chunk_size:
                chunks.append(full_section)
            else:
                # Split oversized sections by paragraphs (double newline)
                chunks.extend(self._split_by_paragraphs(full_section))

        return chunks

    def _split_by_paragraphs(self, text: str) -> list[str]:
        """Split an oversized section into smaller chunks at paragraph boundaries."""
        paragraphs = re.split(r'\n\n+', text)
        result: list[str] = []
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            candidate = f"{current}\n\n{para}".strip() if current else para
            if len(candidate) <= self.max_chunk_size:
                current = candidate
            else:
                if current:
                    result.append(current)
                # If a single paragraph exceeds max_chunk_size, include it anyway
                current = para

        if current:
            result.append(current)
        return result


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_product = _dot(vec_a, vec_b)
    mag_a = math.sqrt(_dot(vec_a, vec_a))
    mag_b = math.sqrt(_dot(vec_b, vec_b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        chunkers = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=0),
            "by_sentences": SentenceChunker(),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }
        result: dict = {}
        for name, chunker in chunkers.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count > 0 else 0
            result[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }
        return result
