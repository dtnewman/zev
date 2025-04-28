import questionary
from rich import print as rprint
from rich.console import Console
import pyperclip


class CLI:
    """Handles CLI user interface interactions"""
    
    def __init__(self):
        self.console = Console()
        self.style = questionary.Style([
            ("answer", "fg:#61afef"),
            ("question", "bold"),
            ("instruction", "fg:#98c379"),
        ])
    
    def get_text_input(self, prompt_text):
        """Get text input from user"""
        return questionary.text(
            prompt_text,
            style=self.style
        ).ask()
    
    def display_thinking_status(self, callback):
        """Display a thinking status while executing a callback"""
        with self.console.status("[bold blue]Thinking...", spinner="dots"):
            return callback()
    
    def display_command_options(self, commands, title="Select command:"):
        """Display command options and handle selection"""
        if not commands:
            print("No commands available")
            return None

        options = [
            questionary.Choice(
                cmd.command, 
                description=cmd.short_explanation, 
                value=cmd
            ) for cmd in commands
        ]
        
        options.append(questionary.Choice("Cancel"))
        options.append(questionary.Separator())
        
        return questionary.select(
            title,
            choices=options,
            use_shortcuts=True,
            style=self.style,
        ).ask()
    
    def display_history_options(self, history_items, show_limit=5):
        """Display history options and handle selection"""
        if not history_items:
            print("No command history found")
            return None
            
        query_options = [
            questionary.Choice(word, value=word) 
            for word in history_items[:show_limit]
        ]
        
        if len(history_items) > show_limit: 
            query_options.append(
                questionary.Choice("Show more...", value="show_more")
            )
        
        query_options.append(questionary.Separator())
        query_options.append(questionary.Choice("Cancel"))
        
        selected = questionary.select(
            "Select from history:",
            choices=query_options,
            use_shortcuts=True,
            style=self.style
        ).ask()
        
        if selected == "show_more":
            all_options = [
                questionary.Choice(word, value=word) 
                for word in history_items
            ]
            all_options.append(questionary.Separator())
            all_options.append(questionary.Choice("Cancel"))
            
            return questionary.select(
                "Select from history (showing all items):",
                choices=all_options,
                use_shortcuts=True,
                style=self.style
            ).ask()
            
        return selected
    
    def copy_to_clipboard(self, command):
        """Copy a command to clipboard and notify user"""
        pyperclip.copy(command.command)
        print("")
        if command.dangerous_explanation:
            rprint(
                f"[red]⚠️ Warning: {command.dangerous_explanation}[/red]\n"
            )
        rprint("[green]✓[/green] Copied to clipboard") 
        
        
cli = CLI()