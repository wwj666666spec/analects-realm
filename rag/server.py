"""给前端用的薄接口。检索、问答和先贤仍走现有函数。"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

from rag.ask import ask, ask_stream
from rag.auth import login_user, logout_user, register_user, user_from_token
from rag.books import catalog, flat_books, outline, section_text
from rag.config import MEDIA_ROOT
from rag.llm import AskError
from rag.presence import (
    build_persona,
    clone_user_voice,
    generate_figure,
    generate_script,
    generate_video,
    list_voices,
    preview_voice,
    save_upload,
    start_video_job,
    video_job,
)
from rag.sage import (
    MAX_SPEAKERS,
    MIN_SPEAKERS,
    SAGES,
    SAGES_DIR,
    converse,
    find_sage,
    is_greeting,
    pick_speakers,
)
from rag.search import Hit, search

app = FastAPI(title="论语")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class QueryBody(BaseModel):
    query: str = Field(max_length=2000)


class AskBody(QueryBody):
    mode: str = "治学"
    lang: str = "zh"


class RoundBody(QueryBody):
    speakers: list[str] = Field(default_factory=list, max_length=5)


class EarlierLine(BaseModel):
    name: str = Field(max_length=40)
    text: str = Field(max_length=4000)


class TalkBody(QueryBody):
    who: str = Field(max_length=40)
    earlier: list[EarlierLine] = Field(default_factory=list, max_length=8)


class AuthBody(BaseModel):
    username: str = Field(max_length=40)
    password: str = Field(max_length=64)


class PersonaBody(BaseModel):
    answers: list[dict] = Field(default_factory=list)
    score: dict[str, int] = Field(default_factory=dict)


class FigureBody(BaseModel):
    photo_id: str = Field(max_length=80)
    virtue: str = Field(default="温", max_length=8)
    gender: str = Field(default="", max_length=12)


class CloneBody(BaseModel):
    audio_id: str = Field(max_length=80)


class VoicePreviewBody(BaseModel):
    text: str = Field(max_length=400)
    voice: str = Field(default="longxiang", max_length=80)


class ScriptBody(BaseModel):
    persona: dict = Field(default_factory=dict)


class VideoBody(BaseModel):
    text: str = Field(max_length=800)
    voice: str = Field(default="longxiang", max_length=80)
    image_id: str = Field(default="", max_length=80)
    photo_id: str = Field(default="", max_length=80)


def _brief(sage_id: str) -> str:
    raw = (SAGES_DIR / sage_id / "SKILL.md").read_text(encoding="utf-8")
    description = ""
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        front = raw[3:end]
        for line in front.splitlines():
            if line.startswith("description:"):
                description = line.split(":", 1)[1].strip()
    marker = "发言。"
    if marker in description:
        return description.split(marker, 1)[1].strip()
    return description


def _card(sage) -> dict[str, str]:
    return {"id": sage.id, "name": sage.name, "line": _brief(sage.id)}


def _excerpt(hit: Hit) -> str:
    text = hit.content.strip()
    if "\n" in text:
        text = text.split("\n", 1)[1].strip()
    if len(text) > 420:
        text = text[:420] + "…"
    return text


def _sources(hits: list[Hit]) -> list[dict[str, str]]:
    seen: list[str] = []
    items: list[dict[str, str]] = []
    for hit in hits:
        label = f"{hit.layer} 《{hit.book}》{hit.pian}".strip()
        if label in seen:
            continue
        seen.append(label)
        items.append(
            {
                "label": label,
                "layer": hit.layer,
                "book": hit.book,
                "pian": hit.pian,
                "excerpt": _excerpt(hit),
            }
        )
    return items


def _turns(lines) -> list[dict[str, str]]:
    return [{"id": sage.id, "name": sage.name, "text": text} for sage, text in lines]


def _guard(exc: AskError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


def _round_speakers(query: str, tokens: list[str]):
    if is_greeting(query):
        return [find_sage("孔子")]
    if not tokens:
        return pick_speakers()
    chosen = []
    seen: set[str] = set()
    for token in tokens:
        sage = find_sage(token)
        if sage.id == "kongzi" or sage.id in seen:
            continue
        seen.add(sage.id)
        chosen.append(sage)
    total = 1 + len(chosen)
    if total < MIN_SPEAKERS or total > MAX_SPEAKERS:
        raise AskError("围坐人数要在四到五人之间，且孔子在座。")
    return [find_sage("孔子"), *chosen]


COOKIE = "lunyu_session"


def _set_session(response: Response, token: str) -> None:
    response.set_cookie(
        COOKIE,
        token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 14,
        path="/",
    )


@app.get("/api/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.get("/api/me")
def me_api(request: Request) -> dict[str, str]:
    name = user_from_token(request.cookies.get(COOKIE, ""))
    if not name:
        raise HTTPException(status_code=401, detail="还没有登录。")
    return {"username": name}


@app.post("/api/register")
def register_api(body: AuthBody, response: Response) -> dict[str, str]:
    try:
        token = register_user(body.username, body.password)
    except AskError as exc:
        raise _guard(exc) from exc
    _set_session(response, token)
    return {"username": body.username.strip()}


@app.post("/api/login")
def login_api(body: AuthBody, response: Response) -> dict[str, str]:
    try:
        token = login_user(body.username, body.password)
    except AskError as exc:
        raise _guard(exc) from exc
    _set_session(response, token)
    return {"username": body.username.strip()}


@app.post("/api/logout")
def logout_api(request: Request, response: Response) -> dict[str, bool]:
    logout_user(request.cookies.get(COOKIE, ""))
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@app.get("/api/books")
def books_api() -> dict:
    categories = catalog()
    return {"categories": categories, "books": flat_books()}


@app.get("/api/book")
def book_api(name: str = "") -> dict:
    try:
        return outline(name)
    except AskError as exc:
        raise _guard(exc) from exc


@app.get("/api/book/text")
def book_text_api(name: str = "", index: int = 0) -> dict:
    try:
        return section_text(name, index)
    except AskError as exc:
        raise _guard(exc) from exc


@app.get("/api/sages")
def sages() -> dict[str, list[dict[str, str]]]:
    return {"sages": [_card(sage) for sage in SAGES]}


@app.get("/api/search")
def search_api(q: str = "", limit: int = 8) -> dict[str, list[dict[str, str]]]:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="要检索的句子是空的。")
    limit = min(max(limit, 1), 12)
    try:
        hits = search(query, limit, None)
    except AskError as exc:
        raise _guard(exc) from exc
    return {"hits": _sources(hits)}


@app.post("/api/ask")
def ask_api(body: AskBody) -> dict:
    try:
        agent, answer, hits = ask(body.query, body.mode, lang=body.lang)
    except AskError as exc:
        raise _guard(exc) from exc
    return {
        "agent": agent,
        "mode": body.mode,
        "answer": answer,
        "sources": _sources(hits),
    }


@app.post("/api/ask/stream")
def ask_stream_api(body: AskBody) -> StreamingResponse:
    def events():
        try:
            for kind, payload in ask_stream(body.query, body.mode, lang=body.lang):
                if kind == "meta":
                    hits = payload.get("hits") or []
                    data = {
                        "type": "meta",
                        "agent": payload.get("agent"),
                        "mode": payload.get("mode") or body.mode,
                        "sources": _sources(hits),
                    }
                elif kind == "delta":
                    data = {"type": "delta", "text": payload}
                else:
                    data = {"type": "done"}
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except AskError as exc:
            data = {"type": "error", "detail": str(exc)}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/seat")
def seat_api(body: QueryBody) -> dict[str, list[dict[str, str]]]:
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="问题是空的。")
    try:
        speakers = _round_speakers(query, [])
    except AskError as exc:
        raise _guard(exc) from exc
    return {"speakers": [_card(sage) for sage in speakers]}


@app.post("/api/round")
def round_api(body: RoundBody) -> dict:
    try:
        speakers = _round_speakers(body.query, body.speakers)
        lines, hits = converse(body.query, speakers)
    except AskError as exc:
        raise _guard(exc) from exc
    return {"kind": "round", "turns": _turns(lines), "sources": _sources(hits)}


@app.post("/api/talk")
def talk_api(body: TalkBody) -> dict:
    try:
        earlier = [(item.name, item.text) for item in body.earlier]
        lines, hits = converse(body.query, [find_sage(body.who)], earlier=earlier)
    except AskError as exc:
        raise _guard(exc) from exc
    return {"kind": "talk", "turns": _turns(lines), "sources": _sources(hits)}


@app.get("/api/presence/voices")
def presence_voices() -> dict:
    return {"voices": list_voices()}


@app.post("/api/presence/persona")
def presence_persona(body: PersonaBody) -> dict:
    try:
        return {"persona": build_persona(body.answers, body.score or None)}
    except AskError as exc:
        raise _guard(exc) from exc


@app.post("/api/presence/upload/photo")
async def presence_upload_photo(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    try:
        return save_upload("photo", file.filename or "photo.jpg", data)
    except AskError as exc:
        raise _guard(exc) from exc


@app.post("/api/presence/upload/audio")
async def presence_upload_audio(file: UploadFile = File(...)) -> dict:
    data = await file.read()
    try:
        return save_upload("audio", file.filename or "voice.mp3", data)
    except AskError as exc:
        raise _guard(exc) from exc


@app.post("/api/presence/figure")
def presence_figure(body: FigureBody) -> dict:
    try:
        return generate_figure(body.photo_id, body.virtue, body.gender)
    except AskError as exc:
        raise _guard(exc) from exc


@app.post("/api/presence/voice/clone")
def presence_clone(body: CloneBody) -> dict:
    try:
        return clone_user_voice(body.audio_id)
    except AskError as exc:
        raise _guard(exc) from exc


@app.post("/api/presence/voice/preview")
def presence_voice_preview(body: VoicePreviewBody) -> dict:
    try:
        return preview_voice(body.text, body.voice)
    except AskError as exc:
        raise _guard(exc) from exc


@app.post("/api/presence/script")
def presence_script(body: ScriptBody) -> dict:
    try:
        return {"text": generate_script(body.persona)}
    except AskError as exc:
        raise _guard(exc) from exc


@app.post("/api/presence/video")
def presence_video(body: VideoBody) -> dict:
    try:
        job_id = start_video_job(
            text=body.text,
            voice=body.voice,
            image_id=body.image_id or None,
            photo_id=body.photo_id or None,
        )
        return {"job_id": job_id, "status": "running"}
    except AskError as exc:
        raise _guard(exc) from exc


@app.get("/api/presence/video/{job_id}")
def presence_video_status(job_id: str) -> dict:
    job = video_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="没有找到这个视频任务。")
    return job


def _spa() -> FileResponse:
    # 避免浏览器缓存旧版 index.html，导致界面改动“看不见”
    return FileResponse(
        WEB_DIR / "index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.get("/")
def home_page() -> FileResponse:
    return _spa()


@app.get("/ask")
def ask_page() -> FileResponse:
    return _spa()


@app.get("/sages")
def sages_page() -> FileResponse:
    return _spa()


@app.get("/library")
def library_page() -> FileResponse:
    return _spa()


@app.get("/book")
def book_page() -> FileResponse:
    return _spa()


@app.get("/presence")
def presence_page() -> FileResponse:
    return _spa()


@app.get("/me")
def me_page() -> FileResponse:
    return _spa()


@app.get("/login")
def login_page() -> FileResponse:
    return _spa()


@app.get("/register")
def register_page() -> FileResponse:
    return _spa()


app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8787)


if __name__ == "__main__":
    main()
