"""入口只负责分发：寒暄交给接谈代理，具体问题交给问答代理。"""

from __future__ import annotations

import argparse
import re

from collections.abc import Iterator

from rag.chat_agent import ChatAgent
from rag.config import NEBIUS_FAST_MODEL
from rag.llm import AskError, complete, complete_stream
from rag.prompts import (
    MODE_LAYERS,
    MODES,
    ROUTE_PROMPT,
    chat_prompt,
    reply_language,
    system_prompt,
)
from rag.qa_agent import QaAgent, format_context
from rag.search import Hit, search

# 整句就是这些意思时，直接交给接谈代理，不再请模型判断。
_CHAT_EXACT = {
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
    "好的",
    "知道了",
    "明白了",
    "嗯",
    "哦",
    "好",
    "再见",
    "拜拜",
    "再会",
    "你是谁",
    "你叫什么",
    "你能做什么",
    "你会什么",
    "怎么用",
    "如何使用",
    "帮助",
    "help",
}

chat_agent = ChatAgent()
qa_agent = QaAgent()


def _core(query: str) -> str:
    text = re.sub(r"[^\w]+", "", query.strip().lower(), flags=re.UNICODE)
    return re.sub(r"[呀啊呢吧哦哟哈嗯啦]+$", "", text)


def choose_agent(query: str):
    """返回接谈或问答。拿不准时交给问答。"""
    if _core(query) in _CHAT_EXACT:
        return chat_agent
    decision = complete(
        [
            {"role": "system", "content": ROUTE_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0,
        max_tokens=8,
        model=NEBIUS_FAST_MODEL,
    )
    if any(token in decision for token in ("不必", "不需要", "不用")):
        return chat_agent
    return qa_agent


def _lang(lang: str) -> str:
    return "en" if (lang or "").strip().lower() == "en" else "zh"


def ask(query: str, mode: str = "治学", limit: int = 6, lang: str = "zh") -> tuple[str, str, list[Hit]]:
    query = query.strip()
    lang = _lang(lang)
    if not query:
        raise AskError("问题是空的。")
    if mode not in MODES:
        raise AskError(f"模式只能是 {'、'.join(MODES)}。")
    agent = choose_agent(query)
    if agent is chat_agent:
        return agent.name, agent.run(query, lang), []
    answer, hits = agent.run(query, mode, limit, lang)
    return agent.name, answer, hits


def ask_stream(query: str, mode: str = "治学", limit: int = 6, lang: str = "zh") -> Iterator[tuple[str, object]]:
    """先产出 meta，再陆续产出 delta 文本片，最后 done。"""
    query = query.strip()
    lang = _lang(lang)
    if not query:
        raise AskError("问题是空的。")
    if mode not in MODES:
        raise AskError(f"模式只能是 {'、'.join(MODES)}。")
    agent = choose_agent(query)
    if agent is chat_agent:
        yield "meta", {"agent": agent.name, "mode": mode, "hits": []}
        for piece in complete_stream(
            [
                {"role": "system", "content": chat_prompt(lang)},
                {"role": "user", "content": query},
            ],
            model=NEBIUS_FAST_MODEL,
        ):
            yield "delta", piece
        yield "done", None
        return
    hits = search(query, limit, MODE_LAYERS[mode])
    context = format_context(hits) or "（没有检索到材料）"
    user = (
        f"当前模式：{mode}\n\n"
        f"用户问题：\n{query}\n\n"
        f"知识库检索内容：\n{context}\n\n"
        "请按当前模式回答。出处以检索内容中的《书名》篇 · 章为准。"
    )
    if reply_language(lang):
        user += "\n\nWrite the answer in English."
    yield "meta", {"agent": qa_agent.name, "mode": mode, "hits": hits}
    for piece in complete_stream(
        [
            {"role": "system", "content": system_prompt(mode, lang)},
            {"role": "user", "content": user},
        ]
    ):
        yield "delta", piece
    yield "done", None


def format_result(agent_name: str, mode: str, answer: str, hits: list[Hit]) -> str:
    if agent_name == chat_agent.name:
        return f"【{agent_name}】\n{answer}"
    sources = "\n".join(
        f"{hit.layer} 《{hit.book}》{hit.pian}".strip() for hit in hits
    )
    body = f"【{agent_name}·{mode}】\n{answer}"
    if sources:
        body += f"\n\n检索依据：\n{sources}"
    return body


def main() -> None:
    parser = argparse.ArgumentParser(description="接谈或问答")
    parser.add_argument("query")
    parser.add_argument("--mode", default="治学", choices=MODES)
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args()
    agent_name, answer, hits = ask(args.query, args.mode, args.limit)
    print(format_result(agent_name, args.mode, answer, hits))


if __name__ == "__main__":
    main()
