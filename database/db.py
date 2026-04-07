import json
import os
import shutil
import sys
from pathlib import Path
from typing import List


def _resolve_db_dir() -> Path:
    # In packaged EXE mode, write to a user-writable location.
    if getattr(sys, "frozen", False):
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "TCC-Feud" / "database"
        return Path(sys.executable).resolve().parent / "database"
    return Path(__file__).resolve().parent


def _resolve_bundled_games_file() -> Path | None:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        bundled = base / "database" / "games.json"
        if bundled.exists():
            return bundled
    return None


DB_DIR = _resolve_db_dir()
GAMES_FILE = DB_DIR / "games.json"


def ensure_db_dir() -> None:
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def ensure_games_file() -> None:
    ensure_db_dir()
    if GAMES_FILE.exists():
        return

    bundled_file = _resolve_bundled_games_file()
    if not bundled_file:
        return

    try:
        shutil.copy2(bundled_file, GAMES_FILE)
    except Exception:
        pass


def load_games() -> List[dict]:
    ensure_games_file()
    if not GAMES_FILE.exists():
        return []
    try:
        with GAMES_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_games(games: List[dict]) -> bool:
    ensure_db_dir()
    try:
        with GAMES_FILE.open("w", encoding="utf-8") as f:
            json.dump(games, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False
