from __future__ import annotations

import re


class HeadingChunker:
    """Custom chunking strategy: split by heading/section markers, not by size.

    Design rationale: corpus nhóm trộn hai kiểu văn bản — trang FAQ thông thường
    (chỉ có 1 tiêu đề `#` ở đầu) và văn bản quy chế học vụ chính thức
    (`quy-che-dao-tao-tin-chi.md`) vốn đã được đánh số `CHƯƠNG ...` / `Điều N. ...`
    như luật. FixedSizeChunker cắt cứng theo ký tự có thể chặt đôi một Điều luật
    giữa chừng; HeadingChunker giữ mỗi `Điều`/`CHƯƠNG`/tiêu đề markdown làm một
    chunk riêng để mỗi chunk là một quy định trọn vẹn, dễ trace ngược về đúng
    điều khoản khi trả lời câu hỏi loại "mức học bổng tối đa là bao nhiêu?".
    Section nào vẫn dài hơn chunk_size mới được chẻ tiếp theo đoạn (`\n\n`).
    """

    HEADING_PATTERN = re.compile(
        r"^(#{1,6}\s+.+|CHƯƠNG\s+[IVXLCDM\d]+.*|Điều\s+\d+\..*)$",
        re.MULTILINE,
    )

    def __init__(self, chunk_size: int = 800) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        matches = list(self.HEADING_PATTERN.finditer(text))
        if not matches:
            return self._split_long(text.strip())

        sections: list[str] = []
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections.append(preamble)

        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            section = text[start:end].strip()
            if section:
                sections.append(section)

        chunks: list[str] = []
        for section in sections:
            chunks.extend(self._split_long(section))
        return chunks

    def _split_long(self, section: str) -> list[str]:
        if not section:
            return []
        if len(section) <= self.chunk_size:
            return [section]

        paragraphs = section.split("\n\n")
        chunks: list[str] = []
        buffer = ""
        for paragraph in paragraphs:
            candidate = f"{buffer}\n\n{paragraph}" if buffer else paragraph
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.append(buffer)
            buffer = paragraph
        if buffer:
            chunks.append(buffer)
        return chunks
