"""根据个人照片生成古风形象：只参照五官，服装与氛围按性别提示词生成。"""

from __future__ import annotations

import base64
import io
import mimetypes
import time
from pathlib import Path
from typing import Any

import httpx

from rag.config import DASHSCOPE_API_KEY, FIGURE_DIR
from rag.llm import AskError
from rag.media_upload import upload_public, with_oss_resolve

# 构图须满足数字人人脸检测：单人、正脸、双眼清晰、面部无遮挡、头肩半身
FACE_DETECT_RULES = (
    "必须是一张可用于数字人口型驱动的证件照式半身肖像："
    "画面中只有一个人；人脸正对镜头、双眼平视前方且完全睁开；"
    "五官清晰完整、无遮挡；额头、眉毛、眼睛、鼻子、嘴巴、双颊全部可见；"
    "面部约占画面高度的百分之三十到四十五；头与双肩入镜，胸部以上构图，居中；"
    "柔和均匀的影棚正面光，面部无大面积阴影；表情自然平静、嘴唇自然闭合；"
    "双手不要出现在脸前；不要侧脸、仰拍、俯拍、远景全身。"
)

MALE_PROMPT = (
    f"{FACE_DETECT_RULES}"
    "中国古典写实人像，宋代士大夫风骨，水墨丹青意境，超高清古风定妆照。"
    "一位十六到二十五岁的古代书生少年，面如冠玉，眉目清朗，神情温润儒雅。"
    "乌发以青色丝绦束成高髻或总角，额前发丝整齐不遮眉眼；"
    "不戴官帽、幞头、斗笠，不戴口罩墨镜，面部完全露出。"
    "身着石青交领右衽直裰长袍，袖口宽博垂坠，领缘与袖口有细窄暗纹滚边，"
    "腰系玄色丝绦，衣料为细麻与绸缎质感，色调青黛、月白、黛蓝。"
    "背景为淡墨晕染的宣纸质感浅灰，隐约有远山或竹影，氛围清寂雅致，"
    "如古画工笔人物，光影柔和，突出衣褶与面容。"
)

FEMALE_PROMPT = (
    f"{FACE_DETECT_RULES}"
    "中国古典写实人像，唐代仕女与宋制汉服雅韵，工笔重彩写真，超高清古风定妆照。"
    "一位十八到二十八岁的古代女子，娥眉淡扫，面若桃花，神态娴静温婉。"
    "乌发高绾成云髻或螺髻，发丝服帖，刘海不得遮住眼睛与眉毛；"
    "仅可在发髻后方饰极小金钗或珠花，饰物远离五官，不垂流苏挡脸；"
    "不戴帷帽、面纱、口罩，面部完全露出。"
    "身着交领右衽汉服襦裙上襦，外罩薄纱披帛自然垂落于肩臂（不遮脸），"
    "色调为缃黄、茜红、藕荷、青绿等传统矿物色，衣缘有暗金细绣；"
    "织物质感细腻，层叠真丝与轻纱。"
    "背景为素宣纸白或淡墨远山，如仕女图，影棚柔光，古典雅致。"
)

FACE_PREFIX = (
    "严格保留参考照片中人物的五官、脸型、眉眼与神态，只参照面部样貌，"
    "不要复制原图的服装、发型、配饰与背景。"
    "整体气质必须是中国古代人物，不要现代装或日韩风。"
    "输出必须保证整张正脸清晰可辨，便于后续人脸检测与口型驱动。"
)

NEGATIVE_PROMPT = (
    "变形五官, 换脸失败, 多人, 模糊, 低分辨率, 文字水印, 字幕, "
    "现代服装, 西装, 衬衫, 运动鞋, T恤, 牛仔裤, 嘻哈风, 赛博朋克, "
    "日系JK, 韩系妆造, 欧美时装, 新中式西服, 夸张表情, 闭眼, "
    "侧脸, 侧身, 仰视, 俯视, 遮挡面部, 刘海遮眼, 头发遮脸, "
    "帽子压眉, 官帽遮额, 口罩, 墨镜, 面纱, 手挡脸, 手持扇子遮脸, "
    "过大发饰, 流苏挡脸, 鲜花挡脸, 阴影遮脸, 远景全身, 脸过小, 多余手指"
)

