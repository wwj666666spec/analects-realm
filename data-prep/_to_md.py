# -*- coding: utf-8 -*-
from pathlib import Path

folder = Path(__file__).resolve().parent

for src in sorted(folder.glob("*.txt")):
    raw = src.read_text(encoding="utf-8-sig")
    lines = [line.strip().strip("\u3000") for line in raw.splitlines()]
    paras = [line for line in lines if line]
    if not paras:
        continue
    title = paras[0]
    rest = paras[1:]
    blocks = [f"# {title}"]
    if rest and rest[0] == "司马迁":
        blocks.append(rest[0])
        rest = rest[1:]
    blocks.extend(rest)
    dst = src.with_suffix(".md")
    dst.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    src.unlink()
    print(dst.name, len(blocks))
