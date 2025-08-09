from pathlib import Path
from typing import Dict, Any

from .utils import get_env


BASE_DIR = Path(__file__).resolve().parents[1]


# PikPak credentials and folder
PIKPAK_USERNAME: str | None = get_env("PIKPAK_USERNAME", "22470456@qq.com")
PIKPAK_PASSWORD: str | None = get_env("PIKPAK_PASSWORD", "zwx123456")
ROOT_FOLDER_ID: str | None = get_env("PIKPAK_ROOT_FOLDER_ID", "VOXDJE957ERLA8IV6Wjc4z2So2")


# Data file paths (default to project root)
BANGUMI_JSON_PATH = str(BASE_DIR / "bangumi.json")
BANGUMI_WITH_COVER_JSON_PATH = str(BASE_DIR / "bangumi_with_cover.json")
FOLDER_STRUCTURE_PATH = str(BASE_DIR / "pikpak_folder_structure.json")
BANGUMI_WITH_PLAY_URL_PATH = str(BASE_DIR / "bangumi_with_play_url.json")


# RSS sources
RSS_URLS: Dict[str, str] = {
    "anime_collection": get_env(
        "RSS_URL_ANIME_COLLECTION",
        "https://api.animes.garden/collection/3790167938bdc0674002219aa20e705d0c692334/feed.xml",
    )
}

# Scheduler / state
STATE_PATH = str(BASE_DIR / ".processed_state.json")
SCHEDULE_INTERVAL_SECONDS = int(get_env("SCHEDULE_INTERVAL_SECONDS", "21600") or "21600")  # default 6h


