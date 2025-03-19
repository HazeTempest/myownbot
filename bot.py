import os
import discord
import json
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from colorama import Fore, Style, init
from datetime import datetime, timedelta

init()          # Initialize colorama
load_dotenv()   # Load .env vars

TOKEN = os.getenv('DISCORD_BOT_TOKEN1')

ALLOWED_USER_IDS = list(map(int, os.getenv('ALLOWED_USER_IDS', '').split(',')))        
ALLOW_SPECIFIC_USERS = True

# Bot setup
bot = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX'), help_command=None)

# Persistence for auto-delete state
AUTO_DELETE_ENABLED = True

def load_auto_delete_state():
    try:
        with open('auto_delete_state.txt', 'r') as f:
            return f.read().strip().lower() == 'true'
    except FileNotFoundError:
        return True
def save_auto_delete_state(state):
    with open('auto_delete_state.txt', 'w') as f:
        f.write(str(state))
AUTO_DELETE_ENABLED = load_auto_delete_state()

# Helper function for sending messages
async def send_response(ctx, content, force_delete=False):
    delete_after = 5 if force_delete or AUTO_DELETE_ENABLED else None
    await ctx.send(content, delete_after=delete_after)

# Console utilities (unchanged)
class Console:
    @staticmethod
    async def delete_command_message(ctx):
        if ctx.author == bot.user:
            await asyncio.sleep(2)
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Message already deleted")
            except Exception as e:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to delete: {e}")
    @staticmethod
    def print_cmd(text): print(f"{Fore.WHITE}[{datetime.now().strftime('%H:%M:%S')}] {Fore.LIGHTBLUE_EX}[COMMAND]{Style.RESET_ALL} {text}")
    @staticmethod
    def print_info(text): print(f"{Fore.WHITE}[{datetime.now().strftime('%H:%M:%S')}] {Fore.LIGHTGREEN_EX}[INFO]{Style.RESET_ALL} {text}")
    @staticmethod
    def print_error(text): print(f"{Fore.WHITE}[{datetime.now().strftime('%H:%M:%S')}] {Fore.LIGHTRED_EX}[ERROR]{Style.RESET_ALL} {text}")

# Google Sheets utilities (unchanged)
class Sheets:
    _worksheet = None
    @staticmethod
    def authenticate_google_sheets():
        creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        return gspread.authorize(creds)
    @classmethod
    def get_worksheet(cls):
        if cls._worksheet is None:
            cls._worksheet = cls.authenticate_google_sheets().open_by_key(os.getenv('SPREADSHEET_ID')).worksheet(os.getenv('SHEET_NAME'))
        return cls._worksheet

# User permission check (unchanged)
def is_allowed_user(ctx):
    return not ALLOW_SPECIFIC_USERS or ctx.author.id in ALLOWED_USER_IDS or ctx.author.id == bot.user.id

# Global error handler (unchanged)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments)):
        usage, example = ctx.command.extras.get("usage", ""), ctx.command.extras.get("example", "")
        await send_response(ctx, f"Wrong parameters. Usage: `{bot.command_prefix}{ctx.command.name} {usage}`\nExample: `{bot.command_prefix}{example}`")
    else:
        Console.print_error(f"Command error: {error}")

# Command hooks (unchanged)
@bot.before_invoke
async def before_invoke(ctx):
    if ALLOW_SPECIFIC_USERS and ctx.author.id not in ALLOWED_USER_IDS:
        Console.print_cmd(f"{ctx.author.name} tried {ctx.message.content}")
    if not is_allowed_user(ctx):
        raise commands.CheckFailure
@bot.after_invoke
async def after_invoke(ctx):
    Console.print_cmd(f"{ctx.author.name} used {ctx.command.name}")
    await Console.delete_command_message(ctx)

