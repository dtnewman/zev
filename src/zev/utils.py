import os
import platform


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
