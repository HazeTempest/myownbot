import discord
import os
import dotenv

dotenv.load_dotenv()
token = os.getenv('TOKEN')

client = discord.Client()

@client.event
async def on_message(message):
    # Ignore messages from the bot itself to avoid loops
    if message.author == client.user:
        return
    # Respond to "!ping" with "Pong!"
    if message.content.startswith('!ping'):
        await message.channel.send('Pong!')

# Replace 'YOUR_USER_TOKEN' with your token
client.run(token)