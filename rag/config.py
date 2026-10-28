import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = Path(__file__).resolve().parent / ".env"


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file(ENV_FILE)

DATA_DIR = Path(os.environ.get("LUNYU_DATA_DIR", ROOT / "数据"))

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5434/lunyu",
)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "bge-m3")
EMBED_DIM = 1024

# 对话走 Nebius Token Factory 上的 NVIDIA Nemotron。密钥只写在 rag/.env。
# 正式回答用 Super；寒暄和路由用 Nano，避免把额度花在短句上。
NEBIUS_API_KEY = os.environ.get("NEBIUS_API_KEY", "")
NEBIUS_BASE_URL = os.environ.get(
    "NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"
).rstrip("/")
NEBIUS_MODEL = os.environ.get("NEBIUS_MODEL", "nvidia/nemotron-3-super-120b-a12b")
NEBIUS_FAST_MODEL = os.environ.get(
    "NEBIUS_FAST_MODEL", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
)

# 风骨创作：阿里云百炼（CosyVoice / LivePortrait / 人像风格重绘）
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
# 公网上传后端：dashscope（推荐）| dhuman（旧课程机，多数已失效）
MEDIA_UPLOAD_BACKEND = os.environ.get("MEDIA_UPLOAD_BACKEND", "dashscope")
DHUMAN_UPLOAD_URL = os.environ.get(
    "DHUMAN_UPLOAD_URL",
    "http://8.130.18.16/upload_dhuman.php",
)

MEDIA_ROOT = Path(__file__).resolve().parent / "output"
UPLOAD_DIR = MEDIA_ROOT / "uploads"
AUDIO_DIR = MEDIA_ROOT / "audio"
FIGURE_DIR = MEDIA_ROOT / "figures"
VIDEO_DIR = MEDIA_ROOT / "video"
for _dir in (UPLOAD_DIR, AUDIO_DIR, FIGURE_DIR, VIDEO_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# 超过这个长度的章再按句号切开，切开的每一段仍带着同一个章号。
MAX_CHUNK_CHARS = 1200
