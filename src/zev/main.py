import dotenv
from pathlib import Path
import sys

from zev.config.setup import run_setup
from zev.constants import CONFIG_FILE_NAME, VERSION
from zev.llms.llm import get_inference_provider
from zev.utils import get_env_context, show_help
from zev.history.history import history
from zev.ui.cli import cli


def setup():
    run_setup()


def show_history():
    response_history = history.get_history()
    if not response_history:
        print("No command history found")
        return

    history_items = list(response_history.keys())
    
    while True:
        selected_query = cli.display_history_options(history_items)
        
        if selected_query in (None, "Cancel"):
            return

        selected = cli.display_command_options(response_history[selected_query].commands, f"Commands for '{selected_query}'", history=True)

        if selected == "_back":
            continue
        elif selected != "Cancel" and selected is not None:
            cli.copy_to_clipboard(selected)
            return
        else:
            return


def show_options(words: str):
    context = get_env_context()
    
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
    input = cli.get_input_with_hint("Describe what you want to do:", "(-h for help)")
    if handle_cli_args(input):
        return
    show_options(input)
    

def handle_cli_args(args):
    if not args:
        return False
        
    if isinstance(args, str):
        args = args.split()
        
    if len(args) > 1:
        return False
    
    command = args[0].lower()
    
    if command in ("--setup"):
        setup()
        return True
    
    if command in ("--version"):
        print(f"zev version: {VERSION}")
        return True
    
    if command in ("--last", "-l"):
        show_history()
        return True
    
    if command in ("--help", "-h"):
        show_help()
        return True
        
    return False


def app():
    # check if .zevrc exists or if setting up again
    config_path = Path.home() / CONFIG_FILE_NAME
    args = [arg.strip() for arg in sys.argv[1:]]

    if not config_path.exists():
        run_setup()
        print("Setup complete...\n")
        if len(args) == 1 and args[0] == "--setup":
            return
        
    if handle_cli_args(args):
        return
    
    dotenv.load_dotenv(config_path, override=True)

    if not args:
        run_no_prompt()
        return

    # Strip any trailing question marks from the input
    query = " ".join(args).rstrip("?")
    show_options(query)


if __name__ == "__main__":
    app()
