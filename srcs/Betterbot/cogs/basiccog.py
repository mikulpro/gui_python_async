from discord.ext import commands
import random
import discord


class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
	
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('Rekurze'):
            await message.channel.send(f'{message.content} co to je sakra?')
        if message.author.bot:
            return
        if message.content.startswith('Based'):
            await message.channel.send('Based? Based on what regard.') 

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention} to Hell.')

    @commands.Cog.listener()
    async def on_ready(self):
        print("starting up")
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name="mossadfearsmypower, type !help"))

        for guild in self.bot.guilds:
            print("Joined {}".format(guild.name))
        print("Startup succesfull")

    @commands.command()
    async def HowIamIfeeling(self, ctx):
        """Emoticon"""
        await ctx.send("<:PepeKMS:776788745461825557> ")

    @commands.command()
    async def lol(self, ctx):
        """More or less hello world"""
        await ctx.send("lol indeed")

    @commands.command()
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            return
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
