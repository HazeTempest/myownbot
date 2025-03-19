import os
from discord.ext import commands
from dotenv import load_dotenv
from utils import console

# bot.py, commands, utils will be updated at later time (never)

# Load environment variables
load_dotenv()

# Set up the bot with dynamic prefix
bot = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX'), self_bot=True, help_command=None)

# Load command modules
async def load_cogs():
    await bot.load_extension("commands.google_sheets")
    await bot.load_extension("commands.utility")  # Load utility cog

# Log when the bot connects
@bot.event
async def on_ready():
    # Format the "Logged in as" message
    text = f"Logged in as {bot.user.name}"
    if str(bot.user.discriminator) != "0":  # Check if discriminator exists and is not "0"
        text += f"#{bot.user.discriminator}"
    
    console.print_info(text)
    console.print_info(f"You can now use commands with {os.getenv('DISCORD_BOT_PREFIX')}")

# Run the bot
async def main():
    try:
        await load_cogs()
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))
    except Exception as e:
        console.print_error(f"An error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())