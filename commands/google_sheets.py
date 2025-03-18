import discord
from discord.ext import commands
from utils.sheets import get_worksheet
from utils.logging import log_command_usage, delete_command_message

class GoogleSheets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="readsheet")
    async def read_sheet(self, ctx, range):
        log_command_usage(ctx)
        try:
            data = get_worksheet().get(range)
            await ctx.send(f"Data from range `{range}`:\n```\n{' '.join([' '.join(row) for row in data])}\n```")
            await delete_command_message(ctx)
        except Exception as e:
            print(f"[ERROR] readsheet command failed: {e}")

    @commands.command(name="writesheet")
    async def write_sheet(self, ctx, cell: str, *, value: str):
        log_command_usage(ctx)
        try:
            get_worksheet().update_acell(cell, value)
            await ctx.send(f"Successfully wrote `{value}` to cell `{cell}`.")
            await delete_command_message(ctx)
        except Exception as e:
            print(f"[ERROR] writesheet command failed: {e}")

    @commands.command(name="addscore")
    async def add_score(self, ctx, player_name: str, score: int):
        log_command_usage(ctx)
        try:
            worksheet = get_worksheet()
            col_a = worksheet.col_values(1)
            next_row = len(col_a) + 1
            worksheet.update_cell(next_row, 1, player_name)
            worksheet.update_cell(next_row, 2, score)
            await ctx.send(f"Added `{player_name}` with score `{score}` to row `{next_row}`.")
            await delete_command_message(ctx)
        except Exception as e:
            print(f"[ERROR] addscore command failed: {e}")

def setup(bot):
    bot.add_cog(GoogleSheets(bot))