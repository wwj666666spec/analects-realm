"""接谈代理：打招呼、道谢、道别、询问功能。不查库，不引用典籍。"""

from rag.llm import complete
from rag.prompts import chat_prompt


class ChatAgent:
    name = "接谈"

    def run(self, query: str, lang: str = "zh") -> str:
        return complete(
            [
                {"role": "system", "content": chat_prompt(lang)},
                {"role": "user", "content": query},
            ]
        )
