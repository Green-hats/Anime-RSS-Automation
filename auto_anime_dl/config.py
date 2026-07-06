from pathlib import Path
from typing import Dict

from .utils import get_env

BASE_DIR = Path(__file__).resolve().parents[1]

# PikPak credentials and folder. Configure these via environment variables.
PIKPAK_USERNAME: str | None = get_env("PIKPAK_USERNAME")
PIKPAK_PASSWORD: str | None = get_env("PIKPAK_PASSWORD")
ROOT_FOLDER_ID: str | None = get_env("PIKPAK_ROOT_FOLDER_ID")

# Data file paths (default to project root)
BANGUMI_JSON_PATH = str(BASE_DIR / "bangumi.json")
BANGUMI_WITH_COVER_JSON_PATH = str(BASE_DIR / "bangumi_with_cover.json")
FOLDER_STRUCTURE_PATH = str(BASE_DIR / "pikpak_folder_structure.json")
BANGUMI_WITH_PLAY_URL_PATH = str(BASE_DIR / "bangumi_with_play_url.json")

# RSS sources. Set RSS_URL_ANIME_COLLECTION in your environment before running.
RSS_URLS: Dict[str, str] = {
    "anime_collection": get_env("RSS_URL_ANIME_COLLECTION", "") or ""
}

# Scheduler / state
STATE_PATH = str(BASE_DIR / ".processed_state.json")
SCHEDULE_INTERVAL_SECONDS = int(get_env("SCHEDULE_INTERVAL_SECONDS", "21600") or "21600")
