import os
import discord
from discord.ext import commands
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

# Authenticate with Google Sheets API
def authenticate_google_sheets():
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client

# Get data from a specific range in the sheet
def get_sheet_data(range):
    # Authenticate
    client = authenticate_google_sheets()

    # Open the spreadsheet and worksheet
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheet_name = os.getenv('SHEET_NAME')
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)

    # Get the data from the specified range
    data = worksheet.get(range)
    return data

# Write data to a specific cell in the sheet
def write_to_cell(cell, value):
    # Authenticate
    client = authenticate_google_sheets()

    # Open the spreadsheet and worksheet
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheet_name = os.getenv('SHEET_NAME')
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)

    # Update the specified cell with the value
    worksheet.update_acell(cell, value)

# Set up the Discord bot
bot = commands.Bot(command_prefix="!", self_bot=True)

# Command to read a specific range from the sheet
@bot.command(name="readsheet")
async def read_sheet(ctx, range):
    try:
        data = get_sheet_data(range)
        
        # Format the data into a readable string
        formatted_data = "\n".join([" | ".join(row) for row in data])
        
        # Create an embed
        embed = discord.Embed(
            title=f"Data from Range `{range}`",
            description=f"```\n{formatted_data}\n```",
            color=discord.Color.blue()  # You can change the color
        )

        # Handle avatar (custom or default)
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=avatar_url)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# Command to write to a specific cell in the sheet
@bot.command(name="writesheet")
async def write_sheet(ctx, cell: str, *, value: str):
    try:
        # Write the value to the specified cell
        write_to_cell(cell, value)
        await ctx.send(f"Successfully wrote `{value}` to cell `{cell}`.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# Run the bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))