# main.py
from discord.ext import commands
import discord
from cogs import EXTENSIONS


intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self):
        # initialize our bot instance, make sure to pass your intents!
        # for this example, we'll just have everything enabled
        super().__init__(
            command_prefix="!",
            intents=intents
        )
    
    # the method to override in order to run whatever you need before your bot starts
    async def setup_hook(self):     #for extencion of initial extencions

        for extension in EXTENSIONS:
            await self.load_extension(extension)

        """
        await self.load_extension("sample_cogs.remindercog")
        await self.load_extension("sample_cogs.basiccog")
        await self.load_extension("sample_cogs.openaicog")
        await self.load_extension("sample_cogs.chesscog")
        await self.load_extension("sample_cogs.voicecog")
        await self.load_extension("sample_cogs.ytscraper")
    
        """
    
MyBot().run('MTA5ODU0NTA3NjY5Njc5NzI0Ng.GH3xZO.nO4eSzcFsYphaMKQTfV0YRgzyfoccIdu1U6ddU')