"""用户名和密码。密码只存摘要，登录状态放在 Cookie 里。"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets

from rag.db import connect
from rag.llm import AskError

_NAME = re.compile(r"^[\w\u4e00-\u9fff]{2,20}$")
_READY = False


def _ensure() -> None:
    global _READY
    if _READY:
        return
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    token TEXT PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        conn.commit()
    _READY = True


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120_000)
    return f"{salt}${digest.hex()}"


def _check_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120_000).hex()
    return hmac.compare_digest(check, digest)


def _clean_name(username: str) -> str:
    name = username.strip()
    if not _NAME.match(name):
        raise AskError("用户名用 2 到 20 个字，可以是汉字、字母或数字。")
    return name


def _clean_password(password: str) -> str:
    if len(password) < 6 or len(password) > 64:
        raise AskError("密码至少 6 位。")
    return password


def register_user(username: str, password: str) -> str:
    _ensure()
    name = _clean_name(username)
    secret = _clean_password(password)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s", (name,))
            if cur.fetchone():
                raise AskError("这个用户名已经注册过。")
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (name, _hash_password(secret)),
            )
            user_id = cur.fetchone()[0]
            token = secrets.token_urlsafe(32)
            cur.execute(
                "INSERT INTO auth_sessions (token, user_id) VALUES (%s, %s)",
                (token, user_id),
            )
        conn.commit()
    return token


def login_user(username: str, password: str) -> str:
    _ensure()
    name = username.strip()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, password_hash FROM users WHERE username = %s",
                (name,),
            )
            row = cur.fetchone()
            if not row or not _check_password(password, row[1]):
                raise AskError("用户名或密码不对。")
            token = secrets.token_urlsafe(32)
            cur.execute(
                "INSERT INTO auth_sessions (token, user_id) VALUES (%s, %s)",
                (token, row[0]),
            )
        conn.commit()
    return token


def logout_user(token: str) -> None:
    if not token:
        return
    _ensure()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM auth_sessions WHERE token = %s", (token,))
        conn.commit()


def user_from_token(token: str) -> str | None:
    if not token:
        return None
    _ensure()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT users.username
                FROM auth_sessions
                JOIN users ON users.id = auth_sessions.user_id
                WHERE auth_sessions.token = %s
                """,
                (token,),
            )
            row = cur.fetchone()
    return row[0] if row else None
