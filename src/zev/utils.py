import os
import platform


def get_input_string(
    field_name: str,
    prompt: str,
    default: str = "",
    required: bool = False,
    help_text: str = "",
) -> str:
    if default:
        prompt = f"{prompt} (default: {default})"
    else:
        prompt = f"{prompt}"

    # ANSI escape code for green color (#98c379)
    green_color = "\033[38;2;152;195;121m"
    gray_color = "\033[38;2;100;100;100m"
    reset_color = "\033[0m"

    if help_text:
        formatted_prompt = f"{green_color}{prompt} {gray_color}{help_text}{reset_color}"
    else:
        formatted_prompt = f"{green_color}{prompt}{reset_color}"

    value = input(f"{formatted_prompt} ") or default
    if required and not value:
        print(f"{field_name} is required, please try again")
        return get_input_string(field_name, prompt, default, required, help_text)

    return value or default


def get_env_context() -> str:
    os_name = platform.platform(aliased=True)
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC")
    return f"OS: {os_name}\nSHELL: {shell}" if shell else f"OS: {os_name}"


def show_help():
    print("""
Zev is a simple CLI tool to help you remember terminal commands.

Usage:
zev [query]               Describe what you want to do
zev --help, -h            Show this help message
zev --past, -p            Show command history
zev --setup               Run setup again
zev --version             Show version information
""")
