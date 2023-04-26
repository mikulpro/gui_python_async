# main.py
from discord.ext import commands
import discord

intents = discord.Intents.all()

class ExampleBot(commands.Bot):
    def __init__(self):
        # initialize our bot instance, make sure to pass your intents!
        # for this example, we'll just have everything enabled
        super().__init__(
            command_prefix="!",
            intents=intents
        )
    
    # the method to override in order to run whatever you need before your bot starts
    async def setup_hook(self):
        await self.load_extension("cogs.maincog")

ExampleBot().run('OTU2NjE2MTE1MzQwMDUwNDgz.GGz0Ie.UistjGDj5GqkuZ9PYVuofctH9oSSxaObyLjOdY')

