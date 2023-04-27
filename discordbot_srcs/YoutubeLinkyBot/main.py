import discord
from discord.ext import commands

intents = discord.Intents.all()

class YoutubeScraperBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="yts_",
            intents=intents
        )
    
    async def setup_hook(self):
        await self.load_extension("cogs.maincog")

YoutubeScraperBot().run('')

