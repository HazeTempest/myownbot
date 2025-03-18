import discord
from discord.ext import commands
from utils import sheets, console  # Import the entire sheets and console modules

class GoogleSheets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="readsheet")
    async def read_sheet(self, ctx, range):
        try:
            data = sheets.get_worksheet().get(range)
            await ctx.send(f"Data from range `{range}`:\n```\n{' '.join([' '.join(row) for row in data])}\n```")
            console.print_cmd(f"Used command: readsheet {range}")
        except Exception as e:
            console.print_error(f"readsheet command failed: {e}")

    @commands.command(name="writesheet")
    async def write_sheet(self, ctx, cell: str, *, value: str):
        try:
            sheets.get_worksheet().update_acell(cell, value)
            await ctx.send(f"Successfully wrote `{value}` to cell `{cell}`.")
            console.print_cmd(f"Used command: writesheet {cell} {value}")
        except Exception as e:
            console.print_error(f"writesheet command failed: {e}")

    @commands.command(name="addscore")
    async def add_score(self, ctx, player_name: str, score: int):
        try:
            worksheet = sheets.get_worksheet()
            col_a = worksheet.col_values(1)
            next_row = len(col_a) + 1
            worksheet.update_cell(next_row, 1, player_name)
            worksheet.update_cell(next_row, 2, score)
            await ctx.send(f"Added `{player_name}` with score `{score}` to row `{next_row}`.")
            console.print_cmd(f"Used command: addscore {player_name} {score}")
        except Exception as e:
            console.print_error(f"addscore command failed: {e}")

async def setup(bot):
    await bot.add_cog(GoogleSheets(bot))