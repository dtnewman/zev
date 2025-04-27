from dataclasses import dataclass
import dotenv
import os
from pathlib import Path
import pyperclip
import questionary
from rich import print as rprint
from rich.console import Console
import sys

from zev.config.setup import run_setup
from zev.constants import OPENAI_BASE_URL, OPENAI_DEFAULT_MODEL, CONFIG_FILE_NAME
from zev.llms.llm import get_inference_provider
from zev.utils import get_env_context, get_input_string
from zev.history import history

@dataclass
class DotEnvField:
    name: str
    prompt: str
    required: bool = True
    default: str = ""


DOT_ENV_FIELDS = [
    DotEnvField(
        name="OPENAI_API_KEY",
        prompt="Enter your OpenAI API key",
        required=False,
        default=os.getenv("OPENAI_API_KEY", ""),
    ),
    DotEnvField(
        name="OPENAI_BASE_URL",
        prompt="Enter your OpenAI base URL (for example, to use Ollama, enter http://localhost:11434/v1. If you don't know what this is, just press enter)",
        required=True,
        default=OPENAI_BASE_URL,
    ),
    DotEnvField(
        name="OPENAI_MODEL",
        prompt="Enter your OpenAI model",
        required=True,
        default=OPENAI_DEFAULT_MODEL,
    ),
]


def setup():
    run_setup()


def display_command_options(commands, title="Select command:"):
    """Common function to display command options and handle selection."""
    if not commands:
        print("No commands available")
        return

    options = [questionary.Choice(cmd.command, description=cmd.short_explanation, value=cmd) for cmd in commands]

    options.append(questionary.Choice("Cancel"))
    options.append(questionary.Separator())

    selected = questionary.select(
        title,
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
        pyperclip.copy(selected.command)
        print("")
        if selected.dangerous_explanation:
            rprint(f"[red]⚠️ Warning: {selected.dangerous_explanation}[/red]\n")
        rprint("[green]✓[/green] Copied to clipboard")


def show_last_commands():
    response_history = history.get_history()
    if not response_history:
        print("No command history found")
        return

    query_options = [questionary.Choice(word, value=word) for word in response_history.keys()]

    if not query_options:
        print("No command history found")
        return

    query_options.append(questionary.Choice("Cancel"))
    query_options.append(questionary.Separator())

    selected_query = questionary.select(
        "Select from history:",
        choices=query_options,
        use_shortcuts=True,
        style=questionary.Style([
            ("answer", "fg:#61afef"),
            ("question", "bold"),
            ("instruction", "fg:#98c379"),
        ])
    ).ask()

    if selected_query == "Cancel":
        return

    display_command_options(
        response_history[selected_query].commands,
        f"Commands for '{selected_query}':"
    )


def show_options(words: str):
    context = get_env_context()
    console = Console()
    
    if words.lower() == "last":
        show_last_commands()
        return
            
    with console.status("[bold blue]Thinking...", spinner="dots"):
        inference_provider = get_inference_provider()
        response = inference_provider.get_options(prompt=words, context=context)
        history.save_options(words, response)
    if response is None:
        return

    if not response.is_valid:
        print(response.explanation_if_not_valid)
        return

    if not response.commands:
        print("No commands available")
        return

    display_command_options(response.commands, "Select command:")


def run_no_prompt():
    input = get_input_string("input", "Describe what you want to do", "", False)
    show_options(input)


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
        print(f"zev version: 0.5.3")
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
