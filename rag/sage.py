"""先贤围坐与私聊。人设在 rag/sages，检索仍走现有典籍库。"""

from __future__ import annotations

import argparse
import random
import re
from dataclasses import dataclass
from pathlib import Path

from rag.llm import AskError, complete
from rag.search import Hit, search

SAGES_DIR = Path(__file__).resolve().parent / "sages"
CONTEXT_CHARS = 700
MIN_SPEAKERS = 4
MAX_SPEAKERS = 5

_LENGTH_BIAS = {
    "kongzi": ("short", "medium", "medium"),
    "zilu": ("short", "short", "medium"),
    "yanhui": ("short", "medium"),
    "zigong": ("medium", "long"),
    "zaiyu": ("short", "medium"),
    "zengzi": ("medium", "medium", "long"),
    "minzi": ("short", "medium"),
    "ranqiu": ("short", "medium"),
    "zizhang": ("medium", "long"),
    "zixia": ("medium", "long"),
    "ziyou": ("short", "medium"),
    "zhonggong": ("medium", "long"),
    "zengdian": ("short", "medium"),
    "gongxihua": ("short", "medium"),
    "fanchi": ("short", "medium"),
    "simaniu": ("short", "short", "medium"),
    "gaochai": ("short", "short"),
}

_LENGTH_HINT = {
    "short": "只说一两句，短促自然，不要展开。",
    "medium": "说一小段即可，大约三四句，点到为止。",
    "long": "可以稍长一些，把一层意思说清楚，但仍保持一段，不要写成提纲。",
}

_LENGTH_TOKENS = {"short": 160, "medium": 320, "long": 520}

_STANCE = {
    "kongzi": "点明关键即可，话不要太满，留给后面的人。",
    "zilu": "性情刚直，说话干脆，重做事。",
    "yanhui": "性情温润，话少而细。",
    "zigong": "善言辞，分寸清楚。",
    "zaiyu": "好问、敢疑，不怕顶一句。",
    "zengzi": "重内省，常把话收到自己身上。",
    "minzi": "孝悌、少争，语气缓。",
    "ranqiu": "务实，先问能不能办到。",
    "zizhang": "才高意广，格局开一些。",
    "zixia": "重小节，爱落到一句、一礼上。",
    "ziyou": "重礼乐教化，语气温。",
    "zhonggong": "敬与恕，讲究分寸。",
    "zengdian": "疏朗，不爱把场面绷紧。",
    "gongxihua": "娴于辞令，留意场面与时机。",
    "fanchi": "问得朴实，常落到日用上。",
    "simaniu": "多忧，心里过不去时会说出来。",
    "gaochai": "憨直守礼，话短。",
}

_GREETING = {
    "你好",
    "您好",
    "嗨",
    "哈喽",
    "哈啰",
    "hello",
    "hi",
    "在吗",
    "在么",
    "在不在",
    "有人吗",
    "早上好",
    "下午好",
    "晚上好",
    "早安",
    "午安",
    "晚安",
    "你好吗",
    "最近怎么样",
    "谢谢",
    "谢谢你",
    "感谢",
    "多谢",
    "再见",
    "拜拜",
    "再会",
}


@dataclass(frozen=True)
class Sage:
    id: str
    name: str
    aliases: tuple[str, ...]


SAGES: tuple[Sage, ...] = (
    Sage("kongzi", "孔子", ("夫子", "孔丘", "仲尼")),
    Sage("zilu", "子路", ("仲由", "季路")),
    Sage("yanhui", "颜回", ("子渊", "颜渊")),
    Sage("minzi", "闵子骞", ("闵损",)),
    Sage("zigong", "子贡", ("端木赐",)),
    Sage("zaiyu", "宰予", ("宰我", "子我")),
    Sage("zengzi", "曾参", ("曾子", "子舆")),
    Sage("ranqiu", "冉求", ("冉有", "子有")),
    Sage("gongxihua", "公西华", ("公西赤", "子华")),
    Sage("zengdian", "曾点", ("曾皙", "点")),
    Sage("zhonggong", "仲弓", ("冉雍",)),
    Sage("zixia", "子夏", ("卜商",)),
    Sage("ziyou", "子游", ("言偃",)),
    Sage("zizhang", "子张", ("颛孙师",)),
    Sage("fanchi", "樊迟", ("樊须", "子迟")),
    Sage("simaniu", "司马牛", ("司马耕", "子牛")),
    Sage("gaochai", "高柴", ("子羔",)),
)

