import os
import sys
from pathlib import Path


def _user_data_dir() -> Path:
    # Same locations platformdirs' user_data_dir("zev", appauthor=False) used, so existing configs are found.
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    xdg_data_home = os.environ.get("XDG_DATA_HOME", "").strip()
    return Path(xdg_data_home) if xdg_data_home else Path.home() / ".local" / "share"


def get_app_dir() -> Path:
    path = _user_data_dir() / "zev"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_path() -> Path:
    return get_app_dir() / "config"


def get_history_path() -> Path:
    return get_app_dir() / "history"


def migrate_legacy_files() -> None:
    """Move legacy ~/. files to the app data dir if they exist."""
    home = Path.home()
    migrations = [
        (home / ".zevrc", get_config_path()),
        (home / ".zevhistory", get_history_path()),
        (home / ".zev_update_cache", get_app_dir() / "update_cache"),
    ]
    for old, new in migrations:
        if old.exists() and not new.exists():
            old.rename(new)
