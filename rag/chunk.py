"""把 data 目录里的 Markdown 切成带书名、篇、章号的块。

《论语》原文一块一章。注疏在同一篇里按原文开头八个汉字对齐章号。
礼、家语、史记按二级标题切，过长再按句号切开。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from rag.config import DATA_DIR, MAX_CHUNK_CHARS

PIAN_RE = re.compile(
    r"(?:学而|为政|八佾|里仁|公冶长|雍也|述而|泰伯|子罕|乡党|先进|"
    r"[颜顔]渊|子路|宪问|[卫衞]灵公|季氏|阳货|微子|子张|[尧堯]曰)"
    r"第[一二三四五六七八九十百零]+"
)
ZHANG_RE = re.compile(r"^(\d+\.\d+)\s*(.+)$", re.S)
VARIANT = str.maketrans({"顔": "颜", "衞": "卫", "堯": "尧"})
HEAD_HAN = 8
HEAD_WINDOW = 24


@dataclass
class Chapter:
    pian: str
    zhang: str
    text: str
    anchor: str
    key: str


@dataclass
class Chunk:
    id: str
    content: str
    book: str
    layer: str
    pian: str
    zhang: str
    anchor: str
    part: int
    source: str
    meta: dict = field(default_factory=dict)


# 只用于对齐，不改写入正文。这些字在各书里常混用。
FOLD = str.maketrans(
    {
        "於": "于",
        "説": "说",
        "悅": "说",
        "悦": "说",
        "遠": "远",
        "逺": "远",
        "後": "后",
    }
)


def han_only(text: str) -> str:
    return "".join(ch for ch in text.translate(FOLD) if "\u4e00" <= ch <= "\u9fff")


def strip_notes(text: str) -> str:
    """去掉注疏夹在引文中间的（马曰……）一类注文，方便和原文逐字对齐。"""
    previous = None
    current = text
    while previous != current:
        previous = current
        current = re.sub(r"（[^（）]*）", "", current)
        current = re.sub(r"\([^()]*\)", "", current)
    return current


LINE_PIAN = re.compile(
    r"^(?:论语)?"
    r"((?:学而|为政|八佾|里仁|公冶长|雍也|述而|泰伯|子罕|乡党|先进|"
    r"[颜顔]渊|子路|宪问|[卫衞]灵公|季氏|阳货|微子|子张|[尧堯]曰)"
    r"第[一二三四五六七八九十百零]+)"
)


def first_sentence(text: str, limit: int = 42) -> str:
    compact = re.sub(r"\s+", "", text.strip())
    matched = re.match(r"^.{1,42}?[。？！]", compact)
    if matched:
        return matched.group(0)
    return compact[:limit]


def layer_of(filename: str) -> str:
    if filename == "论语.md":
        return "原文"
    if filename.startswith("论语"):
        return "注疏"
    if "礼记" in filename:
        return "礼"
    return "史传"


def parse_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    title = ""
    sections: list[tuple[str, str]] = []
    heading = ""
    buf: list[str] = []
    seen_heading = False

    def flush() -> None:
        nonlocal buf
        body = "\n".join(buf).strip()
        buf = []
        if body:
            sections.append((heading, body))

    for line in text.lstrip("\ufeff").splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            flush()
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            seen_heading = True
            continue
        buf.append(line)
    flush()
    if not seen_heading and sections:
        return title, [("", sections[0][1] if len(sections) == 1 else "\n\n".join(body for _, body in sections))]
    return title, sections


def paragraphs(body: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", body.strip()) if part.strip()]


def pian_in(heading: str) -> str | None:
    matched = PIAN_RE.search(heading.translate(VARIANT))
    if not matched:
        return None
    return matched.group(0)


def load_original(data_dir: Path) -> tuple[dict[str, list[Chapter]], list[Chunk]]:
    path = data_dir / "论语.md"
    title, sections = parse_sections(path.read_text(encoding="utf-8"))
    book = title or "论语"
    by_pian: dict[str, list[Chapter]] = {}
    chunks: list[Chunk] = []
    for heading, body in sections:
        pian = pian_in(heading) or heading
        chapters: list[Chapter] = []
        for para in paragraphs(body):
            matched = ZHANG_RE.match(para.replace("\n", ""))
            if not matched:
                continue
            zhang, text = matched.group(1), matched.group(2).strip()
            key = han_only(text)[:HEAD_HAN]
            chapter = Chapter(pian, zhang, text, first_sentence(text), key)
            chapters.append(chapter)
            chunks.append(
                make_chunk(
                    book=book,
                    layer="原文",
                    pian=pian,
                    zhang=zhang,
                    anchor=chapter.anchor,
                    body=text,
                    part=0,
                    source=path.name,
                )
            )
        if pian:
            by_pian[pian] = chapters
    return by_pian, chunks


def align_section(body: str, chapters: list[Chapter]) -> list[tuple[str, str, str]]:
    """返回 (章号, 正文, 锚点)。对不上的段落章号为空。"""
    if not chapters:
        return [("", body, first_sentence(body))]

    keys = [(chapter.zhang, chapter.key, chapter.anchor) for chapter in chapters if len(chapter.key) >= 6]
    assigned: list[tuple[str, str]] = []
    expected = 0
    current = ""

    for para in paragraphs(body):
        head = han_only(strip_notes(para))[:HEAD_WINDOW]
        found = -1
        for index, (zhang, key, _anchor) in enumerate(keys):
            if index < expected:
                continue
            if key and key in head:
                found = index
                break
        if found >= 0:
            current = keys[found][0]
            expected = found + 1
            assigned.append((current, para))
            continue
        if current:
            assigned.append((current, para))
        else:
            assigned.append(("", para))

    merged: list[tuple[str, list[str]]] = []
    for zhang, para in assigned:
        if merged and merged[-1][0] == zhang:
            merged[-1][1].append(para)
        else:
            merged.append((zhang, [para]))

    anchors = {chapter.zhang: chapter.anchor for chapter in chapters}
    pieces: list[tuple[str, str, str]] = []
    for zhang, parts in merged:
        text = "\n\n".join(parts).strip()
        if not text:
            continue
        anchor = anchors.get(zhang, "") if zhang else first_sentence(text)
        pieces.append((zhang, text, anchor))
    matched = sum(1 for zhang, _text, _anchor in pieces if zhang)
    if matched < max(3, len(chapters) // 2):
        sliced = slice_by_keys(body, chapters)
        if sliced:
            return sliced
    return pieces


def slice_by_keys(body: str, chapters: list[Chapter]) -> list[tuple[str, str, str]] | None:
    """一篇注疏挤在同一段里时，按原文开头的汉字顺序切开。"""
    cleaned = strip_notes(body)
    han: list[str] = []
    indexes: list[int] = []
    for index, char in enumerate(cleaned):
        folded = char.translate(FOLD)
        if "\u4e00" <= folded <= "\u9fff":
            han.append(folded)
            indexes.append(index)
    haystack = "".join(han)
    cursor = 0
    found: list[tuple[int, Chapter]] = []
    for chapter in chapters:
        if len(chapter.key) < 6:
            continue
        position = haystack.find(chapter.key, cursor)
        if position < 0:
            continue
        found.append((indexes[position], chapter))
        cursor = position + len(chapter.key)
    if len(found) < max(3, len(chapters) // 2):
        return None
    pieces: list[tuple[str, str, str]] = []
    front = cleaned[: found[0][0]].strip()
    if front:
        pieces.append(("", front, first_sentence(front)))
    for index, (start, chapter) in enumerate(found):
        end = found[index + 1][0] if index + 1 < len(found) else len(cleaned)
        text = cleaned[start:end].strip()
        if text:
            pieces.append((chapter.zhang, text, chapter.anchor))
    return pieces


def split_on_pian_lines(heading: str, body: str) -> list[tuple[str, str]]:
    """没有二级标题的注本，按单独成行的篇名切开。"""
    if pian_in(heading):
        return [(heading, body)]
    lines = body.splitlines()
    cuts: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        matched = LINE_PIAN.match(line.strip().translate(VARIANT))
        if matched:
            cuts.append((index, matched.group(1).translate(VARIANT)))
    if len(cuts) < 2:
        return [(heading, body)]
    sections: list[tuple[str, str]] = []
    front = "\n".join(lines[: cuts[0][0]]).strip()
    if front:
        sections.append((heading, front))
    for index, (start, pian) in enumerate(cuts):
        end = cuts[index + 1][0] if index + 1 < len(cuts) else len(lines)
        text = "\n".join(lines[start:end]).strip()
        if text:
            sections.append((pian, text))
    return sections


def split_long(text: str, limit: int = MAX_CHUNK_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]
    sentences = re.split(r"(?<=[。？！])", text)
    parts: list[str] = []
    buf = ""
    for sentence in sentences:
        if not sentence:
            continue
        if buf and len(buf) + len(sentence) > limit:
            parts.append(buf.strip())
            buf = sentence
        else:
            buf += sentence
    if buf.strip():
        parts.append(buf.strip())
    wrapped: list[str] = []
    for part in parts or [text]:
        rest = part.strip()
        while len(rest) > limit:
            wrapped.append(rest[:limit])
            rest = rest[limit:]
        if rest:
            wrapped.append(rest)
    return wrapped or [text]


def make_chunk(
    book: str,
    layer: str,
    pian: str,
    zhang: str,
    anchor: str,
    body: str,
    part: int,
    source: str,
) -> Chunk:
    label = f"《{book}》"
    if pian:
        label += pian
    if zhang:
        label += f" · {zhang}"
    content = f"{label}\n{body.strip()}"
    chunk_id = f"{book}|{pian}|{zhang}|{part}|{source}"
    return Chunk(
        id=chunk_id,
        content=content,
        book=book,
        layer=layer,
        pian=pian,
        zhang=zhang,
        anchor=anchor,
        part=part,
        source=source,
    )


def chunks_from_pieces(
    book: str,
    layer: str,
    pian: str,
    pieces: list[tuple[str, str, str]],
    source: str,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    seen: dict[tuple[str, str], int] = {}
    for zhang, text, anchor in pieces:
        for piece in split_long(text):
            key = (pian, zhang)
            part = seen.get(key, 0)
            seen[key] = part + 1
            body = piece
            if part > 0 and anchor and anchor not in piece:
                body = anchor + "\n" + piece
            chunks.append(
                make_chunk(
                    book=book,
                    layer=layer,
                    pian=pian,
                    zhang=zhang,
                    anchor=anchor,
                    body=body,
                    part=part,
                    source=source,
                )
            )
    return chunks


def chunk_other(path: Path, book: str, layer: str) -> list[Chunk]:
    _title, sections = parse_sections(path.read_text(encoding="utf-8"))
    chunks: list[Chunk] = []
    if not sections:
        return chunks
    for heading, body in sections:
        pian = pian_in(heading) or heading
        pieces = [("", body, first_sentence(body))]
        chunks.extend(chunks_from_pieces(book, layer, pian, pieces, path.name))
    return chunks


def chunk_commentary(path: Path, book: str, original: dict[str, list[Chapter]]) -> list[Chunk]:
    _title, sections = parse_sections(path.read_text(encoding="utf-8"))
    chunks: list[Chunk] = []
    expanded: list[tuple[str, str]] = []
    for heading, body in sections:
        expanded.extend(split_on_pian_lines(heading, body))
    for heading, body in expanded:
        pian = pian_in(heading) or ""
        chapters = original.get(pian, []) if pian else []
        if chapters:
            pieces = align_section(body, chapters)
        else:
            label = heading or ""
            pieces = [("", body, first_sentence(body))]
            pian = label
        chunks.extend(chunks_from_pieces(book, "注疏", pian, pieces, path.name))
    return chunks


def build_chunks(data_dir: Path | None = None) -> list[Chunk]:
    data_dir = data_dir or DATA_DIR
    original, base_chunks = load_original(data_dir)
    chunks = list(base_chunks)
    for path in sorted(data_dir.glob("*.md")):
        if path.name == "论语.md":
            continue
        title, _sections = parse_sections(path.read_text(encoding="utf-8"))
        book = title or path.stem
        layer = layer_of(path.name)
        if layer == "注疏":
            chunks.extend(chunk_commentary(path, book, original))
        else:
            chunks.extend(chunk_other(path, book, layer))
    return dedupe_ids(chunks)


def dedupe_ids(chunks: list[Chunk]) -> list[Chunk]:
    seen: dict[str, int] = {}
    out: list[Chunk] = []
    for chunk in chunks:
        count = seen.get(chunk.id, 0)
        seen[chunk.id] = count + 1
        if count:
            chunk = Chunk(
                id=f"{chunk.id}#{count}",
                content=chunk.content,
                book=chunk.book,
                layer=chunk.layer,
                pian=chunk.pian,
                zhang=chunk.zhang,
                anchor=chunk.anchor,
                part=chunk.part,
                source=chunk.source,
            )
        out.append(chunk)
    return out


def summarize(chunks: list[Chunk]) -> str:
    lines: list[str] = []
    by_source: dict[str, list[Chunk]] = {}
    for chunk in chunks:
        by_source.setdefault(chunk.source, []).append(chunk)
    lines.append(f"共 {len(chunks)} 块，来自 {len(by_source)} 个文件")
    for source, group in by_source.items():
        with_zhang = sum(1 for chunk in group if chunk.zhang)
        lines.append(
            f"{source}\t{group[0].layer}\t块 {len(group)}\t有章号 {with_zhang}"
        )
    return "\n".join(lines)


def sample_zhang(chunks: list[Chunk], zhang: str = "1.1", limit: int = 20) -> str:
    lines = [f"章 {zhang} 样例"]
    shown = 0
    for chunk in chunks:
        if chunk.zhang != zhang or chunk.part != 0:
            continue
        preview = chunk.content.replace("\n", " ")[:72]
        lines.append(f"- {chunk.layer} {chunk.book} | {preview}")
        shown += 1
        if shown >= limit:
            break
    return "\n".join(lines)
