"""风骨创作：人设、古风形象、音色、诵读短视频。"""

from __future__ import annotations

import json
import shutil
import threading
import uuid
from pathlib import Path
from typing import Any, Callable

from rag.config import FIGURE_DIR, UPLOAD_DIR
from rag.cosyvoice_api import VOICE_CATALOG, clone_voice, synthesize_speech
from rag.liveportrait_api import LivePortraitAPI
from rag.llm import AskError, complete
from rag.media_upload import upload_public
from rag.style_repaint import normalize_gender, repaint_ancient

WUDE = ("温", "良", "恭", "俭", "让")
PERSONA_SEED = {
    "温": {
        "name": "温润守正之士",
        "motto": "君子欲讷于言而敏于行。",
        "mottoSrc": "《论语·里仁》4.24",
        "tags": ["不急不躁", "体谅他人", "内省自持"],
        "line": "沉静自省，待人温和，遇事先看自己那一处。",
    },
    "良": {
        "name": "良善笃行之士",
        "motto": "君子耻其言而过其行。",
        "mottoSrc": "《论语·宪问》14.27",
        "tags": ["言行相顾", "守信践诺", "就事论事"],
        "line": "诚恳笃实，重承诺与行动，不愿把话说过头。",
    },
    "恭": {
        "name": "恭谨端方之士",
        "motto": "居处恭，执事敬，与人忠。",
        "mottoSrc": "《论语·子路》13.19",
        "tags": ["敬事而信", "守时有节", "克己有度"],
        "line": "持重有度，敬事而信，习惯把分寸放在前面。",
    },
    "俭": {
        "name": "俭素自持之士",
        "motto": "饭疏食饮水，曲肱而枕之，乐亦在其中矣。",
        "mottoSrc": "《论语·述而》7.16",
        "tags": ["取用有度", "不慕浮华", "专注本业"],
        "line": "简素自守，不慕浮华，把心思放在真正要紧的事上。",
    },
    "让": {
        "name": "谦让有容之士",
        "motto": "躬自厚而薄责于人，则远怨矣。",
        "mottoSrc": "《论语·卫灵公》15.15",
        "tags": ["先听后言", "不争其功", "推己及人"],
        "line": "谦和有容，先听后言，善于给别人留余地。",
    },
}


def save_upload(kind: str, filename: str, data: bytes) -> dict[str, str]:
    suffix = Path(filename).suffix.lower() or ".bin"
    if kind == "photo" and suffix not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        raise AskError("照片请使用 JPG / PNG / WEBP。")
    if kind == "audio" and suffix not in {".mp3", ".wav", ".m4a"}:
        raise AskError("音频请使用 MP3 / WAV / M4A。")
    if len(data) > 12 * 1024 * 1024:
        raise AskError("文件过大，请控制在 12MB 以内。")
    token = uuid.uuid4().hex
    path = UPLOAD_DIR / f"{kind}_{token}{suffix}"
    path.write_bytes(data)
    return {"id": token, "name": Path(filename).name, "path": str(path), "kind": kind}


def _upload_path(token: str, kind: str) -> Path:
    matches = list(UPLOAD_DIR.glob(f"{kind}_{token}.*"))
    if not matches:
        # also allow figure tokens stored under FIGURE_DIR via special kind
        if kind == "figure":
            matches = list(FIGURE_DIR.glob(f"*{token}*"))
        if not matches:
            raise AskError("没有找到这份上传文件。")
    return matches[0]


def build_persona(answers: list[dict[str, Any]], score: dict[str, int] | None = None) -> dict[str, Any]:
    if score is None:
        score = {key: 0 for key in WUDE}
        for item in answers:
            weights = item.get("w") or {}
            for key, value in weights.items():
                if key in score:
                    score[key] += int(value)
    top = sorted(WUDE, key=lambda key: score.get(key, 0), reverse=True)
    seed = PERSONA_SEED[top[0]]
    second = PERSONA_SEED[top[1]]
    summary = (
        f"主德「{top[0]}」，次德「{top[1]}」。"
        f"基础画像：{seed['name']}。{seed['line']}"
    )
    prompt = (
        "你是儒家五德画像助手。根据用户测试得分与作答，生成一份专属人设卡。"
        "只输出 JSON，不要 Markdown。字段："
        "name, motto, mottoSrc, line, tags(数组，3到5个), analysis(80到120字)。"
        "座右铭须出自《论语》并写清篇名。"
        f"\n五德得分：{json.dumps(score, ensure_ascii=False)}"
        f"\n主德参考：{json.dumps(seed, ensure_ascii=False)}"
        f"\n次德参考：{json.dumps(second, ensure_ascii=False)}"
        f"\n作答摘要：{json.dumps(answers, ensure_ascii=False)[:1800]}"
    )
    try:
        raw = complete(
            [{"role": "system", "content": prompt}, {"role": "user", "content": "请生成人设卡。"}],
            temperature=0.6,
            max_tokens=700,
        )
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text)
    except Exception:
        data = {
            "name": seed["name"],
            "motto": seed["motto"],
            "mottoSrc": seed["mottoSrc"],
            "line": seed["line"],
            "tags": seed["tags"],
            "analysis": summary,
        }
    tags = data.get("tags") or seed["tags"]
    if isinstance(tags, str):
        tags = [tags]
    return {
        "name": str(data.get("name") or seed["name"])[:24],
        "motto": str(data.get("motto") or seed["motto"]),
        "mottoSrc": str(data.get("mottoSrc") or seed["mottoSrc"]),
        "line": str(data.get("line") or seed["line"]),
        "tags": [str(tag)[:16] for tag in tags][:5],
        "analysis": str(data.get("analysis") or summary),
        "score": score,
        "top": top,
        "max": max(score.values()) if score else 1,
        "summary": summary,
    }


