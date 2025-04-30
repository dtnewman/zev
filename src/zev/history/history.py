from pathlib import Path
import json
from typing import Optional, Dict
from collections import OrderedDict

from zev.llms.types import OptionsResponse, Command


class History:
    def __init__(self, max_entries: int = 100):
        self.history_file = Path.home() / ".zevhistory"
        self.max_entries = max_entries

    def save_options(self, words: str, options: OptionsResponse):
        options_response = {
            "query": words,
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

        history_entries = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    history_entries = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        history_entries.insert(0, options_response)
        history_entries = history_entries[:self.max_entries]

        with open(self.history_file, "w") as f:
            json.dump(history_entries, f, indent=2)

    def get_history(self) -> Optional[Dict[str, OptionsResponse]]:
        if not self.history_file.exists():
            return None

        try:
            with open(self.history_file, "r") as f:
                history_entries = json.load(f)
            
            entries = OrderedDict()
            for entry in history_entries:
                words = entry["query"]
                commands = [
                    Command(
                        command=cmd["command"],
                        short_explanation=cmd["short_explanation"],
                        is_dangerous=cmd["is_dangerous"],
                        dangerous_explanation=cmd.get("dangerous_explanation")
                    )
                    for cmd in entry["commands"]
                ]
                
                entries[words] = OptionsResponse(
                    commands=commands,
                    is_valid=True,
                    explanation_if_not_valid=None
                )
            
            return entries if entries else None
        except (json.JSONDecodeError, IOError):
            return None


history = History()
