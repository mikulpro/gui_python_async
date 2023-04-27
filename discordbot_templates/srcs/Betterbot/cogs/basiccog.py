from discord.ext import commands
import random
import discord


class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
	
    @commands.Cog.listener()
    async def on_message(self, message):
        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        print("starting up")
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name="mossadfearsmypower, type !help"))

        for guild in self.bot.guilds:
            print("Joined {}".format(guild.name))
        print("Startup succesfull")

    @commands.command()
    async def HowIamIfeeling(self, ctx):
        pass

    @commands.command()
    async def lol(self, ctx):
        pass

    @commands.command()
    async def roll(self, ctx, dice: str):
        pass

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
