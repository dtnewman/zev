import sys
from pathlib import Path
from subprocess import run as run_command

import dotenv
import pyperclip
import questionary
from rich import print as rprint
from rich.console import Console

from zev.config.setup import run_setup
from zev.constants import CONFIG_FILE_NAME
from zev.llms.llm import get_inference_provider
from zev.utils import get_env_context, get_input_string


def setup():
    run_setup()


def show_options(words: str):
    context = get_env_context()
    console = Console()
    with console.status("[bold blue]Thinking...", spinner="dots"):
        inference_provider = get_inference_provider()
        response = inference_provider.get_options(prompt=words, context=context)
    if response is None:
        return

    if not response.is_valid:
        print(response.explanation_if_not_valid)
        return

    if not response.commands:
        print("No commands available")
        return

    options = [
        questionary.Choice(cmd.command, description=cmd.short_explanation, value=cmd) for cmd in response.commands
    ]
    options.append(questionary.Choice("Cancel"))
    options.append(questionary.Separator())

    selected = questionary.select(
        "Select command:",
        choices=options,
        use_shortcuts=True,
        style=questionary.Style(
            [
                ("answer", "fg:#61afef"),
                ("question", "bold"),
                ("instruction", "fg:#98c379"),
            ]
        ),
    ).ask()

    if selected != "Cancel":
        print("")
        if selected.dangerous_explanation:
            rprint(f"[red]⚠️ Warning: {selected.dangerous_explanation}[/red]\n")
        try:
            pyperclip.copy(selected.command)
            rprint("[green]✓[/green] Copied to clipboard")
        except pyperclip.PyperclipException as e:
            rprint(
                "[red]Could not copy to clipboard (see https://github.com/dtnewman/zev?tab=readme-ov-file#-dependencies)[/red]\n"
            )
            rprint("[cyan]Here is your command:[/cyan]")
            print(selected.command)
            if questionary.confirm("Would you like to run it?").ask():
                print("Running command:", selected.command)
                run_command(selected.command, shell=True)


def run_no_prompt():
    user_input = get_input_string("input", "Describe what you want to do", "", False)
    show_options(user_input)


def app():
    # check if .zevrc exists or if setting up again
    config_path = Path.home() / CONFIG_FILE_NAME
    args = [arg.strip() for arg in sys.argv[1:]]

    if not config_path.exists():
        run_setup()
        print("Setup complete...\n")
        if len(args) == 1 and args[0] == "--setup":
            return
    elif len(args) == 1 and args[0] == "--setup":
        dotenv.load_dotenv(config_path, override=True)
        run_setup()
        print("Setup complete...\n")
        return
    elif len(args) == 1 and args[0] == "--version":
        print("zev version: 0.7.1")
        return

    # important: make sure this is loaded before actually running the app (in regular or interactive mode)
    dotenv.load_dotenv(config_path, override=True)

    if not args:
        run_no_prompt()
        return

    # Strip any trailing question marks from the input
    query = " ".join(args).rstrip("?")
    show_options(query)


if __name__ == "__main__":
    app()
