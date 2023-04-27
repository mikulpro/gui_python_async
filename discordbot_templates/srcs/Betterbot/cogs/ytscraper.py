import discord
from discord.ext import commands
from googleapiclient.discovery import build
import urllib.parse

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.youtube = build('youtube', 'v3', developerKey='AIzaSyDz2YFpn_OiVeN34ntdn-fNOKlN7Lsq78U')

    @commands.command()
    async def youtube(self, ctx, *, search):
        """youtube search"""
        query = urllib.parse.quote(search)
        request = self.youtube.search().list(
            part='id,snippet',
            q=query,
            type='video'
        )
        response = request.execute()

        videos = []
        for item in response['items']:
            video = {
                'title': item['snippet']['title'],
                'url': f'https://www.youtube.com/watch?v={item["id"]["videoId"]}'
            }
            videos.append(video)

        if len(videos) > 0:
            embed = discord.Embed(title=f"Search results for '{search}'", color=discord.Color.blue())
            for i, video in enumerate(videos[:5]):
                embed.add_field(name=f"Video {i+1}", value=f"[{video['title']}]({video['url']})", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No videos found.")

async def setup(bot):
    await bot.add_cog(YouTube(bot))
