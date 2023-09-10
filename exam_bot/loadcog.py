from discord.ext import commands, tasks
import random
import discord
import socket
import asyncio
import logging
from pkgutil import iter_modules

# Initialize the logger
logger = logging.getLogger('discord.LoadCog')

class LoadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 65432))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)  # Set the socket to be non-blocking
        self.reciever.start()

    @tasks.loop(seconds=5)
    async def reciever(self):
        available_cogs = [m.name for m in iter_modules(['cogs'], prefix='cogs.')]
        try:
            conn, addr = self.server_socket.accept()
        except BlockingIOError:
            return

        try:
            data = conn.recv(1024)
            command = data.decode('utf-8').strip()
            logger.info(f"Received command: {command}")

            action, cog_name = command.split(" ", 1)

            if cog_name not in available_cogs:
                response = "Invalid Cog"
                logger.warning(f"Invalid cog specified: {cog_name}")
            elif action not in ["Load", "Unload", "Reload"]:
                response = "Invalid Action"
                logger.warning(f"Invalid action specified: {action}")
            else:
                try:
                    await getattr(self.bot, f"{action.lower()}_extension")(cog_name)
                    logger.info(f"Success at {action}ing {cog_name}")
                    response = "Success"
                except Exception as e:
                    response = "Failed"
                    logger.error(f"Failed to {action} {cog_name}: {e}")

            conn.sendall(response.encode('utf-8'))

        finally:
            conn.close()

    @tasks.loop(seconds=4)
    async def manual_reloader(self):
        for extension in [m.name for m in iter_modules(['cogs'], prefix='cogs.')]:
            try:
                await self.bot.load_extension(extension)
            except Exception as e:
                logger.error(f"Failed to load {extension}: {e}")

    @commands.command()
    async def lol3(self, ctx):
        await ctx.send("lol indeed")

    @commands.command(hidden=True)
    async def startmanualload(self, ctx):
        self.manual_reloader.start()
        await ctx.send("sure nerd")

async def setup(bot):
    await bot.add_cog(LoadCog(bot))
