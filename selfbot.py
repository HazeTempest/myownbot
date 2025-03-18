import os
import discord
import dotenv
from discord.ext import commands
from datetime import datetime, timedelta

# Load the .env file and get the token from it
dotenv.load_dotenv()
TOKEN = os.getenv('TOKENALT')
PREFIX = os.getenv('PREFIX')

# Create the bot instance with a command prefix
bot = commands.Bot(command_prefix=PREFIX)

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Prefix command: ping
@bot.command(name="ping", description="Responds with Pong! 🏓")
async def ping(ctx: commands.Context):
    await ctx.send("Pong! 🏓")

# Prefix command: resetping
@bot.command(name="resetping", description="Reminds specific users of daily reset with a timestamp.")
async def resetping(ctx: commands.Context, *users: str):
    # Check if no users were provided
    if not users:
        await ctx.send("Please mention users to remind!")
        return

    # List to store valid user mentions
    mentions = []

    # Loop through each user input
    for user_input in users:
        # Check if the input is a mention (e.g., <@123456789012345678>)
        if user_input.startswith("<@") and user_input.endswith(">"):
            mentions.append(user_input)  # Directly add the mention
        else:
            # Try to find the user by name in the guild
            user = discord.utils.get(ctx.guild.members, name=user_input)
            if user:
                mentions.append(f"<@{user.id}>")  # Convert to mention
            else:
                await ctx.send(f"User '{user_input}' not found!")
                return

    # Get today's date at 4 PM
    now = datetime.now()
    today_4pm = now.replace(hour=16, minute=0, second=0, microsecond=0)

    # If it's already past 4 PM, set the timestamp for 4 PM tomorrow
    if now > today_4pm:
        today_4pm += timedelta(days=1)

    # Convert to Unix timestamp
    unix_timestamp = int(today_4pm.timestamp())

    # Send the message with the timestamp and user mentions
    await ctx.send(f"{' '.join(mentions)} Please do your GS runs. Reset <t:{unix_timestamp}:R>")

# Event: When a message is sent
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author != bot.user:
        return

    # Respond to "$ping" even if it's in the middle of a sentence
    if "$ping" in message.content.lower():
        await message.channel.send("Pong! 🏓")

    # Respond to "$hello"
    if message.content.lower() == "$hello":
        await message.channel.send("Hello!")

    # Ensure commands are processed
    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)