# Google Sheets commands (unchanged)
class GoogleSheets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="readsheet", extras={"description": "Reads data from a range.", "usage": "<range>", "example": "readsheet A1:B2"})
    async def read_sheet(self, ctx, range: str):
        try:
            data = Sheets.get_worksheet().get(range)
            await send_response(ctx, f"Data from `{range}`:\n```\n{'\\n'.join(' '.join(row) for row in data)}\n```")
        except Exception as e:
            Console.print_error(f"readsheet failed: {e}")

    @commands.command(name="writesheet", extras={"description": "Writes a value to a cell.", "usage": "<cell> <value>", "example": "writesheet A1 Hello"})
    async def write_sheet(self, ctx, cell: str, *, value: str):
        if not value:
            await send_response(ctx, f"Wrong parameters. Usage: `{self.bot.command_prefix}writesheet <cell> <value>`\nExample: `{self.bot.command_prefix}writesheet A1 Hello`")
            return
        try:
            Sheets.get_worksheet().update_acell(cell, value)
            await send_response(ctx, f"Wrote `{value}` to `{cell}`.")
        except Exception as e:
            Console.print_error(f"writesheet failed: {e}")

    @commands.command(name="addscore", extras={"description": "Adds players' scores.", "usage": "[<player1> <score1> ...]", "example": 'addscore "Haze Clarke" 2000'})
    async def add_score(self, ctx, *args: str):
        if not args:
            await send_response(ctx, f"Wrong parameters. Usage: `{self.bot.command_prefix}addscore <player1> <score1> [<player2> <score2> ...]`\nExample: `{self.bot.command_prefix}{self.command.extras['example']}`")
            return
        if len(args) % 2 != 0:
            await send_response(ctx, f"Each player needs a score. Usage: `{self.bot.command_prefix}addscore <player1> <score1> [<player2> <score2> ...]`\nExample: `{self.bot.command_prefix}{self.command.extras['example']}`")
            return
        try:
            rows = []
            for i in range(0, len(args), 2):
                player, score_str = args[i], args[i+1]
                score = int(score_str)
                rows.append([player, score])
            Sheets.get_worksheet().append_rows(rows)
            await send_response(ctx, f"Added scores for {len(rows)} players.")
        except ValueError:
            await send_response(ctx, f"Scores must be integers. Usage: `{self.bot.command_prefix}addscore <player1> <score1> [<player2> <score2> ...]`\nExample: `{self.bot.command_prefix}{self.command.extras['example']}`")
        except Exception as e:
            Console.print_error(f"addscore failed: {e}")

    @commands.command(name="viewscore", extras={"description": "Views all scores for a player.", "usage": "<player>", "example": 'viewscore "Haze Clarke"'})
    async def view_score(self, ctx, player_name: str):
        try:
            worksheet = Sheets.get_worksheet()
            names, scores = worksheet.col_values(1), worksheet.col_values(2)
            player_scores = [scores[i] for i, name in enumerate(names) if name.lower() == player_name.lower() and i < len(scores)]
            await send_response(ctx, f"Scores for `{player_name}`: `{' '.join(player_scores)}`" if player_scores else f"No scores for `{player_name}`.")
        except Exception as e:
            Console.print_error(f"viewscore failed: {e}")

    @commands.command(name="resetscore", extras={"description": "Resets all scores.", "usage": "", "example": "resetscore"})
    async def reset_score(self, ctx):
        try:
            worksheet = Sheets.get_worksheet()
            num_rows = len(worksheet.col_values(1))
            if num_rows > 0:
                worksheet.update(f'A1:B{num_rows}', [[''] * 2] * num_rows)
                await send_response(ctx, "All scores reset.")
            else:
                await send_response(ctx, "No scores to reset.")
        except Exception as e:
            Console.print_error(f"resetscore failed: {e}")

