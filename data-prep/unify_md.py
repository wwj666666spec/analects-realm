# -*- coding: utf-8 -*-
"""把 data 目录里的 md 统一成两级标题。

# 用文件名（译文两篇用「史记·篇名译文」）。
## 只标原文里单独成行的篇、卷、序、提要、凡例、目录。
不新加章节编号，不改动句子里的文字。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "data"

SKIP = {"论语.md", "史记孔子世家.md", "史记仲尼弟子列传.md"}
TRANS = {
    "史记孔子世家-翻译.md": "史记·孔子世家译文",
    "史记仲尼弟子列传-翻译.md": "史记·仲尼弟子列传译文",
}

LUNYU_PIAN = re.compile(
    r"^(?:学而|为政|八佾|里仁|公冶长|雍也|述而|泰伯|子罕|乡党|先进|"
    r"[颜顔]渊|子路|宪问|[卫衞]灵公|季氏|阳货|微子|子张|[尧堯]曰)"
    r"第[一二三四五六七八九十百零]+$"
)
LIJI_PIAN = re.compile(r"^[\u4e00-\u9fff]{2,14}第[一二三四五六七八九十百零]+$")
JUAN = re.compile(r"^卷[一二三四五六七八九十百零]+$")
JUAN_PIAN = re.compile(r"^卷[一二三四五六七八九十百零]+[ \t\u3000]+\S.{0,30}$")
JIAYU_JUAN = re.compile(r"^(?:孔子家语)?卷[一二三四五六七八九十百零]+$")
JIAYU_PIAN = re.compile(r"^[\u4e00-\u9fff]{2,12}第[一二三四五六七八九十百零]+$")
JIYU_SEC = re.compile(r"^［([^］]+)］(（[上下]）)?$")
LIJI_MARK = re.compile(r"^《礼记([^》]+)》$")

LUNYU_STRUCT = {"论语全解", "论语学案", "论语意原", "论语笔解", "论语集注"}
LUNYU_TIYAO = {"论语商", "论语拾遗", "论语稽求篇", "论语类考", "论语集说", "论语集解义疏"}
LIJI_PIAN_FILES = {"礼记大全", "礼记述注", "礼记集说"}
LIJI_TIYAO = {"礼记析疑", "礼记训义择言", "礼记纂言"}

TONG_NAMES = {
    "玉藻", "明堂位", "丧服小记", "大传", "少仪", "学记", "乐记", "杂记",
    "丧大记", "祭法", "祭义", "祭统", "经解", "哀公问", "仲尼燕居", "孔子闲居",
    "坊记", "中庸", "表记", "缁衣", "奔丧", "问丧", "服问", "间传", "三年问",
    "深衣", "投壶", "儒行", "大学", "昏义", "乡饮酒义", "燕义", "聘义", "丧服四制",
    "射义", "冠义",
}
TONG_EXTRA = "冠义冠，古乱反。"


def han(text: str) -> int:
    return sum(1 for c in text if "\u4e00" <= c <= "\u9fff")


def nonempty(text: str) -> list[str]:
    rows = []
    for line in text.splitlines():
        s = line.strip().strip("\u3000").strip()
        if s:
            rows.append(s)
    return rows


def drop_duplicate_title(stem: str, rows: list[str]) -> list[str]:
    if rows and rows[0] == stem:
        return rows[1:]
    return rows


def heading_of(stem: str, line: str) -> str | None:
    if stem in LUNYU_STRUCT:
        if line == "提要" or LUNYU_PIAN.match(line):
            return line
        return None
    if stem == "论语注疏" and line.startswith("●"):
        inner = line[1:]
        if inner == "（序）":
            return "序"
        return inner
    if stem == "论语点睛补注":
        if line.startswith("【") and line.endswith("】"):
            inner = line[1:-1]
            if inner == "论语点睛补注下" or LUNYU_PIAN.match(inner):
                return inner
        return None
    if stem in LUNYU_TIYAO:
        return line if line == "提要" else None
    if stem == "论语集释":
        return line if line == "凡例" else None
    if stem in LIJI_PIAN_FILES:
        if line == "提要" or LIJI_PIAN.match(line):
            return line
        return None
    if stem == "礼记正义":
        if line == "序" or JUAN_PIAN.match(line):
            return line
        return None
    if stem == "礼记注疏":
        if line == "目录" or JUAN.match(line):
            return line
        return None
    if stem in LIJI_TIYAO:
        return line if line == "提要" else None
    if stem == "孔子家语":
        if JIAYU_JUAN.match(line) or JIAYU_PIAN.match(line):
            return line
        return None
    if stem == "孔子集语":
        if line in {"序", "表"} or JUAN.match(line):
            return line
        m = JIYU_SEC.match(line)
        if m:
            return m.group(1) + (m.group(2) or "")
        return None
    if stem == "礼记通论辑本":
        if line in TONG_NAMES or line == TONG_EXTRA:
            return line
        return None
    return None


def blocks_for(stem: str, rows: list[str]) -> list[str]:
    if stem == "礼记":
        return blocks_liji(rows)
    out = []
    for line in rows:
        title = heading_of(stem, line)
        out.append(f"## {title}" if title else line)
    return out


def blocks_liji(rows: list[str]) -> list[str]:
    idx = next(i for i, line in enumerate(rows) if LIJI_MARK.match(line))
    out = ["## 目录", *rows[:idx]]
    for line in rows[idx:]:
        m = LIJI_MARK.match(line)
        out.append(f"## {m.group(1)}" if m else line)
    return out


def render(title: str, blocks: list[str]) -> str:
    return "\n\n".join([f"# {title}", *blocks]) + "\n"


def h1_of(name: str) -> str:
    if name in TRANS:
        return TRANS[name]
    return Path(name).stem


def convert_file(path: Path, write: bool) -> tuple[str, int, int, list[str]]:
    old = path.read_text(encoding="utf-8")
    if path.name in TRANS:
        lines = old.splitlines(keepends=True)
        ending = "\n"
        if lines and lines[0].endswith("\r\n"):
            ending = "\r\n"
        elif lines and lines[0].endswith("\r"):
            ending = "\r"
        lines[0] = "# " + TRANS[path.name] + ending
        new = "".join(lines)
        heads: list[str] = []
        if write and new != old:
            path.write_text(new, encoding="utf-8")
        return path.name, han(old), han(new), heads
    stem = path.stem
    rows = drop_duplicate_title(stem, nonempty(old))
    blocks = blocks_for(stem, rows)
    new = render(stem, blocks)
    heads = [b[3:] for b in blocks if b.startswith("## ")]
    if write:
        path.write_text(new, encoding="utf-8")
    return path.name, han(old), han(new), heads


def already_done(path: Path, text: str) -> bool:
    first = text.lstrip("\ufeff").splitlines()[0].strip() if text.strip() else ""
    if path.name in TRANS:
        return first == "# " + TRANS[path.name]
    return first.startswith("# ")


def main() -> None:
    write = "--write" in sys.argv
    report = []
    for path in sorted((ROOT).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if path.name in SKIP or already_done(path, text):
            report.append(f"{path.name}\tSKIP\t{han(text)}")
            continue
        name, before, after, heads = convert_file(path, write)
        report.append(f"{name}\t{before}\t{after}\t{after - before}\theadings={len(heads)}")
        for h in heads:
            report.append(f"  ## {h}")
    out = Path(__file__).resolve().parent / "unify_headings.txt"
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {out.name} write={write}")


if __name__ == "__main__":
    main()
