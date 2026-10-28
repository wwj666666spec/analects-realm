"""把切好的典籍写入 Postgres，并用 Ollama 生成向量。"""

from __future__ import annotations

import argparse

from rag.chunk import Chunk, build_chunks, summarize
from rag.config import DATA_DIR, EMBED_MODEL
from rag.db import connect, ensure_schema
from rag.embed import embed_texts


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.7f}" for value in values) + "]"


def drop_existing(conn, chunks: list[Chunk]) -> list[Chunk]:
    existing: set[str] = set()
    ids = [chunk.id for chunk in chunks]
    with conn.cursor() as cur:
        for start in range(0, len(ids), 1000):
            cur.execute(
                """
                SELECT id FROM documents
                WHERE id = ANY(%s) AND embedding IS NOT NULL
                """,
                (ids[start : start + 1000],),
            )
            existing.update(row[0] for row in cur.fetchall())
    return [chunk for chunk in chunks if chunk.id not in existing]


def insert_chunks(chunks: list[Chunk], batch_size: int, rebuild: bool) -> None:
    with connect() as conn:
        ensure_schema(conn)
        if rebuild:
            conn.execute("TRUNCATE documents")
            conn.commit()
        else:
            before = len(chunks)
            chunks = drop_existing(conn, chunks)
            print(f"跳过已有向量 {before - len(chunks)} 块，待写入 {len(chunks)} 块", flush=True)
        total = len(chunks)
        if total == 0:
            return
        for start in range(0, total, batch_size):
            batch = chunks[start : start + batch_size]
            vectors = embed_texts([chunk.content for chunk in batch])
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO documents
                        (id, content, book, layer, pian, zhang, anchor, part, source, body, embedding)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        book = EXCLUDED.book,
                        layer = EXCLUDED.layer,
                        pian = EXCLUDED.pian,
                        zhang = EXCLUDED.zhang,
                        anchor = EXCLUDED.anchor,
                        part = EXCLUDED.part,
                        source = EXCLUDED.source,
                        body = EXCLUDED.body,
                        embedding = EXCLUDED.embedding
                    """,
                    [
                        (
                            chunk.id,
                            chunk.content,
                            chunk.book,
                            chunk.layer,
                            chunk.pian,
                            chunk.zhang,
                            chunk.anchor,
                            chunk.part,
                            chunk.source,
                            chunk.content.split("\n", 1)[1] if "\n" in chunk.content else chunk.content,
                            vector_literal(vector),
                        )
                        for chunk, vector in zip(batch, vectors)
                    ],
                )
            conn.commit()
            print(f"已写入 {min(start + len(batch), total)}/{total}", flush=True)


def select_chunks(books: list[str], limit: int) -> list[Chunk]:
    chunks = build_chunks(DATA_DIR)
    if books:
        wanted = set(books)
        chunks = [chunk for chunk in chunks if chunk.book in wanted or chunk.source in wanted]
    if limit:
        chunks = chunks[:limit]
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="把典籍 Markdown 入库")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="只写入前 N 块，用来试跑")
    parser.add_argument("--books", default="", help="按书名或文件名过滤，逗号分隔")
    parser.add_argument("--rebuild", action="store_true", help="清空 documents 后重写")
    args = parser.parse_args()
    books = [item.strip() for item in args.books.split(",") if item.strip()]
    chunks = select_chunks(books, args.limit)
    print(summarize(chunks))
    print(f"嵌入模型 {EMBED_MODEL}，本批 {len(chunks)} 块")
    insert_chunks(chunks, args.batch_size, args.rebuild)


if __name__ == "__main__":
    main()
