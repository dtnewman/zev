from pathlib import Path
from typing import Optional

from zev.llms.types import OptionsResponse, HistoryEntry

class History:
    def __init__(self, max_entries: int = 100, file: Optional[Path] = None) -> None:
        self.path = file or Path.home() / ".zevhistory"
        self.max_entries = max_entries
        self.path.touch(exist_ok=True)
        self.encoding = "utf-8"

    def save_options(self, query: str, options: OptionsResponse) -> None:
        entry = HistoryEntry(
            query=query,
            response=options,
        )
        with open(self.path, "a", encoding=self.encoding) as f:
            f.write(entry.model_dump_json())
            f.write("\n")
        self._enforce_limit()

    def get_history(self) -> dict[str, HistoryEntry]:
        with open(self.path, "r", encoding=self.encoding) as f:
            entries = [
                HistoryEntry.model_validate_json(line)
                for line in f
                if line.strip()
            ]

        if not entries:
            return None

        return { entry.query: entry for entry in reversed(entries) }
    
    def _enforce_limit(self) -> None:
        with open(self.path, "r+", encoding=self.encoding) as f:
            lines = f.readlines()
            if len(lines) <= self.max_entries:
                return
            f.seek(0)
            f.writelines(lines[-self.max_entries :])
            f.truncate()

history = History()
