from discord.ext import commands
import openai
APIKEY = "your api key"
openai.api_key = APIKEY

class OpenAICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def askgpt(self, ctx, arg):
        """Makes simple request to chat gpt"""
        output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": 
                arg}]
        )
        
        await ctx.send(output['choices'][0]['message']['content'])

async def setup(bot):
    await bot.add_cog(OpenAICog(bot))