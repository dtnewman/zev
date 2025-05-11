from pathlib import Path
from typing import Optional

import pyperclip
import questionary
from pydantic import BaseModel
from rich import print as rprint

from zev.constants import HISTORY_FILE_NAME
from zev.llms.types import OptionsResponse


class HistoryEntry(BaseModel):
    query: str
    response: OptionsResponse


class History:
    def __init__(self) -> None:
        self.path = Path.home() / HISTORY_FILE_NAME
        self.max_entries = 100
        self.path.touch(exist_ok=True)
        self.encoding = "utf-8"

    def save_options(self, query: str, options: OptionsResponse) -> None:
        entry = HistoryEntry(query=query, response=options)
        self._write_to_history_file(entry)

    def get_history(self) -> list[HistoryEntry]:
        with open(self.path, "r", encoding=self.encoding) as f:
            entries = [HistoryEntry.model_validate_json(line) for line in f if line.strip()]

        if not entries:
            return None

        return entries

    def _write_to_history_file(self, new_entry: HistoryEntry) -> None:
        with open(self.path, "r+", encoding=self.encoding) as f:
            lines = f.readlines()
            lines.append(new_entry.model_dump_json() + "\n")
            if len(lines) > self.max_entries:
                lines = lines[-self.max_entries :]
            f.seek(0)
            f.writelines(lines)
            f.truncate()

    def display_history_options(self, reverse_history_entries, show_limit=5) -> Optional[HistoryEntry]:
        if not reverse_history_entries:
            print("No command history found")
            return None

        style = questionary.Style(
            [
                ("answer", "fg:#61afef"),
                ("question", "bold"),
                ("instruction", "fg:#98c379"),
            ]
        )

        query_options = [questionary.Choice(entry.query, value=entry) for entry in reverse_history_entries[:show_limit]]

        if len(reverse_history_entries) > show_limit:
            query_options.append(questionary.Choice("Show more...", value="show_more"))

        query_options.append(questionary.Separator())
        query_options.append(questionary.Choice("Cancel"))

        selected = questionary.select(
            "Select from history:", choices=query_options, use_shortcuts=True, style=style
        ).ask()

        if selected == "show_more":
            all_options = [questionary.Choice(entry.query, value=entry) for entry in reverse_history_entries]
            all_options.append(questionary.Separator())
            all_options.append(questionary.Choice("Cancel"))

            return questionary.select(
                "Select from history (showing all items):", choices=all_options, use_shortcuts=True, style=style
            ).ask()

        return selected

    def show_history(self):
        history_entries = self.get_history()
        if not history_entries:
            print("No command history found")
            return

        selected_entry = self.display_history_options(list(reversed(history_entries)))

        if selected_entry in (None, "Cancel"):
            return

        commands = selected_entry.response.commands

        if not commands:
            print("No commands available")
            return None

        style = questionary.Style(
            [
                ("answer", "fg:#61afef"),
                ("question", "bold"),
                ("instruction", "fg:#98c379"),
            ]
        )

        options = [questionary.Choice(cmd.command, description=cmd.short_explanation, value=cmd) for cmd in commands]

        options.append(questionary.Choice("Cancel"))
        options.append(questionary.Separator())

        selected = questionary.select(
            f"Commands for '{selected_entry.query}'",
            choices=options,
            use_shortcuts=True,
            style=style,
        ).ask()

        if selected != "Cancel" and selected is not None:
            try:
                pyperclip.copy(selected.command)
                print("")
                if selected.dangerous_explanation:
                    rprint(f"[red]⚠️ Warning: {selected.dangerous_explanation}[/red]\n")
                rprint("[green]✓[/green] Copied to clipboard")
            except pyperclip.PyperclipException as e:
                rprint(
                    f"[red]Could not copy to clipboard: {e} (the clipboard may not work at all if you are running over SSH)[/red]"
                )
                rprint("[cyan]Here is your command:[/cyan]")
                print(selected.command)


history = History()
