"""LivePortrait：人脸检测与数字人视频。"""

from __future__ import annotations

import time
from typing import Any

import httpx

from rag.config import DASHSCOPE_API_KEY
from rag.llm import AskError
from rag.media_upload import with_oss_resolve


class LivePortraitAPI:
    def __init__(self) -> None:
        if not DASHSCOPE_API_KEY.strip():
            raise AskError("请在 rag/.env 中配置 DASHSCOPE_API_KEY（阿里云百炼）。")
        self.headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }
        self.detect_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/face-detect"
        self.generate_url = (
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis/"
        )
        self.task_url = "https://dashscope.aliyuncs.com/api/v1/tasks/"

    def _headers(self, *, async_mode: bool = False) -> dict[str, str]:
        # oss:// 临时链接必须带 OssResourceResolve，否则百炼无法解析
        headers = with_oss_resolve(self.headers)
        if async_mode:
            headers["X-DashScope-Async"] = "enable"
        return headers

    def detect_face(self, image_url: str) -> dict[str, Any]:
        payload = {"model": "liveportrait-detect", "input": {"image_url": image_url}}
        response = httpx.post(self.detect_url, headers=self._headers(), json=payload, timeout=60)
        data = response.json()
        if response.status_code >= 400:
            raise AskError(f"人脸检测失败：{data}")
        return data

    def generate_video(
        self,
        image_url: str,
        audio_url: str,
        # calm/适中幅度：诵读时轻微点头与口型，过大反而露破绽
        template_id: str = "calm",
        eye_move_freq: float = 0.4,
        video_fps: int = 30,
        mouth_move_strength: float = 0.85,
        paste_back: bool = True,
        head_move_strength: float = 0.45,
    ) -> dict[str, Any]:
        payload = {
            "model": "liveportrait",
            "input": {"image_url": image_url, "audio_url": audio_url},
            "parameters": {
                "template_id": template_id,
                "eye_move_freq": eye_move_freq,
                "video_fps": video_fps,
                "mouth_move_strength": mouth_move_strength,
                "paste_back": paste_back,
                "head_move_strength": head_move_strength,
            },
        }
        response = httpx.post(
            self.generate_url,
            headers=self._headers(async_mode=True),
            json=payload,
            timeout=60,
        )
        data = response.json()
        if response.status_code >= 400:
            raise AskError(f"提交视频任务失败：{data}")
        return data

    def check_task(self, task_id: str) -> dict[str, Any]:
        response = httpx.get(f"{self.task_url}{task_id}", headers=self.headers, timeout=30)
        return response.json()

    def wait_for_task(
        self,
        task_id: str,
        polling_interval: float = 5,
        max_attempts: int = 72,
    ) -> dict[str, Any]:
        for _ in range(max_attempts):
            data = self.check_task(task_id)
            status = data.get("output", {}).get("task_status")
            if status in {"SUCCEEDED", "FAILED"}:
                return data
            time.sleep(polling_interval)
        raise AskError("视频生成超时，请稍后再试。")

    def detect_emo(self, image_url: str, ratio: str = "3:4") -> dict[str, Any]:
        payload = {
            "model": "emo-detect-v1",
            "input": {"image_url": image_url},
            "parameters": {"ratio": ratio},
        }
        response = httpx.post(self.detect_url, headers=self._headers(), json=payload, timeout=60)
        data = response.json()
        if response.status_code >= 400:
            raise AskError(f"人像检测失败：{data}")
        return data

    def generate_emo_video(
        self,
        image_url: str,
        audio_url: str,
        face_bbox: list,
        ext_bbox: list,
        # calm：动作克制，更像自然诵读，减少大幅晃动露馅
        style_level: str = "calm",
    ) -> dict[str, Any]:
        payload = {
            "model": "emo-v1",
            "input": {
                "image_url": image_url,
                "audio_url": audio_url,
                "face_bbox": face_bbox,
                "ext_bbox": ext_bbox,
            },
            "parameters": {"style_level": style_level},
        }
        response = httpx.post(
            self.generate_url,
            headers=self._headers(async_mode=True),
            json=payload,
            timeout=60,
        )
        data = response.json()
        if response.status_code >= 400:
            raise AskError(f"提交诵读视频任务失败：{data}")
        return data

    def detect_wan_s2v(self, image_url: str) -> dict[str, Any]:
        """万相数字人图像检测（当前账号可用；LivePortrait/EMO 常报 Model not exist）。"""
        payload = {"model": "wan2.2-s2v-detect", "input": {"image_url": image_url}}
        response = httpx.post(self.detect_url, headers=self._headers(), json=payload, timeout=60)
        data = response.json()
        if response.status_code >= 400 or data.get("code"):
            raise AskError(f"人脸检测失败：{data}")
        return data

    def generate_wan_s2v(
        self,
        image_url: str,
        audio_url: str,
        *,
        resolution: str = "480P",
        style: str = "speech",
    ) -> dict[str, Any]:
        payload = {
            "model": "wan2.2-s2v",
            "input": {"image_url": image_url, "audio_url": audio_url},
            "parameters": {"resolution": resolution, "style": style},
        }
        response = httpx.post(
            self.generate_url,
            headers=self._headers(async_mode=True),
            json=payload,
            timeout=60,
        )
        data = response.json()
        if response.status_code >= 400 or data.get("code"):
            raise AskError(f"提交视频任务失败：{data}")
        return data
