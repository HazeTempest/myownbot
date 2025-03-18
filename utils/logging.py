import asyncio
import discord
from colorama import Fore, Style, init

# Initialize colorama
init()

async def delete_command_message(ctx):
    await asyncio.sleep(5)
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Message already deleted: {ctx.message.content}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to delete message: {e}")

def log_command_usage(ctx):
    params = " ".join([f"{k}: {v}" for k, v in ctx.kwargs.items()]) if ctx.kwargs else " ".join(ctx.args[1:])
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Used command: {ctx.command.name} {params}")