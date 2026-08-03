"""Chiến lược chunking tùy chỉnh cho corpus quy định / dịch vụ đại học (K3).

Không nằm trong phần TODO bắt buộc của Giai đoạn 1 — đây là chiến lược nhóm
thiết kế thêm cho Giai đoạn 2.
"""

from __future__ import annotations

import re


class HeadingChunker:
    """Chia tài liệu theo ranh giới tiêu đề/mục của văn bản hành chính.

    Lý do thiết kế: corpus K3 là quy định/nội quy đại học, gần như luôn được
    đánh số theo "Chương … / Điều N. … / I) … / 1. …". Một điều khoản là một
    đơn vị ngữ nghĩa trọn vẹn ("điều kiện + hệ quả"); cắt theo số ký tự sẽ tách
    đôi điều khoản, còn cắt theo tiêu đề thì mỗi chunk trả lời được trọn một câu
    hỏi và luôn mang theo tiêu đề của chính nó để nhúng (embed).

    Ba bước:
        1. Cắt tại mỗi dòng là tiêu đề; tiêu đề đi kèm phần thân bên dưới nó.
        2. Gộp các mục quá ngắn với mục kế tiếp (tránh chunk chỉ có tiêu đề).
        3. Cắt nhỏ mục quá dài theo ranh giới đoạn, có lặp lại dòng tiêu đề
           ở đầu mỗi phần để không mất ngữ cảnh.
    """

    HEADING = re.compile(
        r"^\s*("
        r"Điều\s+\d+|CHƯƠNG\s+[IVXLC\d]+|Chương\s+[IVXLC\d]+|"
        r"Mục\s+\d+|MỤC\s+\d+|Phần\s+\d+|"
        r"[IVX]+\)|[IVX]+\.\s|"
        r"\d+(\.\d+)*[.)]\s|"
        r"#{1,6}\s"
        r")"
    )

    def __init__(self, chunk_size: int = 900, min_chunk_size: int = 120) -> None:
        self.chunk_size = chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = self._split_on_headings(text)
        sections = self._merge_short(sections)

        chunks: list[str] = []
        for section in sections:
            chunks.extend(self._split_long(section))
        return chunks

    def _split_on_headings(self, text: str) -> list[str]:
        sections: list[list[str]] = []
        current: list[str] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            if self.HEADING.match(line) and current:
                sections.append(current)
                current = []
            current.append(line.strip())
        if current:
            sections.append(current)
        return ["\n".join(section) for section in sections]

    def _merge_short(self, sections: list[str]) -> list[str]:
        merged: list[str] = []
        for section in sections:
            if merged and len(merged[-1]) < self.min_chunk_size:
                merged[-1] = f"{merged[-1]}\n{section}"
            else:
                merged.append(section)
        return merged

    def _split_long(self, section: str) -> list[str]:
        if len(section) <= self.chunk_size:
            return [section]

        lines = section.splitlines()
        heading, body = lines[0], lines[1:]
        parts: list[str] = []
        buffer = heading
        for line in body:
            candidate = f"{buffer}\n{line}"
            if len(candidate) <= self.chunk_size or buffer == heading:
                buffer = candidate
            else:
                parts.append(buffer)
                buffer = f"{heading} (tiếp)\n{line}"   # giữ tiêu đề ở mọi phần
        parts.append(buffer)
        return parts
