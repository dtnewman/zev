import os
import platform
import json
import platformdirs
from typing import Optional

from zev.llm import Command


def get_input_string(
    field_name: str,
    prompt: str,
    default: str = "",
    required: bool = False,
) -> str:
    if default:
        prompt = f"{prompt} (default: {default})"
    else:
        prompt = f"{prompt}"

    # ANSI escape code for green color (#98c379)
    green_color = "\033[38;2;152;195;121m"
    reset_color = "\033[0m"

    value = input(f"{green_color}{prompt}{reset_color}: ") or default
    if required and not value:
        print(f"{field_name} is required, please try again")
        return get_input_string(field_name, prompt, default, required)

    return value or default


def get_env_context() -> str:
    os_name = platform.platform(aliased=True)
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC")
    return f"OS: {os_name}\nSHELL: {shell}" if shell else f"OS: {os_name}"


def save_last_options(commands: list[Command]):
    app_data_dir = platformdirs.user_data_dir("zev")
    os.makedirs(app_data_dir, exist_ok=True)
    last_options_file = os.path.join(app_data_dir, "last_options.json")
    
    options_data = [
        {
            "command": cmd.command,
            "short_explanation": cmd.short_explanation
        }
        for cmd in commands
    ]
    
    with open(last_options_file, "w") as f:
        json.dump(options_data, f)


def get_last_options() -> Optional[list[Command]]:
    app_data_dir = platformdirs.user_data_dir("zev")
    last_options_file = os.path.join(app_data_dir, "last_options.json")
    
    if not os.path.exists(last_options_file):
        return None
        
    try:
        with open(last_options_file, "r") as f:
            options_data = json.load(f)
            
        return [
            Command(
                command=opt["command"],
                short_explanation=opt["short_explanation"]
            )
            for opt in options_data
        ]
    except (json.JSONDecodeError, KeyError):
        return None
   