_BY_ID = {sage.id: sage for sage in SAGES}


def _core(query: str) -> str:
    text = re.sub(r"[^\w]+", "", query.strip().lower(), flags=re.UNICODE)
    return re.sub(r"[呀啊呢吧哦哟哈嗯啦]+$", "", text)


def is_greeting(query: str) -> bool:
    return _core(query) in _GREETING


def find_sage(token: str) -> Sage:
    raw = token.strip()
    key = raw.lower()
    for sage in SAGES:
        names = (sage.id, sage.name, *sage.aliases)
        if key in {item.lower() for item in names} or raw in names:
            return sage
    known = "、".join(sage.name for sage in SAGES)
    raise AskError(f"没有这个人：{token}。现在在册的是：{known}")


def skill_text(sage: Sage) -> str:
    path = SAGES_DIR / sage.id / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3 :]
    return text.strip()


def round_rules() -> str:
    return (SAGES_DIR / "round.md").read_text(encoding="utf-8").strip()


def pick_speakers(rng: random.Random | None = None) -> list[Sage]:
    """孔子必在且第一个。一场只请四到五人，其余同门旁听。"""
    rng = rng or random.Random()
    others = [sage for sage in SAGES if sage.id != "kongzi"]
    count = rng.randint(MIN_SPEAKERS, MAX_SPEAKERS)
    chosen = rng.sample(others, count - 1)
    return [_BY_ID["kongzi"], *chosen]


def _source_line(hit: Hit) -> str:
    return f"{hit.layer} 《{hit.book}》{hit.pian}".strip()


def _context(hits: list[Hit]) -> str:
    blocks = []
    for hit in hits:
        body = hit.content.strip()
        if len(body) > CONTEXT_CHARS:
            body = body[:CONTEXT_CHARS] + "…"
        blocks.append(f"{_source_line(hit)}\n{body}")
    return "\n\n".join(blocks)


def _stance(sage: Sage, index: int) -> str:
    if sage.id == "kongzi":
        if index == 0:
            return _STANCE["kongzi"]
        return "你若再开口，只补一句关键的，不要把前面的话重说一遍。"
    return _STANCE.get(sage.id, "按自己的性情说话。")


def _length_plan(sage: Sage, rng: random.Random | None = None) -> tuple[str, str, int]:
    rng = rng or random.Random()
    choices = _LENGTH_BIAS.get(sage.id, ("short", "medium", "long"))
    kind = rng.choice(choices)
    return kind, _LENGTH_HINT[kind], _LENGTH_TOKENS[kind]


