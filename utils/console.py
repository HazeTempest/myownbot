import asyncio
import discord
from colorama import Fore, Style, init

# Initialize colorama
init()

# Global variable for auto-delete delay (in seconds)
AUTO_DELETE_DELAY = 2  # You can change this value

async def delete_command_message(ctx):
    """Delete the user's command message after a delay."""
    await asyncio.sleep(AUTO_DELETE_DELAY)
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Message already deleted: {ctx.message.content}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to delete message: {e}")

def print_color(color, text):
    """Print colored text."""
    print(color + text + Style.RESET_ALL)

def print_cmd(text):
    """Print a command-related message."""
    print(f"{Style.NORMAL}{Fore.WHITE}[{get_formatted_time()}] {Fore.LIGHTBLUE_EX}{Style.BRIGHT}[COMMAND]{Style.RESET_ALL} {text}")

def print_info(text):
    """Print an info message."""
    print(f"{Style.NORMAL}{Fore.WHITE}[{get_formatted_time()}] {Fore.LIGHTGREEN_EX}{Style.BRIGHT}[INFO]{Style.RESET_ALL} {text}")

def print_error(text):
    """Print an error message."""
    print(f"{Style.NORMAL}{Fore.WHITE}[{get_formatted_time()}] {Fore.LIGHTRED_EX}{Style.BRIGHT}[ERROR]{Style.RESET_ALL} {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Style.NORMAL}{Fore.WHITE}[{get_formatted_time()}] {Fore.LIGHTYELLOW_EX}{Style.BRIGHT}[WARNING]{Style.RESET_ALL} {text}")

def get_formatted_time():
    """Get the current time in a formatted string."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")