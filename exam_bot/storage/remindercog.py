from discord.ext import commands
import discord
import asyncio
import datetime

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command() 
    async def set_reminder(self, message, arg): #arg is in minutes
        """set reminder at date 04:30 for example"""
        try:
            reminder_time = datetime.datetime.strptime(arg, '%H:%M')
        except ValueError:
            await message.channel.send("Sorry, that's not a valid time format. Please try again.")
            return
        reminder_time = datetime.datetime.combine(datetime.datetime.now().date(), reminder_time.time())
        now = datetime.datetime.now()
        time_delta = reminder_time - now
        print(reminder_time, now, time_delta)

        if time_delta.total_seconds() < 0:
            await message.channel.send("Sorry, you can't set a reminder for a time in the past.")
            return

        await message.channel.send(f"Okay, I will remind you at {reminder_time}.")

        await asyncio.sleep(time_delta.total_seconds())

        await message.channel.send(f"Hey {message.author.mention}, it's time!")
    @commands.command() 
    async def ping_after_x_secs(self, message, arg):
        secs = int(arg)
        await asyncio.sleep(secs)
        await message.channel.send(f"Hey {message.author.mention}, it's time!")
async def setup(bot):
    await bot.add_cog(ReminderCog(bot))