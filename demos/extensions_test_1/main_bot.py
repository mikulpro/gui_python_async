import discord
from discord.ext import commands

intents = discord.Intents.default()  # Create default intents
intents.typing = False  # You can adjust these intents based on your bot's needs
intents.presences = False

# Create a bot instance with intents and a command prefix
bot = commands.Bot(command_prefix='//', intents=intents)

async def test(ctx):
    await bot.load_extension('extensions.hello')

# Run the bot with your token
token = input("Token: ")
bot.run(token)