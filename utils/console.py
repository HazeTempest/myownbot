import os
import sys
import colorama
from datetime import datetime

# Initialize colorama
colorama.init()

def clear():
    """Clear the console."""
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

def resize(columns, rows):
    """Resize the console."""
    if sys.platform == "win32":
        os.system(f"mode con cols={columns} lines={rows}")
    else:
        os.system(f"echo '\033[8;{rows};{columns}t'")

def get_formatted_time():
    """Get the current time in a formatted string."""
    return datetime.now().strftime("%H:%M:%S")

def print_color(color, text):
    """Print colored text."""
    print(color + text + colorama.Style.RESET_ALL)

def print_cmd(text):
    """Print a command-related message."""
    print(f"{colorama.Style.NORMAL}{colorama.Fore.WHITE}[{get_formatted_time()}] {colorama.Fore.LIGHTBLUE_EX}{colorama.Style.BRIGHT}[COMMAND]{colorama.Style.RESET_ALL} {text}")

def print_info(text):
    """Print an info message."""
    print(f"{colorama.Style.NORMAL}{colorama.Fore.WHITE}[{get_formatted_time()}] {colorama.Fore.LIGHTGREEN_EX}{colorama.Style.BRIGHT}[INFO]{colorama.Style.RESET_ALL} {text}")

def print_success(text):
    """Print a success message."""
    print(f"{colorama.Style.NORMAL}{colorama.Fore.WHITE}[{get_formatted_time()}] {colorama.Fore.LIGHTGREEN_EX}{colorama.Style.BRIGHT}[SUCCESS]{colorama.Style.RESET_ALL} {text}")

def print_error(text):
    """Print an error message."""
    print(f"{colorama.Style.NORMAL}{colorama.Fore.WHITE}[{get_formatted_time()}] {colorama.Fore.LIGHTRED_EX}{colorama.Style.BRIGHT}[ERROR]{colorama.Style.RESET_ALL} {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"{colorama.Style.NORMAL}{colorama.Fore.WHITE}[{get_formatted_time()}] {colorama.Fore.LIGHTYELLOW_EX}{colorama.Style.BRIGHT}[WARNING]{colorama.Style.RESET_ALL} {text}")