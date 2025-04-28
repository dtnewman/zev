from dataclasses import dataclass
import dotenv
import os
from pathlib import Path
import sys

from zev.config.setup import run_setup
from zev.constants import OPENAI_BASE_URL, OPENAI_DEFAULT_MODEL, CONFIG_FILE_NAME, EDIT_PROMPT
from zev.llms.llm import get_inference_provider
from zev.utils import get_env_context, get_input_string
from zev.history import history
from zev.ui.cli import cli


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


def show_last_commands():
    response_history = history.get_history()
    if not response_history:
        print("No command history found")
        return

    history_items = list(response_history.keys())
    
    selected_query = cli.display_history_options(history_items)
    
    if selected_query in (None, "Cancel"):
        return

    selected = cli.display_command_options(response_history[selected_query].commands, f"Commands for '{selected_query}'")

    if selected != "Cancel" and selected is not None:
        cli.copy_to_clipboard(selected)


def show_options(words: str):
    context = get_env_context()
    
    if words.lower() == "last":
        show_last_commands()
        return
    
    def generate_response():
        inference_provider = get_inference_provider()
        response = inference_provider.get_options(prompt=words, context=context)
        history.save_options(words, response)
        return response
    
    response = cli.display_thinking_status(generate_response)
            
    if response is None:
        return

    if not response.is_valid:
        print(response.explanation_if_not_valid)
        return

    if not response.commands:
        print("No commands available")
        return

    selected = cli.display_command_options(response.commands, "Select command:")

    if selected != "Cancel" and selected is not None:
        cli.copy_to_clipboard(selected)


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
