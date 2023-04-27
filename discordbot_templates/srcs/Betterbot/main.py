# main.py
from discord.ext import commands
import discord

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
        await self.load_extension("cogs.openaicog")
        await self.load_extension("cogs.basiccog")
    
MyBot().run('your api token')

