import logging
from discord.ext import commands
import random
import discord

logger = logging.getLogger('discord.BasicCog')

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.depth = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.depth > 15:
            self.depth = 0  # Resetting for future use
            return
        if message.content.startswith('Rekurze'):
            self.depth += 1
            await message.channel.send(f'{message.content} co to je sakra?')
            logger.info(f'Rekurze triggered. Depth: {self.depth}')
        if message.author.bot:
            return
        if message.content.startswith('Based'):
            await message.channel.send('Based? Based on what regard.')
            logger.info('Based command triggered.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention} to Hell.')
            logger.info(f'Member {member.mention} joined.')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name="mossadfearsmypower, type !help"))
        for guild in self.bot.guilds:
            logger.info("Joined {}".format(guild.name))
        logger.info("Startup successful.")

    @commands.command()
    async def HowIamIfeeling(self, ctx):
        await ctx.send("<:PepeKMS:776788745461825557>")
        logger.info('HowIamIfeeling command triggered.')

    @commands.command()
    async def lol(self, ctx):
        await ctx.send("lol indeed")
        logger.info('lol command triggered.')

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            logger.warning('Incorrect roll format.')
            return
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)
        logger.info(f'Roll command triggered. Rolls: {rolls}, Limit: {limit}')

async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
