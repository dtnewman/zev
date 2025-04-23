from dataclasses import dataclass
import dotenv
import os
import platformdirs
import pyperclip
import questionary
from rich import print as rprint
from rich.console import Console
import sys

from zev.constants import DEFAULT_OPENAI_BASE_URL, DEFAULT_OPENAI_MODEL, DEFAULT_GEMINI_MODEL, DEFAULT_PROVIDER, LLMProvider
from zev.llm import get_options
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
        prompt="Enter your OpenAI base URL (for example, to use Ollama, enter http://localhost:11434/v1. Required if using OpenAI provider)",
        required=False,
        default=DEFAULT_OPENAI_BASE_URL,
    ),
    DotEnvField(
        name="OPENAI_MODEL",
        prompt="Enter your OpenAI model (required if using OpenAI provider)",
        required=False,
        default=DEFAULT_OPENAI_MODEL,
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
        default=DEFAULT_GEMINI_MODEL,
    ),
]


def setup():
    new_file = ""
    
    # First, get the LLM provider
    llm_provider_field = next(field for field in DOT_ENV_FIELDS if field.name == "LLM_PROVIDER")
    provider = get_input_string(
        llm_provider_field.name, 
        llm_provider_field.prompt, 
        llm_provider_field.default, 
        llm_provider_field.required
    ).lower()
    new_file += f"{llm_provider_field.name}={provider}\n"
    
    # Then, show only the relevant fields based on the selected provider
    for field in DOT_ENV_FIELDS:
        # Skip the provider field as we've already handled it
        if field.name == "LLM_PROVIDER":
            continue
            
        # Skip OpenAI fields if Gemini is selected
        if provider == LLMProvider.GEMINI and field.name.startswith("OPENAI_"):
            new_file += f"{field.name}=\n"  # Add empty value to maintain the field
            continue
            
        # Skip Gemini fields if OpenAI is selected
        if provider == LLMProvider.OPENAI and field.name.startswith("GEMINI_"):
            new_file += f"{field.name}=\n"  # Add empty value to maintain the field
            continue
            
        # For the selected provider, prompt for the field value
        new_value = get_input_string(field.name, field.prompt, field.default, field.required)
        new_file += f"{field.name}={new_value}\n"

    # Create the app data directory if it doesn't exist
    app_data_dir = platformdirs.user_data_dir("zev")
    os.makedirs(app_data_dir, exist_ok=True)

    # Write the new .env file
    with open(os.path.join(app_data_dir, ".env"), "w") as f:
        f.write(new_file)


def show_options(words: str):
    context = get_env_context()
    console = Console()
    with console.status("[bold blue]Thinking...", spinner="dots"):
        response = get_options(prompt=words, context=context)
    if response is None:
        return

    if not response.is_valid:
        print(response.explanation_if_not_valid)
        return

    if not response.commands:
        print("No commands available")
        return

    options = [questionary.Choice(cmd.command, description=cmd.short_explanation) for cmd in response.commands]
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
        pyperclip.copy(selected)
        rprint("\n[green]✓[/green] Copied to clipboard")


def run_no_prompt():
    input = get_input_string("input", "Describe what you want to do", "", False)
    show_options(input)


def app():
    # check if .env exists or if setting up again
    app_data_dir = platformdirs.user_data_dir("zev")
    args = [arg.strip() for arg in sys.argv[1:]]
    
    if not os.path.exists(os.path.join(app_data_dir, ".env")):
        setup()
        print("Setup complete...\n")
        if len(args) == 1 and args[0] == "--setup":
            return
    elif len(args) == 1 and args[0] == "--setup":
        dotenv.load_dotenv(os.path.join(app_data_dir, ".env"), override=True)
        setup()
        print("Setup complete...\n")
        return
    elif len(args) == 1 and args[0] == "--version":
        print(f"zev version: 0.3.1")
        return

    # important: make sure this is loaded before actually running the app (in regular or interactive mode)
    dotenv.load_dotenv(os.path.join(app_data_dir, ".env"), override=True)

    if not args:
        run_no_prompt()
        return

    # Strip any trailing question marks from the input
    query = " ".join(args).rstrip("?")
    show_options(query)


if __name__ == "__main__":
    app()
