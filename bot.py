import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the bot
bot = commands.Bot(command_prefix="!", self_bot=True)

# Load command modules
bot.load_extension("commands.google_sheets")
bot.load_extension("commands.utility")

# Log when the bot is ready
@bot.event
async def on_ready():
    print(f"[INFO] Logged in as {bot.user} (ID: {bot.user.id})")

# Run the bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))