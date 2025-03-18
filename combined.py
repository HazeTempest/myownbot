import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import asyncio
from colorama import Fore, Style, init
from datetime import datetime, timedelta

# Initialize colorama
init()

# Load environment variables
load_dotenv()

# Global variable for auto-delete delay (in seconds)
AUTO_DELETE_DELAY = 2  # You can change this value

# Console utilities
class Console:
    @staticmethod
    async def delete_command_message(ctx):
        """Delete the user's command message after a delay."""
        await asyncio.sleep(AUTO_DELETE_DELAY)
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Message already deleted: {ctx.message.content}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to delete message: {e}")

    @staticmethod
    def print_cmd(text):
        """Print a command-related message."""
        print(f"{Style.NORMAL}{Fore.WHITE}[{Console.get_formatted_time()}] {Fore.LIGHTBLUE_EX}{Style.BRIGHT}[COMMAND]{Style.RESET_ALL} {text}")

    @staticmethod
    def print_info(text):
        """Print an info message."""
        print(f"{Style.NORMAL}{Fore.WHITE}[{Console.get_formatted_time()}] {Fore.LIGHTGREEN_EX}{Style.BRIGHT}[INFO]{Style.RESET_ALL} {text}")

    @staticmethod
    def print_error(text):
        """Print an error message."""
        print(f"{Style.NORMAL}{Fore.WHITE}[{Console.get_formatted_time()}] {Fore.LIGHTRED_EX}{Style.BRIGHT}[ERROR]{Style.RESET_ALL} {text}")

    @staticmethod
    def print_warning(text):
        """Print a warning message."""
        print(f"{Style.NORMAL}{Fore.WHITE}[{Console.get_formatted_time()}] {Fore.LIGHTYELLOW_EX}{Style.BRIGHT}[WARNING]{Style.RESET_ALL} {text}")

    @staticmethod
    def get_formatted_time():
        """Get the current time in a formatted string."""
        return datetime.now().strftime("%H:%M:%S")

# Google Sheets utilities
class Sheets:
    @staticmethod
    def authenticate_google_sheets():
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.getenv('GOOGLE_SHEETS_CREDENTIALS'),
            ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )
        return gspread.authorize(creds)

    @staticmethod
    def get_worksheet():
        client = Sheets.authenticate_google_sheets()
        return client.open_by_key(os.getenv('SPREADSHEET_ID')).worksheet(os.getenv('SHEET_NAME'))

# Set up the bot
bot = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX'), self_bot=True, help_command=None)

# Google Sheets commands
class GoogleSheets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="readsheet")
    async def read_sheet(self, ctx, range):
        try:
            data = Sheets.get_worksheet().get(range)
            formatted_data = "\n".join([" ".join(row) for row in data])  # Format each row on a new line
            await ctx.send(f"Data from range `{range}`:\n```\n{formatted_data}\n```")
            await Console.delete_command_message(ctx)  # Delete the command message
            Console.print_cmd(f"Used command: readsheet {range}")
        except Exception as e:
            Console.print_error(f"readsheet command failed: {e}")

    @commands.command(name="writesheet")
    async def write_sheet(self, ctx, cell: str, *, value: str):
        try:
            Sheets.get_worksheet().update_acell(cell, value)
            await ctx.send(f"Successfully wrote `{value}` to cell `{cell}`.")
            await Console.delete_command_message(ctx)  # Delete the command message
            Console.print_cmd(f"Used command: writesheet {cell} {value}")
        except Exception as e:
            Console.print_error(f"writesheet command failed: {e}")

    @commands.command(name="addscore")
    async def add_score(self, ctx, player_name: str, score: int):
        try:
            worksheet = Sheets.get_worksheet()
            col_a = worksheet.col_values(1)
            next_row = len(col_a) + 1
            worksheet.update_cell(next_row, 1, player_name)
            worksheet.update_cell(next_row, 2, score)
            await ctx.send(f"Added `{player_name}` with score `{score}` to row `{next_row}`.")
            await Console.delete_command_message(ctx)  # Delete the command message
            Console.print_cmd(f"Used command: addscore {player_name} {score}")
        except Exception as e:
            Console.print_error(f"addscore command failed: {e}")

