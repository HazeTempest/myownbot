import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils import console

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
        await console.delete_command_message(ctx)  # Delete the command message
        console.print_cmd("Used command: help")

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000, 2)
        await ctx.send(f"Pong! Latency is {latency}ms.")
        await console.delete_command_message(ctx)  # Delete the command message
        console.print_cmd("Used command: ping")

    @commands.command(name="delete")
    async def delete_messages(self, ctx, number: int):
        try:
            messages = []
            async for message in ctx.channel.history(limit=number + 1):
                if message.author == self.bot.user:
                    messages.append(message)
            await ctx.channel.delete_messages(messages)
            await console.delete_command_message(ctx)  # Delete the command message
            console.print_cmd(f"Used command: delete {number}")
        except Exception as e:
            console.print_error(f"delete command failed: {e}")

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
            await console.delete_command_message(ctx)  # Delete the command message
            console.print_cmd(f"Used command: resetping {time} {' '.join(users)}")
        except Exception as e:
            console.print_error(f"resetping command failed: {e}")

    @commands.command(name="error")
    async def error_command(self, ctx):
        try:
            # Intentionally cause an error
            raise ValueError("This is a test error.")
        except Exception as e:
            console.print_error(f"error command failed: {e}")
            await ctx.send(f"An error occurred: {e}")
            await console.delete_command_message(ctx)

    @commands.command(name="shutdown")
    async def shutdown_command(self, ctx):
        """Shut down the bot gracefully."""
        await ctx.message.delete()  # Instantly delete the command message
        await ctx.send("Shutting down...", delete_after=0)  # Send and instantly delete the response
        console.print_info("Shutdown command received.")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Utility(bot))