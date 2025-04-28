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
from zev.constants import OPENAI_BASE_URL, OPENAI_DEFAULT_MODEL, CONFIG_FILE_NAME, DEFAULT_PROVIDER, GEMINI_DEFAULT_MODEL
from zev.llms.llm import get_inference_provider
from zev.utils import get_env_context, get_input_string


@dataclass
class DotEnvField:
    name: str
    prompt: str
    required: bool = True
    default: str = ""


DOT_ENV_FIELDS = [
    DotEnvField(
        name="LLM_PROVIDER",
        prompt="Enter your LLM provider (openai or gemini)",
        required=True,
        default=DEFAULT_PROVIDER,
    ),
    DotEnvField(
        name="OPENAI_API_KEY",
        prompt="Enter your OpenAI API key (required if using OpenAI provider)",
        required=False,
        default=os.getenv("OPENAI_API_KEY", ""),
    ),
    DotEnvField(
        name="OPENAI_BASE_URL",
        prompt="Enter your OpenAI base URL (for example, to use Ollama, enter http://localhost:11434/v1. If you don't know what this is, just press enter)",
        required=False,
        default=OPENAI_BASE_URL,
    ),
    DotEnvField(
        name="OPENAI_MODEL",
        prompt="Enter your OpenAI model",
        required=False,
        default=OPENAI_DEFAULT_MODEL,
    ),
    DotEnvField(
        name="GEMINI_API_KEY",
        prompt="Enter your Gemini API key (required if using Gemini provider)",
        required=False,
        default=os.getenv("GEMINI_API_KEY", ""),
    ),
    DotEnvField(
        name="GEMINI_MODEL",
        prompt="Enter your Gemini model (required if using Gemini provider)",
        required=False,
        default=GEMINI_DEFAULT_MODEL,
    ),
]


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

    options = [questionary.Choice(cmd.command, description=cmd.short_explanation, value=cmd) for cmd in response.commands]
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
        pyperclip.copy(selected.command)
        print("")
        if selected.dangerous_explanation:
            rprint(f"[red]⚠️ Warning: {selected.dangerous_explanation}[/red]\n")
        rprint("[green]✓[/green] Copied to clipboard")


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
