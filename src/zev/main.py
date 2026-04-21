import sys

import dotenv
from rich import print as rprint
from rich.console import Console

from zev.command_history import CommandHistory
from zev.command_selector import show_options
from zev.config import config
from zev.config.setup import run_setup
from zev.llms.llm import get_inference_provider
from zev.paths import get_config_path, migrate_legacy_files
from zev.update_check import check_for_updates_in_background, get_update_message
from zev.utils import get_env_context, get_input_string, show_help

command_history = CommandHistory()


def setup():
    run_setup()


def get_options(words: str):
    context = get_env_context()
    console = Console()
    rprint(f"")
    inference_provider = get_inference_provider()
    with console.status(
        f"[bold blue]Thinking... [grey39](running query using {inference_provider.model} via {config.llm_provider} backend)",
        spinner="dots",
    ):
        response = inference_provider.get_options(prompt=words, context=context)
        command_history.save_options(words, response)

    if response is None:
        return

    if not response.is_valid:
        print(response.explanation_if_not_valid)
        return

    if not response.commands:
        print("No commands available")
        return

    show_options(response.commands)


def run_no_prompt():
    input = get_input_string("input", "Describe what you want to do:", required=False, help_text="(-h for help)")
    if handle_special_case(input):
        return
    get_options(input)


def handle_special_case(args):
    if not args:
        return False

    if isinstance(args, str):
        args = args.split()

    if len(args) > 1:
        return False

    command = args[0].lower()

    if command == "--setup" or command == "-s":
        setup()
        return True

    if command == "--version" or command == "-v":
        from importlib.metadata import version
        print(f"zev version: {version('zev')}")
        return True

    if command == "--recent" or command == "-r":
        command_history.show_history()
        return True

    if command == "--help" or command == "-h":
        show_help()
        return True

    return False


def app():
    migrate_legacy_files()
    check_for_updates_in_background()

    update_msg = get_update_message()
    if update_msg:
        rprint(update_msg)

    config_path = get_config_path()
    args = [arg.strip() for arg in sys.argv[1:]]

    if not config_path.exists():
        run_setup()
        config.reload()
        print("Setup complete...\n")
        if len(args) == 1 and args[0] == "--setup":
            return

    if handle_special_case(args):
        return

    dotenv.load_dotenv(config_path, override=True)
    config.reload()

    if not args:
        run_no_prompt()
        return

    # Strip any trailing question marks from the input
    query = " ".join(args).rstrip("?")
    get_options(query)


if __name__ == "__main__":
    app()