def generate_figure(photo_id: str, virtue: str = "温", gender: str = "") -> dict[str, str]:
    photo = _upload_path(photo_id, "photo")
    figure = repaint_ancient(photo, virtue=virtue or "温", gender=gender or "")
    token = uuid.uuid4().hex
    saved = FIGURE_DIR / f"figure_{token}{figure.suffix}"
    shutil.copyfile(figure, saved)
    return {
        "id": token,
        "path": str(saved),
        "url": f"/media/figures/{saved.name}",
        "virtue": virtue or "温",
        "gender": normalize_gender(gender) or "",
    }


def clone_user_voice(audio_id: str) -> dict[str, str]:
    audio = _upload_path(audio_id, "audio")
    voice_id = clone_voice(audio)
    return {"voice_id": voice_id, "label": "我的克隆声线"}


def preview_voice(text: str, voice: str) -> dict[str, str]:
    path = synthesize_speech(text, voice)
    return {"url": f"/media/audio/{path.name}", "path": str(path)}


def generate_script(persona: dict[str, Any]) -> str:
    name = persona.get("name") or "研习者"
    line = persona.get("line") or ""
    motto = persona.get("motto") or ""
    analysis = persona.get("analysis") or ""
    prompt = (
        "请根据人物设定，写一段适合个人诵读短视频的旁白。"
        "语气克制、有文化感，不要标题和问候，字数 45 到 60 字（数字人单段约 20 秒）。"
        f"\n人设名号：{name}\n画像：{line}\n座右铭：{motto}\n分析：{analysis}"
    )
    return complete(
        [{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=400,
    ).strip()


def generate_video(
    *,
    text: str,
    voice: str,
    image_id: str | None = None,
    photo_id: str | None = None,
    progress=None,
) -> dict[str, str]:
    def note(stage: str, message: str) -> None:
        if progress:
            progress(stage, message)

    text = text.strip()
    if not text:
        raise AskError("请先填写诵读文字。")
    if len(text) > 800:
        raise AskError("诵读文字请控制在 800 字以内。")

    if image_id:
        image_path = _upload_path(image_id, "figure")
    elif photo_id:
        image_path = _upload_path(photo_id, "photo")
    else:
        raise AskError("请先上传照片或生成古风形象。")

    # 万相数字人 wan2.2-s2v 要求音频 < 20 秒；中文约 3.5 字/秒
    wan_limit = 65
    wan_text = text if len(text) <= wan_limit else text[:wan_limit].rstrip("，,。；;、 ") + "。"
    if wan_text != text:
        note("tts", f"数字人单段不超过约 20 秒，已截取前 {wan_limit} 字合成语音…")
    else:
        note("tts", "正在合成诵读语音…")
    audio_path = synthesize_speech(wan_text, voice)
    api = LivePortraitAPI()
    submitted = None
    last_error = None

    # 优先万相数字人（当前账号 LivePortrait/EMO 常返回 Model not exist）
    try:
        note("upload", "正在上传形象与音频…")
        detect_image_url = upload_public(image_path, model="wan2.2-s2v-detect")
        note("detect", "正在做人脸检测…")
        detect = api.detect_wan_s2v(detect_image_url)
        output = detect.get("output") or {}
        if not output.get("check_pass", False):
            message = output.get("message") or "请换一张脸部清晰、无遮挡的正面半身照"
            raise AskError(f"人脸检测未通过：{message}")
        image_url = upload_public(image_path, model="wan2.2-s2v")
        audio_url = upload_public(audio_path, model="wan2.2-s2v")
        note("submit", "正在提交万相数字人任务…")
        submitted = api.generate_wan_s2v(image_url, audio_url, resolution="480P", style="speech")
    except AskError as exc:
        last_error = exc

    # 回退 LivePortrait
    if not submitted or not submitted.get("output", {}).get("task_id"):
        try:
            note("upload", "改用灵动人像接口，正在上传…")
            detect_image_url = upload_public(image_path, model="liveportrait-detect")
            note("detect", "正在做人脸检测…")
            detect = api.detect_face(detect_image_url)
            if not detect.get("output", {}).get("pass", False):
                message = detect.get("output", {}).get("message") or "请换一张脸部清晰的正面照片"
                raise AskError(f"人脸检测未通过：{message}")
            image_url = upload_public(image_path, model="liveportrait")
            audio_url = upload_public(audio_path, model="liveportrait")
            note("submit", "正在提交数字人任务…")
            submitted = api.generate_video(
                image_url,
                audio_url,
                template_id="calm",
                eye_move_freq=0.4,
                mouth_move_strength=0.85,
                head_move_strength=0.45,
            )
        except AskError as exc:
            last_error = last_error or exc

    # 再回退 EMO
    if not submitted or not submitted.get("output", {}).get("task_id"):
        try:
            note("upload", "改用悦动人像接口，正在上传…")
            detect_url = upload_public(image_path, model="emo-detect-v1")
            note("detect", "正在检测人像动作区域…")
            detect = api.detect_emo(detect_url, ratio="3:4")
            output = detect.get("output") or {}
            if not output.get("check_pass", False):
                raise AskError(output.get("message") or "人像检测未通过，请换一张正面半身照")
            face_bbox = output.get("face_bbox")
            ext_bbox = output.get("ext_bbox")
            if not face_bbox or not ext_bbox:
                raise AskError("人像检测没有返回动作区域。")
            image_url = upload_public(image_path, model="emo-v1")
            audio_url = upload_public(audio_path, model="emo-v1")
            note("submit", "正在提交悦动人像任务…")
            submitted = api.generate_emo_video(
                image_url,
                audio_url,
                face_bbox,
                ext_bbox,
                style_level="calm",
            )
        except AskError as exc:
            raise last_error or exc from exc

    task_id = submitted.get("output", {}).get("task_id")
    if not task_id:
        raise last_error or AskError(f"未能提交视频任务：{submitted}")
    note("render", "口型与动作生成中，通常需要 2～6 分钟，请稍候…")
    result = api.wait_for_task(task_id, polling_interval=5, max_attempts=120)
    if result.get("output", {}).get("task_status") != "SUCCEEDED":
        message = result.get("output", {}).get("message") or result.get("output", {}).get("error_message") or result
        raise AskError(f"视频生成失败：{message}")
    video_url = result.get("output", {}).get("results", {}).get("video_url")
    if not video_url:
        raise AskError(f"视频生成成功但没有地址：{result}")
    note("done", "成片已生成")
    return {
        "task_id": task_id,
        "video_url": video_url,
        "audio_url": f"/media/audio/{audio_path.name}",
        "image_url": f"/media/{'figures' if image_id else 'uploads'}/{image_path.name}",
    }


_VIDEO_JOBS: dict[str, dict[str, Any]] = {}


def start_video_job(
    *,
    text: str,
    voice: str,
    image_id: str | None = None,
    photo_id: str | None = None,
) -> str:
    job_id = uuid.uuid4().hex
    _VIDEO_JOBS[job_id] = {
        "job_id": job_id,
        "status": "running",
        "stage": "queued",
        "message": "任务已创建",
    }

    def _run() -> None:
        def progress(stage: str, message: str) -> None:
            job = _VIDEO_JOBS.get(job_id) or {}
            job.update({"status": "running", "stage": stage, "message": message})
            _VIDEO_JOBS[job_id] = job

        try:
            result = generate_video(
                text=text,
                voice=voice,
                image_id=image_id,
                photo_id=photo_id,
                progress=progress,
            )
            _VIDEO_JOBS[job_id] = {
                "job_id": job_id,
                "status": "succeeded",
                "stage": "done",
                "message": "成片已生成",
                **result,
            }
        except Exception as exc:  # noqa: BLE001
            _VIDEO_JOBS[job_id] = {
                "job_id": job_id,
                "status": "failed",
                "stage": "error",
                "message": str(exc),
                "detail": str(exc),
            }

    threading.Thread(target=_run, daemon=True).start()
    return job_id


def video_job(job_id: str) -> dict[str, Any] | None:
    return _VIDEO_JOBS.get(job_id)


def list_voices() -> list[dict[str, str]]:
    voices = [
        {
            "id": item["id"],
            "name": item["name"],
            "desc": item["desc"],
            "gender": item["gender"],
            "backend": item["backend"],
        }
        for item in VOICE_CATALOG
    ]
    voices.append(
        {"id": "mine", "name": "我的克隆声线", "desc": "上传音频后生成", "gender": "clone", "backend": ""}
    )
    return voices
