"""把本地文件上传到百炼临时存储，供 LivePortrait / CosyVoice 等接口使用。

原课程机 `upload_dhuman.php` 已 404，改为官方临时 OSS：
https://help.aliyun.com/zh/model-studio/get-temporary-file-url
"""

from __future__ import annotations

import uuid
from pathlib import Path

import httpx

from rag.config import DASHSCOPE_API_KEY, DHUMAN_UPLOAD_URL, MEDIA_UPLOAD_BACKEND
from rag.llm import AskError

_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".mp4": "video/mp4",
}

# 调用模型时若 URL 以 oss:// 开头，必须带此 Header
OSS_RESOLVE_HEADER = {"X-DashScope-OssResourceResolve": "enable"}


def _require_key() -> str:
    if not DASHSCOPE_API_KEY.strip():
        raise AskError("请在 rag/.env 中配置 DASHSCOPE_API_KEY（阿里云百炼）。")
    return DASHSCOPE_API_KEY


def _get_policy(api_key: str, model: str) -> dict:
    response = httpx.get(
        "https://dashscope.aliyuncs.com/api/v1/uploads",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        params={"action": "getPolicy", "model": model},
        timeout=30,
    )
    data = response.json()
    if response.status_code >= 400:
        raise AskError(f"获取百炼上传凭证失败：{data}")
    policy = data.get("data")
    if not policy:
        raise AskError(f"获取百炼上传凭证失败：{data}")
    return policy


def _upload_dashscope(path: Path, model: str) -> str:
    """上传到百炼临时存储，返回 oss://... URL（约 48 小时有效）。"""
    api_key = _require_key()
    policy = _get_policy(api_key, model)
    # 避免同名覆盖（凭证里往往 forbid_overwrite=true）
    safe_name = f"{uuid.uuid4().hex[:12]}_{path.name}"
    key = f"{policy['upload_dir']}/{safe_name}"
    mime = _MIME.get(path.suffix.lower(), "application/octet-stream")

    with path.open("rb") as handle:
        response = httpx.post(
            policy["upload_host"],
            data={
                "OSSAccessKeyId": policy["oss_access_key_id"],
                "Signature": policy["signature"],
                "policy": policy["policy"],
                "x-oss-object-acl": policy["x_oss_object_acl"],
                "x-oss-forbid-overwrite": policy["x_oss_forbid_overwrite"],
                "key": key,
                "success_action_status": "200",
            },
            files={"file": (safe_name, handle, mime)},
            timeout=120,
        )
    if response.status_code >= 300:
        raise AskError(f"上传到百炼临时存储失败：HTTP {response.status_code} {response.text[:300]}")
    return f"oss://{key}"


def _upload_dhuman(path: Path) -> str:
    """兼容旧的课程上传机（若仍可用）。"""
    mime = _MIME.get(path.suffix.lower(), "application/octet-stream")
    with path.open("rb") as handle:
        response = httpx.post(
            DHUMAN_UPLOAD_URL,
            files={"file": (path.name, handle, mime)},
            headers={"User-Agent": "lunyu-presence/1.0"},
            timeout=120,
        )
    response.raise_for_status()
    data = response.json()
    if not data.get("success") or not data.get("url"):
        raise AskError(f"公网上传失败：{data.get('error') or data}")
    return str(data["url"])


def upload_public(file_path: str | Path, model: str = "liveportrait") -> str:
    """上传本地文件，返回可供百炼模型读取的 URL。

    优先走百炼临时存储（需指定后续调用的 model 名）；
    若显式配置了可用的 DHUMAN_UPLOAD_URL 且环境变量 MEDIA_UPLOAD_BACKEND=dhuman，则走旧通道。
    """
    path = Path(file_path)
    if not path.is_file():
        raise AskError(f"文件不存在：{path}")

    backend = (MEDIA_UPLOAD_BACKEND or "dashscope").strip().lower()
    if backend == "dhuman":
        try:
            return _upload_dhuman(path)
        except Exception as exc:  # noqa: BLE001
            raise AskError(f"公网上传失败：{exc}") from exc

    try:
        return _upload_dashscope(path, model=model or "liveportrait")
    except AskError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AskError(f"公网上传失败：{exc}") from exc


def with_oss_resolve(headers: dict[str, str] | None = None) -> dict[str, str]:
    """合并 OssResourceResolve 头，供携带 oss:// URL 的请求使用。"""
    merged = dict(headers or {})
    merged.update(OSS_RESOLVE_HEADER)
    return merged
