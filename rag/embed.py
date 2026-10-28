import httpx

from rag.config import EMBED_DIM, EMBED_MODEL, OLLAMA_URL


class EmbedError(RuntimeError):
    pass


def embed_texts(texts: list[str], timeout: float = 180) -> list[list[float]]:
    if not texts:
        return []
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": texts},
        )
        if response.status_code == 404:
            vectors = []
            for text in texts:
                one = client.post(
                    f"{OLLAMA_URL}/api/embeddings",
                    json={"model": EMBED_MODEL, "prompt": text},
                )
                one.raise_for_status()
                vectors.append(one.json()["embedding"])
            _check_dim(vectors)
            return vectors
        response.raise_for_status()
        vectors = response.json().get("embeddings")
        if not vectors:
            raise EmbedError(f"Ollama 没有返回向量：{response.text[:300]}")
        _check_dim(vectors)
        return vectors


def _check_dim(vectors: list[list[float]]) -> None:
    width = len(vectors[0]) if vectors else 0
    if width != EMBED_DIM:
        raise EmbedError(
            f"模型 {EMBED_MODEL} 的向量是 {width} 维，数据表需要 {EMBED_DIM} 维。"
            "请改用 bge-m3，或同时改 schema.sql 里的 vector 维度。"
        )
