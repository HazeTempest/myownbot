import os
import discord
from discord.ext import commands
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import asyncio

# Load environment variables
load_dotenv()

# Authenticate with Google Sheets API
def authenticate_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv('GOOGLE_SHEETS_CREDENTIALS'),
        ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(creds)

# Get worksheet
def get_worksheet():
    client = authenticate_google_sheets()
    return client.open_by_key(os.getenv('SPREADSHEET_ID')).worksheet(os.getenv('SHEET_NAME'))

# Set up the Discord bot
bot = commands.Bot(command_prefix="!", self_bot=True)

# Auto-delete command message after 5 seconds
async def delete_command_message(ctx):
    await asyncio.sleep(5)  # Wait for 5 seconds
    await ctx.message.delete()

# Command to read a specific range from the sheet
@bot.command(name="readsheet")
async def read_sheet(ctx, range):
    try:
        data = get_worksheet().get(range)
        message = await ctx.send(f"Data from range `{range}`:\n```\n{' '.join([' '.join(row) for row in data])}\n```")
        await delete_command_message(ctx)  # Delete the command message
    except Exception as e:
        message = await ctx.send(f"An error occurred: {e}")
        await delete_command_message(ctx)  # Delete the command message

# Command to write to a specific cell in the sheet
@bot.command(name="writesheet")
async def write_sheet(ctx, cell: str, *, value: str):
    try:
        get_worksheet().update_acell(cell, value)
        message = await ctx.send(f"Successfully wrote `{value}` to cell `{cell}`.")
        await delete_command_message(ctx)  # Delete the command message
    except Exception as e:
        message = await ctx.send(f"An error occurred: {e}")
        await delete_command_message(ctx)  # Delete the command message

# Command to add a player's name and score
@bot.command(name="addscore")
async def add_score(ctx, player_name: str, score: int):
    try:
        worksheet = get_worksheet()
        # Find the next empty row in column A
        col_a = worksheet.col_values(1)  # Get all values in column A
        next_row = len(col_a) + 1  # Next empty row
        
        # Write player name in column A and score in the next available column
        worksheet.update_cell(next_row, 1, player_name)  # Column A
        worksheet.update_cell(next_row, 2, score)        # Column B (next column)
        
        message = await ctx.send(f"Added `{player_name}` with score `{score}` to row `{next_row}`.")
        await delete_command_message(ctx)  # Delete the command message
    except Exception as e:
        message = await ctx.send(f"An error occurred: {e}")
        await delete_command_message(ctx)  # Delete the command message

# Command to check bot latency
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000, 2)  # Latency in milliseconds
    message = await ctx.send(f"Pong! Latency is {latency}ms.")
    await delete_command_message(ctx)  # Delete the command message

# Command to delete a specified number of bot messages
@bot.command(name="delete")
async def delete_messages(ctx, number: int):
    try:
        # Fetch messages in the channel
        messages = []
        async for message in ctx.channel.history(limit=number + 1):  # +1 to include the command itself
            if message.author == bot.user:  # Only delete messages sent by the bot
                messages.append(message)
        
        # Delete the messages
        await ctx.channel.delete_messages(messages)
        await delete_command_message(ctx)  # Delete the command message
    except Exception as e:
        message = await ctx.send(f"An error occurred: {e}")
        await delete_command_message(ctx)  # Delete the command message

# Run the bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))