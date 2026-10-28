"""混合检索：原句用全文短语和包含匹配，白话提问用向量，再按章号把注疏补上。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from rag.db import connect
from rag.embed import embed_texts

RRF_K = 60
LAYER_RANK = {"原文": 0, "注疏": 1, "礼": 2, "史传": 3}


@dataclass
class Hit:
    id: str
    content: str
    book: str
    layer: str
    pian: str
    zhang: str
    anchor: str
    part: int
    source: str
    score: float = 0.0


def _rrf(rankings: list[tuple[list[str], float]]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ids, weight in rankings:
        for rank, doc_id in enumerate(ids):
            scores[doc_id] = scores.get(doc_id, 0.0) + weight / (RRF_K + rank + 1)
    return scores


def _rows_to_hits(rows: list[tuple], scores: dict[str, float]) -> list[Hit]:
    hits = []
    for row in rows:
        hit = Hit(*row)
        hit.score = scores.get(hit.id, 0.0)
        hits.append(hit)
    return hits


def search(query: str, limit: int = 8, layers: list[str] | None = None) -> list[Hit]:
    query = query.strip()
    if not query:
        return []
    layer_filter = layers or []
    vector = embed_texts([query])[0]
    vector_text = "[" + ",".join(f"{value:.7f}" for value in vector) + "]"

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM documents
                WHERE (%(layers)s::text[] = '{}'::text[] OR layer = ANY(%(layers)s))
                  AND fts @@ phraseto_tsquery('simple', %(query)s)
                LIMIT 30
                """,
                {"query": query, "layers": layer_filter},
            )
            phrase_ids = [row[0] for row in cur.fetchall()]

            like = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
            cur.execute(
                """
                SELECT id FROM documents
                WHERE (%(layers)s::text[] = '{}'::text[] OR layer = ANY(%(layers)s))
                  AND body LIKE %(like)s ESCAPE '\\'
                LIMIT 30
                """,
                {"like": like, "layers": layer_filter},
            )
            like_ids = [row[0] for row in cur.fetchall()]

            cur.execute(
                """
                SELECT id FROM documents
                WHERE (%(layers)s::text[] = '{}'::text[] OR layer = ANY(%(layers)s))
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> %(vector)s::vector
                LIMIT 30
                """,
                {"vector": vector_text, "layers": layer_filter},
            )
            vector_ids = [row[0] for row in cur.fetchall()]

            scores = _rrf(
                [
                    (phrase_ids, 1.0),
                    (like_ids, 0.8),
                    (vector_ids, 0.5),
                ]
            )
            ranked_ids = [doc_id for doc_id, _score in sorted(scores.items(), key=lambda item: -item[1])]
            ranked_ids = ranked_ids[:15]

            cur.execute(
                """
                SELECT zhang FROM documents
                WHERE id = ANY(%(ids)s) AND zhang <> '' AND layer = '原文'
                """,
                {"ids": like_ids + phrase_ids},
            )
            exact_zhang = sorted({row[0] for row in cur.fetchall()})

            extra_ids: list[str] = []
            if exact_zhang:
                cur.execute(
                    """
                    SELECT id FROM documents
                    WHERE zhang = ANY(%(zhang)s)
                      AND (%(layers)s::text[] = '{}'::text[] OR layer = ANY(%(layers)s))
                    ORDER BY layer, book, part
                    LIMIT 40
                    """,
                    {"zhang": exact_zhang, "layers": layer_filter},
                )
                extra_ids = [row[0] for row in cur.fetchall()]

            wanted = list(dict.fromkeys(ranked_ids + extra_ids))
            cur.execute(
                """
                SELECT id, content, book, layer, pian, zhang, anchor, part, source
                FROM documents
                WHERE id = ANY(%(ids)s)
                """,
                {"ids": wanted},
            )
            rows = cur.fetchall()

    hits = _rows_to_hits(rows, scores)
    exact = set(exact_zhang)
    normalized = "".join(query.split())
    for hit in hits:
        if normalized and normalized in hit.content:
            hit.score += 1.2
        if hit.zhang and hit.zhang in exact:
            hit.score += 0.6
        if hit.layer == "原文":
            hit.score += 0.3
        elif hit.layer == "注疏" and hit.zhang in exact:
            hit.score += 0.2

    hits.sort(key=lambda hit: (-hit.score, LAYER_RANK.get(hit.layer, 9), hit.zhang, hit.book, hit.part))

    picked: list[Hit] = []
    per_book: dict[str, int] = {}
    for hit in hits:
        if per_book.get(hit.book, 0) >= 2:
            continue
        picked.append(hit)
        per_book[hit.book] = per_book.get(hit.book, 0) + 1
        if len(picked) >= limit:
            break
    return picked


def format_hits(hits: list[Hit]) -> str:
    blocks = []
    for index, hit in enumerate(hits, start=1):
        where = hit.pian
        if hit.zhang:
            where = f"{where} · {hit.zhang}" if where else hit.zhang
        preview = hit.content.strip()
        if len(preview) > 280:
            preview = preview[:280] + "…"
        blocks.append(f"{index}. {hit.layer} 《{hit.book}》{where}  ({hit.score:.3f})\n{preview}")
    return "\n\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description="检索已入库的典籍")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--layers", default="", help="逗号分隔，例如 原文,注疏")
    args = parser.parse_args()
    layers = [item.strip() for item in args.layers.split(",") if item.strip()]
    hits = search(args.query, args.limit, layers or None)
    print(format_hits(hits) or "没有命中")


if __name__ == "__main__":
    main()
