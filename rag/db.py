from pathlib import Path

import psycopg

from rag.config import DATABASE_URL

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect() -> psycopg.Connection:
    return psycopg.connect(DATABASE_URL)


def ensure_schema(conn: psycopg.Connection) -> None:
    script = SCHEMA_PATH.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        for statement in script.split(";"):
            sql = statement.strip()
            if sql:
                cur.execute(sql)
    conn.commit()