# Utility commands
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", extras={"description": "Shows this help message.", "usage": "", "example": "help"})
    async def help_command(self, ctx):
        commands_list = [(f"{self.bot.command_prefix}{cmd.name} {cmd.extras.get('usage', '')}".strip(), cmd.extras.get("description", "No description"), 
                         f"{self.bot.command_prefix}{cmd.extras.get('example', '')}") for cmd in sorted(self.bot.commands, key=lambda c: c.name) 
                         if cmd.cog_name in ["GoogleSheets", "Utility"]]
        if not commands_list:
            return
        max_cmd, max_desc, max_ex = max(len(c[0]) for c in commands_list), max(len(c[1]) for c in commands_list), max(len(c[2]) for c in commands_list)
        lines = [f"{'Command':<{max_cmd}}  {'Description':<{max_desc}}  {'Example':<{max_ex}}", "-" * (max_cmd + max_desc + max_ex + 4)]
        lines.extend(f"{c[0]:<{max_cmd}}  {c[1]:<{max_desc}}  {c[2]:<{max_ex}}" for c in commands_list)
        await send_response(ctx, f"```\n{chr(10).join(lines)}\n```")

    @commands.command(name="ping", extras={"description": "Checks bot latency.", "usage": "", "example": "ping"})
    async def ping(self, ctx):
        await send_response(ctx, f"Pong! Latency is {round(self.bot.latency * 1000, 2)}ms.")

    @commands.command(name="delete", extras={"description": "Deletes bot messages.", "usage": "<number>", "example": "delete 3"})
    async def delete_messages(self, ctx, number: int):
        try:
            messages = [msg async for msg in ctx.channel.history(limit=number + 1) if msg.author == self.bot.user]
            await ctx.channel.delete_messages(messages)
        except Exception as e:
            Console.print_error(f"delete failed: {e}")

    @commands.command(name="reminder", extras={"description": "Sends a reminder.", "usage": "[GS] <time> [user1 ...]", "example": "reminder GS 16 User1 "})
    async def reminder(self, ctx, *args: str):
        if len(args) < 2:
            await send_response(ctx, f"Wrong parameters. Usage: `{self.bot.command_prefix}reminder [GS] <time> <user1> [user2 ...]`\nExample: `{self.bot.command_prefix}{self.command.extras['example']}`")
            return
        gs_mode = False
        if args[0].lower() == "gs":
            gs_mode = True
            time_str = args[1]
            users = args[2:]
        else:
            time_str = args[0]
            users = args[1:]
        try:
            time = int(time_str)
            if time < 0 or time > 23:
                await send_response(ctx, "Time must be between 0 and 23.")
                return
        except ValueError:
            await send_response(ctx, "Time must be an integer.")
            return
        if not users:
            await send_response(ctx, "At least one user must be specified.")
            return
        mentions = []
        for u in users:
            if u.startswith("<@") and u.endswith(">"):
                mentions.append(u)
            elif (user := discord.utils.get(ctx.guild.members, name=u)):
                mentions.append(f"<@{user.id}>")
            else:
                await send_response(ctx, f"User '{u}' not found!")
                return
        now = datetime.now()
        reset_time = now.replace(hour=time, minute=0, second=0, microsecond=0)
        if now > reset_time:
            reset_time += timedelta(days=1)
        timestamp = int(reset_time.timestamp())
        if gs_mode:
            message = f"{' '.join(mentions)}\nPlease do your GS runs. Reset <t:{timestamp}:R> or <t:{timestamp}:t> local time"
        else:
            message = f"{' '.join(mentions)}\nReminder <t:{timestamp}:R> or <t:{timestamp}:t> local time"
        await send_response(ctx, message)

    @commands.command(name="shutdown", extras={"description": "Shuts down the bot.", "usage": "", "example": "shutdown"})
    async def shutdown_command(self, ctx):
        if ctx.author == self.bot.user:
            await ctx.message.delete()
        message = await ctx.send("Shutting down...")
        await message.delete()
        Console.print_info("Shutdown received.")
        await self.bot.close()

    @commands.command(name="autodel", extras={"description": "Toggles auto-delete.", "usage": "<on/off>", "example": "autodel off"})
    async def auto_delete_toggle(self, ctx, state: str):
        global AUTO_DELETE_ENABLED
        state = state.lower()
        if state in ["on", "off"]:
            AUTO_DELETE_ENABLED = state == "on"
            save_auto_delete_state(AUTO_DELETE_ENABLED)
            await send_response(ctx, f"Auto-delete is now **{'enabled' if AUTO_DELETE_ENABLED else 'disabled'}**.", force_delete=True)
        else:
            await send_response(ctx, f"Invalid state. Usage: `{self.bot.command_prefix}autodel <on/off>`\nExample: `{self.bot.command_prefix}{self.command.extras['example']}`", force_delete=True)

# Bot events and main
@bot.event
async def on_ready():
    Console.print_info(f"Logged in as {bot.user.name}")
    Console.print_info(f"Use commands with {bot.command_prefix}")
    if ALLOW_SPECIFIC_USERS:
        allowed_users = []
        for user_id in ALLOWED_USER_IDS:
            user = bot.get_user(user_id)
            if user:
                allowed_users.append(user.name)
            else:
                allowed_users.append(f"Unknown User (ID: {user_id})")
        if allowed_users:
            Console.print_info("Allowed users: " + ", ".join(allowed_users))
        else:
            Console.print_info("No allowed users found or resolved.")

async def main():
    try:
        await bot.add_cog(GoogleSheets(bot))
        await bot.add_cog(Utility(bot))
        await bot.start(TOKEN)
    except Exception as e:
        Console.print_error(f"Error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()
            Console.print_info("Bot closed gracefully.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        Console.print_info("Ctrl+C received, shutting down...")
    except Exception as e:
        Console.print_error(f"Unexpected error: {e}")