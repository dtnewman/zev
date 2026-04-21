from pathlib import Path

from platformdirs import user_data_dir


def get_app_dir() -> Path:
    path = Path(user_data_dir("zev", appauthor=False))
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
