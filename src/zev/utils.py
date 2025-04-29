import os
import platform


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
zev --last, -l            Show command history
zev --setup               Run setup again
zev --version             Show version information
""")