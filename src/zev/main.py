import dotenv
from pathlib import Path
import pyperclip
import questionary
from rich import print as rprint
from rich.console import Console
import sys

from zev.config.setup import run_setup
from zev.constants import CONFIG_FILE_NAME
from zev.llms.llm import get_inference_provider
from zev.utils import get_env_context, show_help, get_input_string
from zev.history.history import history


def setup():
    run_setup()


def show_options(words: str):
    context = get_env_context()
    console = Console()
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
            rprint(f"[red]Could not copy to clipboard: {e} (the clipboard may not work at all if you are running over SSH)[/red]")
            rprint("[cyan]Here is your command:[/cyan]")
            print(selected.command)


def run_no_prompt():
    input = get_input_string("input", "Describe what you want to do:", required=False, help_text="(-h for help)")
    if handle_args(input):
        return
    show_options(input)
    

def display_history_options(history_entries, show_limit=5):
    if not history_entries:
        print("No command history found")
        return None
    
    style = questionary.Style([
        ("answer", "fg:#61afef"),
        ("question", "bold"),
        ("instruction", "fg:#98c379"),
    ])
        
    query_options = [
        questionary.Choice(query, value=query) 
        for query in list(history_entries.keys())[:show_limit]
    ]
    
    if len(history_entries) > show_limit: 
        query_options.append(
            questionary.Choice("Show more...", value="show_more")
        )
    
    query_options.append(questionary.Separator())
    query_options.append(questionary.Choice("Cancel"))
    
    selected = questionary.select(
        "Select from history:",
        choices=query_options,
        use_shortcuts=True,
        style=style
    ).ask()
    
    if selected == "show_more":
        all_options = [
            questionary.Choice(query, value=query) 
            for query in history_entries.keys()
        ]
        all_options.append(questionary.Separator())
        all_options.append(questionary.Choice("Cancel"))
        
        return questionary.select(
            "Select from history (showing all items):",
            choices=all_options,
            use_shortcuts=True,
            style=style
        ).ask()
        
    return selected


def show_history():
    history_entries = history.get_history() 
    if not history_entries:
        print("No command history found")
        return
    
    selected_query = display_history_options(history_entries)
    
    if selected_query in (None, "Cancel"):
        return
    
    commands = history_entries[selected_query].response.commands

    if not commands:
        print("No commands available")
        return None

    style = questionary.Style([
        ("answer", "fg:#61afef"),
        ("question", "bold"),
        ("instruction", "fg:#98c379"),
    ])

    options = [
        questionary.Choice(
            cmd.command, 
            description=cmd.short_explanation, 
            value=cmd
        ) for cmd in commands
    ]
        
    options.append(questionary.Choice("Cancel"))
    options.append(questionary.Separator())
    
    selected = questionary.select(
        f"Commands for '{selected_query}'",
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
            rprint(f"[red]Could not copy to clipboard: {e} (the clipboard may not work at all if you are running over SSH)[/red]")
            rprint("[cyan]Here is your command:[/cyan]")
            print(selected.command)


def handle_args(args):
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
        print(f"zev version: 0.6.2")
        return True
    
    if command in ("--past", "-p"):
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
        
    if handle_args(args):
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
