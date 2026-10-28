"""书库目录。只读本地 Markdown，不重新入库。"""

from __future__ import annotations

import re
from pathlib import Path

from rag.chunk import layer_of
from rag.config import DATA_DIR
from rag.llm import AskError

CATEGORIES = (
    ("原文", "《论语》正文"),
    ("注疏", "各家对《论语》的解释"),
    ("礼", "《礼记》及相关"),
    ("史传", "史记、家语、集语"),
)
SECTION_LIMIT = 8000


def _path(name: str) -> Path:
    stem = name.strip()
    if not stem or any(mark in stem for mark in ("/", "\\", "..")):
        raise AskError("没有这本书。")
    path = (DATA_DIR / f"{stem}.md").resolve()
    if path.parent != DATA_DIR.resolve() or not path.is_file():
        raise AskError("没有这本书。")
    return path


def catalog() -> list[dict]:
    grouped: dict[str, list[str]] = {key: [] for key, _desc in CATEGORIES}
    for path in sorted(DATA_DIR.glob("*.md"), key=lambda item: item.stem):
        grouped[layer_of(path.name)].append(path.stem)
    return [
        {"id": key, "name": key, "desc": desc, "books": grouped[key]}
        for key, desc in CATEGORIES
    ]


def flat_books() -> list[dict[str, str]]:
    """扁平书目，供前端直接渲染，避免只依赖分类映射。"""
    items: list[dict[str, str]] = []
    for group in catalog():
        for name in group["books"]:
            items.append(
                {
                    "id": name,
                    "title": name,
                    "group": group["id"],
                    "desc": group["desc"],
                }
            )
    return items


def outline(name: str) -> dict:
    path = _path(name)
    sections = _split(path.read_text(encoding="utf-8"))
    return {
        "name": path.stem,
        "layer": layer_of(path.name),
        "sections": [{"index": index, "title": title} for index, title, _body in sections],
    }


def section_text(name: str, index: int) -> dict:
    path = _path(name)
    sections = _split(path.read_text(encoding="utf-8"))
    if index < 0 or index >= len(sections):
        raise AskError("没有这一节。")
    title, body = sections[index][1], sections[index][2]
    truncated = len(body) > SECTION_LIMIT
    if truncated:
        body = body[:SECTION_LIMIT] + "…"
    return {"name": path.stem, "title": title, "text": body, "truncated": truncated}


def _split(text: str) -> list[tuple[int, str, str]]:
    chunks = re.split(r"(?m)^## ", text.lstrip("\ufeff"))
    sections: list[tuple[str, str]] = []
    preface = re.sub(r"^# .+\n?", "", chunks[0], count=1).strip()
    if preface and len(chunks) == 1:
        sections.append(("正文", preface))
    elif preface:
        sections.append(("卷首", preface))
    for chunk in chunks[1:]:
        title, _, body = chunk.partition("\n")
        sections.append((title.strip() or "未名", body.strip()))
    if not sections:
        sections.append(("正文", text.strip()))
    return [(index, title, body) for index, (title, body) in enumerate(sections)]
