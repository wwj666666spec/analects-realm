"""问答代理：先检索原文、注疏、礼、史传，再按治学、修心或修身回答。"""

from rag.llm import complete
from rag.prompts import MODE_LAYERS, reply_language, system_prompt
from rag.search import Hit, search

CONTEXT_CHARS = 900


def cite(hit: Hit) -> str:
    where = hit.pian
    if hit.zhang:
        where = f"{where} · {hit.zhang}" if where else hit.zhang
    return f"{hit.layer} 《{hit.book}》{where}".strip()


def format_context(hits: list[Hit]) -> str:
    blocks = []
    for index, hit in enumerate(hits, start=1):
        body = hit.content.strip()
        if len(body) > CONTEXT_CHARS:
            body = body[:CONTEXT_CHARS] + "…"
        blocks.append(f"【{index}】{cite(hit)}\n{body}")
    return "\n\n".join(blocks)


class QaAgent:
    name = "问答"

    def run(self, query: str, mode: str, limit: int = 6, lang: str = "zh") -> tuple[str, list[Hit]]:
        hits = search(query, limit, MODE_LAYERS[mode])
        context = format_context(hits) or "（没有检索到材料）"
        user = (
            f"当前模式：{mode}\n\n"
            f"用户问题：\n{query}\n\n"
            f"知识库检索内容：\n{context}\n\n"
            "请按当前模式回答。出处以检索内容中的《书名》篇 · 章为准。"
        )
        extra = reply_language(lang)
        if extra:
            user += "\n\nWrite the answer in English."
        answer = complete(
            [
                {"role": "system", "content": system_prompt(mode, lang)},
                {"role": "user", "content": user},
            ]
        )
        return answer, hits
