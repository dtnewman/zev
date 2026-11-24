import os
import platform
import shutil
import subprocess


class ClipboardError(Exception):
    pass


def _candidate_commands() -> list[tuple[list[str], str]]:
    """Clipboard commands to try, in order, as (argv, input encoding)."""
    system = platform.system()
    if system == "Darwin":
        return [(["pbcopy"], "utf-8")]
    if system == "Windows":
        return [(["clip"], "utf-16")]  # clip.exe reads UTF-16 with a BOM correctly

    candidates = []
    if os.environ.get("WAYLAND_DISPLAY"):
        candidates.append((["wl-copy"], "utf-8"))
    candidates += [
        (["xclip", "-selection", "clipboard"], "utf-8"),
        (["xsel", "--clipboard", "--input"], "utf-8"),
        (["clip.exe"], "utf-16"),  # WSL
    ]
    return candidates


def copy(text: str) -> None:
    for argv, encoding in _candidate_commands():
        if not shutil.which(argv[0]):
            continue
        try:
            subprocess.run(argv, input=text.encode(encoding), check=True, timeout=5)
            return
        except (OSError, subprocess.SubprocessError):
            continue
    raise ClipboardError("No working clipboard command found")