# 优先千问图像编辑（支持 oss:// 临时链）；万相垫图仅接受公网 http(s)
QWEN_EDIT_MODELS = ("qwen-image-edit-plus", "qwen-image-2.0-pro")


def _require_key() -> str:
    if not DASHSCOPE_API_KEY.strip():
        raise AskError("请在 rag/.env 中配置 DASHSCOPE_API_KEY（阿里云百炼）。")
    return DASHSCOPE_API_KEY


def _prepare_image(path: Path, max_side: int = 1536) -> tuple[bytes, str]:
    """压缩到接口友好尺寸，返回 (jpeg_bytes, mime)。"""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        raw = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        return raw, mime

    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        elif img.mode == "L":
            img = img.convert("RGB")
        w, h = img.size
        scale = min(1.0, max_side / max(w, h))
        if scale < 1.0:
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90, optimize=True)
        return buf.getvalue(), "image/jpeg"


def _as_data_url(path: Path) -> str:
    data, mime = _prepare_image(path)
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def _prompt_for(gender: str) -> str:
    body = MALE_PROMPT if gender == "male" else FEMALE_PROMPT
    return f"{FACE_PREFIX}{body}"


def _poll(task_id: str, attempts: int = 80, interval: float = 3) -> dict[str, Any]:
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    for _ in range(attempts):
        response = httpx.get(url, headers=headers, timeout=30)
        data = response.json()
        status = data.get("output", {}).get("task_status")
        if status == "SUCCEEDED":
            return data
        if status == "FAILED":
            message = data.get("output", {}).get("message") or data.get("message") or data
            raise AskError(f"古风形象生成失败：{message}")
        time.sleep(interval)
    raise AskError("古风形象生成超时，请稍后再试。")


def _save_image_bytes(photo_path: Path, content: bytes) -> Path:
    out = FIGURE_DIR / f"{photo_path.stem}_ancient.png"
    out.write_bytes(content)
    return out


def _download_result(image_url: str, photo_path: Path) -> Path:
    image = httpx.get(image_url, timeout=120)
    image.raise_for_status()
    return _save_image_bytes(photo_path, image.content)


def _extract_task_image(result: dict[str, Any]) -> str:
    output = result.get("output") or {}
    results = output.get("results") or []
    if isinstance(results, list) and results:
        first = results[0]
        if isinstance(first, dict):
            return first.get("url") or first.get("orig_url") or ""
        return str(first)
    if isinstance(results, dict):
        return results.get("url") or ""
    return output.get("result_url") or ""


def _extract_qwen_image(data: dict[str, Any]) -> str:
    content = (
        ((data.get("output") or {}).get("choices") or [{}])[0]
        .get("message", {})
        .get("content")
    )
    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            image_url = item.get("image") or item.get("url") or ""
            if image_url:
                return str(image_url)
    elif isinstance(content, dict):
        return str(content.get("image") or content.get("url") or "")
    return ""


def detect_gender(photo_path: str | Path) -> str:
    """用视觉模型判断照片人物性别，返回 male / female。"""
    path = Path(photo_path)
    headers = with_oss_resolve(
        {
            "Authorization": f"Bearer {_require_key()}",
            "Content-Type": "application/json",
        }
    )
    # 性别识别优先走临时 OSS，避免大图 base64 撑爆请求
    try:
        image_ref = upload_public(path, model="qwen-vl-plus")
    except AskError:
        image_ref = _as_data_url(path)
    payload = {
        "model": "qwen-vl-plus",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": image_ref},
                        {
                            "text": (
                                "判断照片中主要人物的生理性别。"
                                "只回答一个英文单词：male 或 female。"
                            )
                        },
                    ],
                }
            ]
        },
    }
    try:
        response = httpx.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            headers=headers,
            json=payload,
            timeout=60,
        )
        data = response.json()
        text = (
            ((data.get("output") or {}).get("choices") or [{}])[0]
            .get("message", {})
            .get("content")
        )
        if isinstance(text, list):
            text = " ".join(str(item.get("text") or "") for item in text if isinstance(item, dict))
        raw = str(text or "").lower()
        if "female" in raw or "女" in raw:
            return "female"
        if "male" in raw or "男" in raw:
            return "male"
    except Exception:
        pass
    return "male"


