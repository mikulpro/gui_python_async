from discord.ext import commands

class YoutubeSearchCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
	
    @commands.Cog.listener()
    async def on_ready(self):
        pass
	
    @commands.command()
    async def command(self, ctx: commands.Context):
        await ctx.send("Hello World")

async def setup(bot):
    await bot.add_cog(YoutubeSearchCog(bot))
