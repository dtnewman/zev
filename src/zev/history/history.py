from pathlib import Path
import json
from typing import Optional
from collections import OrderedDict

from zev.llms.types import OptionsResponse, Command


class History:
    def __init__(self, max_entries: int = 100):
        self.history_dir = Path.home() / ".zev"
        self.history_file = self.history_dir / "zev_history.jsonl"
        self.max_entries = max_entries

    def save_options(self, words: str, options: OptionsResponse):
        self.history_dir.mkdir(exist_ok=True)

        options_response = {
            "words": words,
            "commands": [
                {
                    "command": cmd.command,
                    "short_explanation": cmd.short_explanation,
                    "is_dangerous": cmd.is_dangerous,
                    "dangerous_explanation": cmd.dangerous_explanation,
                }
                for cmd in options.commands
            ]
        }

        existing_entries = []
        if self.history_file.exists():
            try:
                with self.history_file.open("r") as f:
                    existing_entries = [json.loads(line) for line in f if line.strip()]
            except (json.JSONDecodeError, IOError):
                existing_entries = []

        all_entries = [options_response] + existing_entries
        all_entries = all_entries[:self.max_entries]

        with self.history_file.open("w") as f:
            for entry in all_entries:
                f.write(json.dumps(entry) + "\n")

    def _parse_command(self, cmd_dict: dict) -> Command:
        return Command(
            command=cmd_dict["command"],
            short_explanation=cmd_dict["short_explanation"],
            is_dangerous=cmd_dict["is_dangerous"],
            dangerous_explanation=cmd_dict.get("dangerous_explanation")
        )

    def get_history(self) -> Optional[dict[str, OptionsResponse]]:
        if not self.history_file.exists():
            return None

        try:
            entries = OrderedDict()
            with self.history_file.open("r") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        words = entry["words"]
                        options_response = OptionsResponse(
                            commands=[
                                self._parse_command(cmd)
                                for cmd in entry["commands"]
                            ],
                            is_valid=True,
                            explanation_if_not_valid=None
                        )
                        entries[words] = options_response

            return entries if entries else None
        except (json.JSONDecodeError, IOError):
            return None


history = History()
