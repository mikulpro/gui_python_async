from discord.ext import commands, tasks
import random
import discord
import socket
import asyncio
from pkgutil import iter_modules


class LoadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 65432))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)  # Important: set the socket to be non-blocking
        self.reciever.start()
        


    @tasks.loop(seconds=5)
    async def reciever(self):
        l = [m.name for m in iter_modules(['cogs'], prefix='cogs.')]
        try:
            conn, addr = self.server_socket.accept()  # Should be non-blocking
        except BlockingIOError:
            # No client is trying to connect, it's safe to skip
            return

        try:
            # Receive data
            data = conn.recv(1024)
            command = data.decode('utf-8')
            print(f"Received command: {command}")

            parts = command.split(" ", 1)
            try:
                if parts[1] in l:
                    if parts[0] == "Load":
                        await self.bot.load_extension(parts[1])
                    elif parts[0] == "Unload":
                        await self.bot.unload_extension(parts[1])   
                    else:
                        print(f"uknowns command: {parts}")
            except:
                print(f"fail: {parts}")
            # Sending a response
            response = "Command received"
            conn.sendall(response.encode('utf-8'))

        finally:
            conn.close()  

    @tasks.loop(seconds=4)
    async def manual_reloader(self):
       
        for extension in [m.name for m in iter_modules(['cogs'], prefix='cogs.')]:
            try:
                await self.bot.load_extension(extension)
            except:
                print(f"fail{extension}")

    @commands.command()
    async def lol3(self, ctx):
        """More or less hello world for testing purposes"""
        await ctx.send("lol indeed")

    @commands.command(hidden=True)
    async def startmanualload(self, ctx):
        self.manual_reloader.start()
        await ctx.send("sure nerd")
        # actually starts manual loading
        # !!! WORKS ONLY WHEN LAUNCHED IN EXAMBOT !!! 

async def setup(bot):
    await bot.add_cog(LoadCog(bot))


