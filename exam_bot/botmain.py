# main.py
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv


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
        await self.load_extension("loadcog")
        await self.load_extension("cogs.basiccog") # optionally commented, missing some features by not being launched at the start
       
load_dotenv()
MyBot().run(os.getenv("DISCORD_TOKEN"))

#READ! due to some vscode/python/pkgutil bs, doesnt work if its not opened inside the exambot folder.