def _speak(sage: Sage, query: str, hits: list[Hit], earlier: list[tuple[str, str]], index: int = 0) -> str:
    if earlier:
        said = "\n\n".join(f"{name}：{text}" for name, text in earlier)
    else:
        said = "（你是第一个发言的人。）"
    material = _context(hits) if hits else "（这句不必引用典籍。）"
    _kind, length_hint, max_tokens = _length_plan(sage)
    user = (
        f"用户说：\n{query}\n\n"
        f"检索材料：\n{material}\n\n"
        f"已经发言的人（仅供你了解，不必点名接话）：\n{said}\n\n"
        f"你的性情：{_stance(sage, index)}\n"
        f"篇幅要求：{length_hint}\n"
        "请只以你自己的身份说一段。以现代汉语为主，可夹少量浅近文言。"
        "前面的话知道就好，顺着自己的性情往下说；不要写「我赞同」「我补充」「我反对」这类套话，也不要复述别人刚说过的意思。"
        "不要使用 Markdown，不要写 # 标题。"
    )
    return complete(
        [
            {"role": "system", "content": round_rules() + "\n\n" + skill_text(sage)},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        max_tokens=max_tokens,
    )


def gather(query: str, limit: int = 8) -> list[Hit]:
    if is_greeting(query):
        return []
    return search(query, limit, None)


def _speak_round(speakers: list[Sage], query: str, hits: list[Hit]) -> list[tuple[Sage, str]]:
    """一场围坐只请求一次，按抽中的顺序一次写完。"""
    cards = "\n\n".join(f"【{sage.name}】\n{skill_text(sage)}" for sage in speakers)
    order = "、".join(sage.name for sage in speakers)
    material = _context(hits) if hits else "（这句不必引用典籍。）"
    user = (
        f"用户说：\n{query}\n\n"
        f"检索材料：\n{material}\n\n"
        f"本次发言顺序：{order}\n"
        "孔子第一个说。后面的人要接前面的话，只补自己的角度，不要重复。\n"
        "请按这个顺序一次写完。每个人先单独占一行，只写姓名，下一行起写正文。"
        "正文里不要再单独一行只写姓名。以现代汉语为主，可夹少量浅近文言。"
    )
    raw = complete(
        [
            {"role": "system", "content": round_rules() + "\n\n" + cards},
            {"role": "user", "content": user},
        ],
        temperature=0.6,
        max_tokens=3200,
        timeout=180,
    )
    return _split_round(raw, speakers)


def _split_round(raw: str, speakers: list[Sage]) -> list[tuple[Sage, str]]:
    names = {sage.name: sage for sage in speakers}
    current: str | None = None
    buckets: dict[str, list[str]] = {sage.name: [] for sage in speakers}
    for line in raw.splitlines():
        head = line.strip().strip("#*> ").strip("：:").strip("【】")
        if head in names:
            current = head
            continue
        if current:
            buckets[current].append(line)
    lines = [(sage, "\n".join(buckets[sage.name]).strip()) for sage in speakers]
    lines = [(sage, text) for sage, text in lines if text]
    if lines:
        return lines
    return [(speakers[0], raw.strip())]


def converse(
    query: str,
    speakers: list[Sage],
    limit: int = 8,
    earlier: list[tuple[str, str]] | None = None,
) -> tuple[list[tuple[Sage, str]], list[Hit]]:
    query = query.strip()
    if not query:
        raise AskError("问题是空的。")
    hits = gather(query, limit)
    said = list(earlier or [])
    if len(speakers) == 1:
        sage = speakers[0]
        return [(sage, _speak(sage, query, hits, said, index=len(said)))], hits
    lines: list[tuple[Sage, str]] = []
    for index, sage in enumerate(speakers):
        text = _speak(sage, query, hits, said, index=index)
        lines.append((sage, text))
        said.append((sage.name, text))
    return lines, hits


def sit_round(query: str, rng: random.Random | None = None, limit: int = 8):
    if is_greeting(query):
        speakers = [_BY_ID["kongzi"]]
    else:
        speakers = pick_speakers(rng)
    return converse(query, speakers, limit)


def sit_private(query: str, who: str, limit: int = 8):
    return converse(query, [find_sage(who)], limit)


def format_session(title: str, lines: list[tuple[Sage, str]], hits: list[Hit]) -> str:
    parts = [title]
    for sage, text in lines:
        parts.append(f"\n{sage.name}\n{text}")
    seen: list[str] = []
    for hit in hits:
        line = _source_line(hit)
        if line not in seen:
            seen.append(line)
    if seen:
        parts.append("\n检索依据：\n" + "\n".join(seen))
    return "\n".join(parts).strip()


def main_round() -> None:
    parser = argparse.ArgumentParser(description="先贤围坐：孔子必说，其余随机")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()
    lines, hits = sit_round(args.query, limit=args.limit)
    names = "、".join(sage.name for sage, _text in lines)
    print(format_session(f"【围坐】{names}", lines, hits))


def main_talk() -> None:
    parser = argparse.ArgumentParser(description="与一位先贤私聊")
    parser.add_argument("who", help="姓名、字或 id，例如 子路")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()
    lines, hits = sit_private(args.query, args.who, args.limit)
    print(format_session(f"【私聊】{lines[0][0].name}", lines, hits))
