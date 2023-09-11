from discord.ext import commands
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import time
from collections import deque

logger = logging.getLogger('discord.itlerCog')

class FindHitlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def startGame(self, ctx, arg):
        """play wiki game findhitler arg is format: wiki/Superconducting_magnet"""

        await ctx.send(f"sure bud")
        depth = await main_async(f"https://en.wikipedia.org/{arg}")
        await ctx.send(f"Found Hitler at depth {depth}")


async def setup(bot):
    await bot.add_cog(FindHitlerCog(bot))


async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_main_content_links(session, url, visited, depth, found):
    if found['status']:  # Check the flag before processing
        return "Skipped", []

    print(f"Processing {url} at depth {depth}")
    start_time = time.time()
    content = await fetch_page(session, url)

    soup = BeautifulSoup(content, 'html.parser')
    main_content = soup.find("div", {"id": "bodyContent"})

    status = "Not found"
    if "Hitler" in main_content.text:
        status = "Found"

    links = []
    for link in main_content.find_all("a"):
        href = link.get("href", "")
        if href.startswith("/wiki/") and ":" not in href:
            full_url = "https://en.wikipedia.org" + href
            if full_url not in visited:
                links.append(full_url)
                visited.add(full_url)

    return status, links

async def producer(queue, visited, found, start_url):
    start_url = "https://en.wikipedia.org/wiki/Superconducting_magnet"
    visited.add(start_url)
    queue.append((start_url, 0))

    async with aiohttp.ClientSession() as session:
        while queue:
            url, depth = queue.popleft()
            if found['status']:  # Check the flag before processing
                break
            status, links = await fetch_main_content_links(session, url, visited, depth, found)
            if status == "Found":
                print(f"Found Hitler at depth {depth+1}")
                found['status'] = True  # Set the flag
                return depth + 1
                break
            for link in links:
                queue.append((link, depth + 1))

async def main_async(start_url):
    visited = set()
    queue = deque()
    found = {'status': False}
    depth = await producer(queue, visited, found, start_url)
    return depth


#TODO 
# PATH send
# Fix everything, it just doesnt work how it is supposed to