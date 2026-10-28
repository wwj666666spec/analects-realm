"""问答、先贤、风骨共用的 Token Factory 调用。模型是 NVIDIA Nemotron。"""

from __future__ import annotations

import json
from collections.abc import Iterator

import httpx

from rag.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL


class AskError(RuntimeError):
    pass


def _auth_headers() -> dict[str, str]:
    if not NEBIUS_API_KEY.strip():
        raise AskError("rag/.env 里的 NEBIUS_API_KEY 是空的。")
    return {"Authorization": f"Bearer {NEBIUS_API_KEY}"}


def _chat_url() -> str:
    return f"{NEBIUS_BASE_URL}/chat/completions"


def _request_body(
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int | None,
    stream: bool,
    model: str | None,
) -> dict:
    body: dict = {
        "model": model or NEBIUS_MODEL,
        "messages": messages,
        "temperature": temperature,
        "stream": stream,
        # 关掉思考过程，否则正文会空，额度也花在推理上。
        "chat_template_kwargs": {"enable_thinking": False},
    }
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    return body


def _redact(text: str) -> str:
    if NEBIUS_API_KEY:
        return text.replace(NEBIUS_API_KEY, "***")
    return text


def _message_text(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    reasoning = message.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()
    raise AskError("Token Factory 没有返回回答。")


def complete(
    messages: list[dict[str, str]],
    timeout: float = 120,
    temperature: float = 0.3,
    max_tokens: int | None = None,
    model: str | None = None,
) -> str:
    body = _request_body(messages, temperature, max_tokens, stream=False, model=model)
    headers = _auth_headers()
    try:
        response = httpx.post(_chat_url(), headers=headers, json=body, timeout=timeout)
    except httpx.ConnectError:
        response = httpx.post(
            _chat_url(), headers=headers, json=body, timeout=timeout, trust_env=False
        )
    if response.status_code >= 400:
        detail = _redact(response.text[:300])
        raise AskError(f"Token Factory 返回 {response.status_code}：{detail}")
    payload = response.json()
    try:
        return _message_text(payload["choices"][0]["message"])
    except (KeyError, IndexError, AttributeError) as exc:
        raise AskError(f"Token Factory 没有返回回答：{_redact(str(payload)[:300])}") from exc


def complete_stream(
    messages: list[dict[str, str]],
    timeout: float = 120,
    temperature: float = 0.3,
    max_tokens: int | None = None,
    model: str | None = None,
) -> Iterator[str]:
    body = _request_body(messages, temperature, max_tokens, stream=True, model=model)
    headers = _auth_headers()
    try:
        response = httpx.stream(
            "POST", _chat_url(), headers=headers, json=body, timeout=timeout
        )
    except httpx.ConnectError:
        response = httpx.stream(
            "POST",
            _chat_url(),
            headers=headers,
            json=body,
            timeout=timeout,
            trust_env=False,
        )
    with response as stream:
        if stream.status_code >= 400:
            detail = _redact(stream.read().decode("utf-8", errors="replace")[:300])
            raise AskError(f"Token Factory 返回 {stream.status_code}：{detail}")
        for line in stream.iter_lines():
            if not line:
                continue
            if line.startswith("data:"):
                line = line[5:].strip()
            if not line or line == "[DONE]":
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                delta = payload["choices"][0].get("delta") or {}
                piece = delta.get("content") or ""
            except (KeyError, IndexError, AttributeError, TypeError):
                continue
            if piece:
                yield piece
