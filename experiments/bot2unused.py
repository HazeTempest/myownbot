import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load the .env file and get the token from it
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Set up intents (required by discord TOS)
intents = discord.Intents.default()
intents.message_content = True  # Enable access to message content

# Create the bot instance with a command prefix (not used for slash commands)
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        # Sync slash commands with Discord
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Slash command: /ping
@bot.tree.command(name="ping", description="Responds with Pong! 🏓")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

# Slash command: /gsreminder
@bot.tree.command(name="gsreminder", description="Reminds specific users to do their GS runs with a timestamp.")
@app_commands.describe(users="The users to remind, separated by spaces.")
async def gsreminder(interaction: discord.Interaction, users: str):
    # Parse the users input into a list of mentions
    user_list = users.split()  # Split the input by spaces
    mentions = " ".join([f"<@{user.strip('<>@! ')}>" for user in user_list])  # Convert to mentions

    # Get today's date at 4 PM
    now = datetime.now()
    today_4pm = now.replace(hour=16, minute=0, second=0, microsecond=0)

    # If it's already past 4 PM, set the timestamp for 4 PM tomorrow
    if now > today_4pm:
        today_4pm += timedelta(days=1)

    # Convert to Unix timestamp
    unix_timestamp = int(today_4pm.timestamp())

    # Send the message with the timestamp and user mentions
    await interaction.response.send_message(f"{mentions} Please do your GS runs. Reset <t:{unix_timestamp}:R>")

# Event: When a message is sent
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Respond to "$ping" even if it's in the middle of a sentence
    if "$ping" in message.content.lower():
        await message.channel.send("Pong! 🏓")

    # Respond to "$hello"
    if message.content.lower() == "$hello":
        await message.channel.send("Hello!")

    # Process commands (required for other commands if using commands.Bot)
    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)