import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.logging import log_command_usage, delete_command_message

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        log_command_usage(ctx)
        try:
            latency = round(self.bot.latency * 1000, 2)
            await ctx.send(f"Pong! Latency is {latency}ms.")
            await delete_command_message(ctx)
        except Exception as e:
            print(f"[ERROR] ping command failed: {e}")

    @commands.command(name="delete")
    async def delete_messages(self, ctx, number: int):
        log_command_usage(ctx)
        try:
            messages = []
            async for message in ctx.channel.history(limit=number + 1):
                if message.author == self.bot.user:
                    messages.append(message)
            await ctx.channel.delete_messages(messages)
        except Exception as e:
            print(f"[ERROR] delete command failed: {e}")

    @commands.command(name="resetping", description="Reminds specific users of daily reset with a timestamp.")
    async def resetping(self, ctx: commands.Context, time: int, *users: str):
        log_command_usage(ctx)
        
        # Validate time input (0-23)
        if time < 0 or time > 23:
            await ctx.send("Time must be between 0 and 23 (24-hour format).")
            return

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

        # Get today's date at the specified time
        now = datetime.now()
        today_time = now.replace(hour=time, minute=0, second=0, microsecond=0)

        # If it's already past the specified time, set the timestamp for the same time tomorrow
        if now > today_time:
            today_time += timedelta(days=1)

        # Convert to Unix timestamp
        unix_timestamp = int(today_time.timestamp())

        # Send the message with the timestamp and user mentions
        await ctx.send(f"{' '.join(mentions)} Please do your GS runs. Reset <t:{unix_timestamp}:R>")

def setup(bot):
    bot.add_cog(Utility(bot))