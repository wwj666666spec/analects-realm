"""CosyVoice：预设音色合成与声音克隆。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from rag.config import AUDIO_DIR, DASHSCOPE_API_KEY
from rag.llm import AskError
from rag.media_upload import upload_public

# 北京地域需 cosyvoice-v2 及以上；系统音色须带对应后缀（如 _v2）
COSYVOICE_MODEL = "cosyvoice-v2"

# 前端 id → 百炼 voice 参数（v2）
VOICE_CATALOG = [
    {"id": "longxiang", "backend": "longjin_v2", "name": "苍古沉雄", "desc": "磁性醇厚，适合沉吟诵读", "gender": "male"},
    {"id": "longshu", "backend": "longshu_v2", "name": "沉稳解说", "desc": "从容平稳，吐字清晰", "gender": "male"},
    {"id": "longxiaocheng", "backend": "longxiaocheng_v2", "name": "明朗通达", "desc": "阳光清朗，气息开阔", "gender": "male"},
    {"id": "longlaotie", "backend": "longlaotie_v2", "name": "刚健铿锵", "desc": "短句有力，骨力较足", "gender": "male"},
    {"id": "longshuo", "backend": "longshuo_v2", "name": "厚实稳重", "desc": "声线饱满，适合庄重朗读", "gender": "male"},
    {"id": "longcheng", "backend": "longcheng_v2", "name": "清朗稳重", "desc": "干净利落，不疾不徐", "gender": "male"},
    {"id": "longxiaochun", "backend": "longxiaochun_v2", "name": "清和冲淡", "desc": "轻声缓语，知性温润", "gender": "female"},
    {"id": "longyuan", "backend": "longyuan_v2", "name": "温润清雅", "desc": "柔和雅致，适合慢读", "gender": "female"},
    {"id": "longwan", "backend": "longwan_v2", "name": "柔婉从容", "desc": "温柔舒缓，气息绵长", "gender": "female"},
    {"id": "longjing", "backend": "longjing_v2", "name": "知性端方", "desc": "沉静有礼，适合讲读", "gender": "female"},
    {"id": "longyue", "backend": "longyue_v2", "name": "温暖平和", "desc": "暖声细语，亲近自然", "gender": "female"},
    {"id": "longxiaobai", "backend": "longxiaobai_v2", "name": "沉静雅致", "desc": "含蓄内敛，不急不躁", "gender": "female"},
]

VOICE_PRESETS = {item["id"]: item["backend"] for item in VOICE_CATALOG}
VOICE_PRESETS.update(
    {
        "fuzi": "longjin_v2",
        "yanhui": "longxiaochun_v2",
        "zilu": "longlaotie_v2",
        "zigong": "longxiaocheng_v2",
        "ziyou": "longyuan_v2",
        # 兼容旧 id / 已带后缀的调用
        "longxiang": "longjin_v2",
        "longjin_v2": "longjin_v2",
        "longshu_v2": "longshu_v2",
        "longxiaocheng_v2": "longxiaocheng_v2",
        "longlaotie_v2": "longlaotie_v2",
        "longshuo_v2": "longshuo_v2",
        "longcheng_v2": "longcheng_v2",
        "longxiaochun_v2": "longxiaochun_v2",
        "longyuan_v2": "longyuan_v2",
        "longwan_v2": "longwan_v2",
        "longjing_v2": "longjing_v2",
        "longyue_v2": "longyue_v2",
        "longxiaobai_v2": "longxiaobai_v2",
    }
)


def _require_key() -> str:
    if not DASHSCOPE_API_KEY.strip():
        raise AskError("请在 rag/.env 中配置 DASHSCOPE_API_KEY（阿里云百炼）。")
    return DASHSCOPE_API_KEY


def resolve_voice(voice: str) -> str:
    voice = (voice or "longxiang").strip()
    if voice in VOICE_PRESETS:
        return VOICE_PRESETS[voice]
    if voice == "mine":
        raise AskError("还没有克隆音色，请先上传音频。")
    # 已是克隆音色 id（如 cosyvoice-v2-xxx）则原样使用
    return voice


def synthesize_speech(text: str, voice: str = "longxiang") -> Path:
    text = text.strip()
    if not text:
        raise AskError("合成文本是空的。")
    if len(text) > 2000:
        raise AskError("合成文本请控制在 2000 字以内。")
    key = _require_key()
    try:
        import dashscope
        from dashscope.audio.tts_v2 import SpeechSynthesizer
    except ImportError as exc:
        raise AskError("未安装 dashscope，请执行：pip install dashscope") from exc

    dashscope.api_key = key
    voice_id = resolve_voice(voice)
    stamp = datetime.now().strftime("%H%M%S")
    path = AUDIO_DIR / f"{stamp}_{voice_id}.mp3"
    try:
        synthesizer = SpeechSynthesizer(model=COSYVOICE_MODEL, voice=voice_id)
        audio = synthesizer.call(text)
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        if "Model not exist" in message or "model" in message.lower():
            raise AskError(
                f"语音合成失败：当前账号未开通 {COSYVOICE_MODEL}，请在百炼控制台开通 CosyVoice。"
            ) from exc
        raise AskError(f"语音合成失败：{exc}") from exc
    if not audio:
        raise AskError("语音合成没有返回音频。")
    path.write_bytes(audio)
    return path


def clone_voice(audio_path: str | Path, prefix: str | None = None) -> str:
    key = _require_key()
    path = Path(audio_path)
    if not path.is_file():
        raise AskError("克隆用的音频不存在。")
    size = path.stat().st_size
    if size > 10 * 1024 * 1024:
        raise AskError("克隆音频需在 10MB 以内。")
    try:
        import dashscope
        from dashscope.audio.tts_v2 import VoiceEnrollmentService
    except ImportError as exc:
        raise AskError("未安装 dashscope，请执行：pip install dashscope") from exc

    dashscope.api_key = key
    # 音色复刻接口同样走百炼临时存储；模型名须与 target_model 一致
    audio_url = upload_public(path, model=COSYVOICE_MODEL)
    name = prefix or ("uc" + datetime.now().strftime("%H%M%S"))
    service = VoiceEnrollmentService()
    try:
        voice_id = service.create_voice(
            target_model=COSYVOICE_MODEL,
            prefix=name[:10],
            url=audio_url,
        )
    except Exception as exc:  # noqa: BLE001
        # SDK 若无法解析 oss://，改走带 OssResourceResolve 的 HTTP 接口
        if not str(audio_url).startswith("oss://"):
            raise AskError(f"声音克隆失败：{exc}") from exc
        voice_id = _clone_voice_http(key, audio_url, name[:10])
    if not voice_id:
        raise AskError("声音克隆失败：没有返回 voice_id。")
    return str(voice_id)


def _clone_voice_http(api_key: str, audio_url: str, prefix: str) -> str:
    import httpx

    from rag.media_upload import with_oss_resolve

    # CosyVoice 音色复刻 REST（与 SDK 等价）
    url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization"
    headers = with_oss_resolve(
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    )
    payload = {
        "model": "voice-enrollment",
        "input": {
            "action": "create_voice",
            "target_model": COSYVOICE_MODEL,
            "prefix": prefix,
            "url": audio_url,
        },
    }
    response = httpx.post(url, headers=headers, json=payload, timeout=120)
    data = response.json()
    if response.status_code >= 400:
        raise AskError(f"声音克隆失败：{data}")
    voice_id = (
        data.get("output", {}).get("voice_id")
        or data.get("output", {}).get("voice")
        or data.get("voice_id")
    )
    if not voice_id:
        raise AskError(f"声音克隆失败：{data}")
    return str(voice_id)