def _generate_qwen_edit(photo_path: Path, prompt: str) -> Path:
    """通义千问图像编辑：在原脸上改服装与场景。"""
    last_error: AskError | None = None
    # 缩略 jpeg，降低上传与推理失败率
    prepared = FIGURE_DIR / f"{photo_path.stem}_prep.jpg"
    prepared.write_bytes(_prepare_image(photo_path)[0])
    data_url = _as_data_url(photo_path)

    for model_name in QWEN_EDIT_MODELS:
        # 临时 OSS 凭证与模型绑定，按当前模型单独上传；失败再退回 base64
        image_refs: list[str] = []
        try:
            image_refs.append(upload_public(prepared, model=model_name))
        except AskError as exc:
            last_error = exc
        image_refs.append(data_url)

        for image_ref in image_refs:
            headers = {
                "Authorization": f"Bearer {_require_key()}",
                "Content-Type": "application/json",
            }
            if str(image_ref).startswith("oss://"):
                headers = with_oss_resolve(headers)
            payload = {
                "model": model_name,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"image": image_ref},
                                {"text": prompt[:800]},
                            ],
                        }
                    ]
                },
                "parameters": {
                    "n": 1,
                    "negative_prompt": NEGATIVE_PROMPT[:500],
                    "prompt_extend": True,
                    "watermark": False,
                    "size": "768*1152",
                },
            }
            try:
                response = httpx.post(
                    "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
                    headers=headers,
                    json=payload,
                    timeout=180,
                )
                data = response.json()
                if response.status_code >= 400 or data.get("code"):
                    message = data.get("message") or data
                    last_error = AskError(f"图像编辑失败（{model_name}）：{message}")
                    continue
                image_url = _extract_qwen_image(data)
                if not image_url:
                    last_error = AskError(f"图像编辑没有返回图片：{str(data)[:400]}")
                    continue
                if image_url.startswith("data:"):
                    raw = image_url.split(",", 1)[-1]
                    return _save_image_bytes(photo_path, base64.b64decode(raw))
                return _download_result(image_url, photo_path)
            except AskError as exc:
                last_error = exc
            except Exception as exc:  # noqa: BLE001
                last_error = AskError(f"图像编辑失败（{model_name}）：{exc}")
    raise last_error or AskError("图像编辑失败。")


def _generate_wanx_ref(photo_path: Path, prompt: str) -> Path:
    """万相文生图（无垫图）。wanx-v1 的 ref 只接受公网 http(s)，临时 oss:// 会报 url error。"""
    payload = {
        "model": "wanx-v1",
        "input": {
            "prompt": prompt[:800],
            "negative_prompt": NEGATIVE_PROMPT[:500],
        },
        "parameters": {
            "style": "<auto>",
            "size": "768*1152",
            "n": 1,
        },
    }
    response = httpx.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
        headers={
            "Authorization": f"Bearer {_require_key()}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        json=payload,
        timeout=60,
    )
    data = response.json()
    if response.status_code >= 400 or data.get("code"):
        raise AskError(f"提交古风形象任务失败：{data.get('message') or data}")
    task_id = data.get("output", {}).get("task_id")
    if not task_id:
        raise AskError(f"古风形象任务没有返回 task_id：{data}")
    result = _poll(task_id)
    image_url = _extract_task_image(result)
    if not image_url:
        raise AskError(f"古风形象没有返回图片地址：{result}")
    return _download_result(image_url, photo_path)


def normalize_gender(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if raw in {"female", "女", "woman", "women"}:
        return "female"
    if raw in {"male", "男", "man", "men"}:
        return "male"
    return ""


def repaint_ancient(
    photo_path: str | Path,
    virtue: str = "温",
    gender: str = "",
) -> Path:
    del virtue  # 服装与氛围按性别提示词，不再用五德风格索引
    path = Path(photo_path)
    if not path.is_file():
        raise AskError("照片不存在。")
    gender = normalize_gender(gender) or detect_gender(path)
    prompt = _prompt_for(gender)
    last_error = None
    # 千问编辑可保留五官；万相仅作文生图兜底（无法可靠垫图）
    for generator in (_generate_qwen_edit, _generate_wanx_ref):
        try:
            return generator(path, prompt)
        except AskError as exc:
            last_error = exc
        except Exception as exc:  # noqa: BLE001
            last_error = AskError(str(exc))
    raise last_error or AskError("古风形象生成失败。")
