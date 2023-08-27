from discord.ext import commands, tasks
import random
import discord
from cogs import EXTENSIONS

class LoadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reloader.start()
	
    @tasks.loop(seconds=5)
    async def reloader(self):
        from cogs import EXTENSIONS
        #[m.name for m in iter_modules(['cogs'], prefix='cogs.')]
        for extension in EXTENSIONS:
            try:
                await self.bot.load_extension(extension)
            except:
                print(f"fail{extension}")

    @commands.command()
    async def lol2(self, ctx):
        """More or less hello world"""
        await ctx.send("lol indeed")


async def setup(bot):
    await bot.add_cog(LoadCog(bot))