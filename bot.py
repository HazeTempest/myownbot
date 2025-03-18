import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import console  # Import the entire console module

# Load environment variables
load_dotenv()

# Set up the bot (disable the default help command)
bot = commands.Bot(command_prefix="!", self_bot=True, help_command=None)

# Load command modules
async def load_cogs():
    await bot.load_extension("commands.google_sheets")
    await bot.load_extension("commands.utility")

# Log when the bot is ready
@bot.event
async def on_ready():
    console.clear()
    console.resize(columns=90, rows=25)
    console.print_info(f"Logged in as {bot.user.name}#{bot.user.discriminator}")
    console.print_info(f"You can now use commands with !")

# Run the bot
async def main():
    await load_cogs()
    await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())