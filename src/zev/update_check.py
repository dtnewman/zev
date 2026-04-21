import json
import sys
import threading
import time
from importlib.metadata import version
from urllib.error import URLError
from urllib.request import urlopen

from zev.paths import get_app_dir

CACHE_FILE = get_app_dir() / "update_cache"
CHECK_INTERVAL = 86400  # 24 hours
PYPI_URL = "https://pypi.org/pypi/zev/json"


def _parse_version(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


def _fetch_latest_version() -> str | None:
    try:
        with urlopen(PYPI_URL, timeout=3) as resp:
            data = json.loads(resp.read())
            return data["info"]["version"]
    except Exception:
        return None


def _should_check() -> bool:
    if not CACHE_FILE.exists():
        return True
    try:
        return time.time() - CACHE_FILE.stat().st_mtime > CHECK_INTERVAL
    except Exception:
        return True


def _write_cache(latest: str | None):
    try:
        CACHE_FILE.write_text(latest or "")
    except Exception:
        pass


def _read_cache() -> str | None:
    try:
        content = CACHE_FILE.read_text().strip()
        return content if content else None
    except Exception:
        return None


def _is_homebrew_install() -> bool:
    return "Cellar" in sys.executable


def get_update_message() -> str | None:
    """Return a Rich-formatted update notice if a newer version is cached, else None."""
    try:
        current = version("zev")
    except Exception:
        return None

    latest = _read_cache()
    if latest and _parse_version(latest) > _parse_version(current):
        if _is_homebrew_install():
            upgrade_cmd = "brew upgrade zev"
        else:
            upgrade_cmd = "pipx upgrade zev"
        return (
            f"[yellow]A new version of zev is available: [bold]{latest}[/bold] "
            f"(you have {current}). Run [bold]{upgrade_cmd}[/bold] to update.[/yellow]"
        )
    return None


def check_for_updates_in_background():
    """Kick off a background thread to refresh the PyPI version cache."""
    if not _should_check():
        return

    def _check():
        latest = _fetch_latest_version()
        _write_cache(latest)

    threading.Thread(target=_check, daemon=True).start()