# Utility commands
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        help_message = """
**Available Commands:**

- `!readsheet <range>`: Reads data from a range.
  Example: `!readsheet A1:B2`

- `!writesheet <cell> <value>`: Writes a value to a cell.
  Example: `!writesheet A1 Hello`

- `!addscore <player> <score>`: Adds a player's score.
  Example: `!addscore Haze 100`

- `!ping`: Checks the bot's latency.

- `!delete <number>`: Deletes bot messages.
  Example: `!delete 3`

- `!resetping <time> <users>`: Sends a reminder at the specified time.
  Example: `!resetping 16 @User1 User2`

- `!error`: Intentionally causes an error for testing.

- `!shutdown`: Shuts down the bot gracefully.
"""
        await ctx.send(help_message)
        await Console.delete_command_message(ctx)  # Delete the command message
        Console.print_cmd("Used command: help")

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000, 2)
        await ctx.send(f"Pong! Latency is {latency}ms.")
        await Console.delete_command_message(ctx)  # Delete the command message
        Console.print_cmd("Used command: ping")

    @commands.command(name="delete")
    async def delete_messages(self, ctx, number: int):
        try:
            messages = []
            async for message in ctx.channel.history(limit=number + 1):
                if message.author == self.bot.user:
                    messages.append(message)
            await ctx.channel.delete_messages(messages)
            await Console.delete_command_message(ctx)  # Delete the command message
            Console.print_cmd(f"Used command: delete {number}")
        except Exception as e:
            Console.print_error(f"delete command failed: {e}")

    @commands.command(name="resetping", description="Reminds specific users of daily reset with a timestamp.")
    async def resetping(self, ctx, time: int, *users: str):
        try:
            if not users:
                await ctx.send("Please mention users to remind!")
                return

            mentions = []
            for user_input in users:
                if user_input.startswith("<@") and user_input.endswith(">"):
                    mentions.append(user_input)
                else:
                    user = discord.utils.get(ctx.guild.members, name=user_input)
                    if user:
                        mentions.append(f"<@{user.id}>")
                    else:
                        await ctx.send(f"User '{user_input}' not found!")
                        return

            now = datetime.now()
            today_time = now.replace(hour=time, minute=0, second=0, microsecond=0)
            if now > today_time:
                today_time += timedelta(days=1)
            unix_timestamp = int(today_time.timestamp())

            await ctx.send(f"{' '.join(mentions)} Please do your GS runs. Reset <t:{unix_timestamp}:R>")
            await Console.delete_command_message(ctx)  # Delete the command message
            Console.print_cmd(f"Used command: resetping {time} {' '.join(users)}")
        except Exception as e:
            Console.print_error(f"resetping command failed: {e}")

    @commands.command(name="error")
    async def error_command(self, ctx):
        try:
            # Intentionally cause an error
            raise ValueError("This is a test error.")
        except Exception as e:
            Console.print_error(f"error command failed: {e}")
            await ctx.send(f"An error occurred: {e}")
            await Console.delete_command_message(ctx)

    @commands.command(name="shutdown")
    async def shutdown_command(self, ctx):
        """Shut down the bot gracefully."""
        await ctx.message.delete()  # Instantly delete the command message
        await ctx.send("Shutting down...", delete_after=0)  # Send and instantly delete the response
        Console.print_info("Shutdown command received.")
        await self.bot.close()

# Log when the bot connects
@bot.event
async def on_connect():
    # Format the "Logged in as" message
    text = f"Logged in as {bot.user.name}"
    if str(bot.user.discriminator) != "0":  # Check if discriminator exists and is not "0"
        text += f"#{bot.user.discriminator}"
    
    Console.print_info(text)
    Console.print_info(f"You can now use commands with {os.getenv('DISCORD_BOT_PREFIX')}")

# Run the bot
async def main():
    try:
        await bot.add_cog(GoogleSheets(bot))
        await bot.add_cog(Utility(bot))
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))
    except Exception as e:
        Console.print_error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())