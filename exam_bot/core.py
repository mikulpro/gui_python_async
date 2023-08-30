from discord.ext import commands
import threading
import discord
import os

def runni_bota():
    '''
    Tato funkce rozsiruje metodu bot_run() z discord.py o (pseudo) threadding, ktery je potreba pro spravne fungovani bota.
    '''

    # intents
    intents = discord.Intents.default()
    intents.typing = True
    intents.presences = True

    # instance bota
    global bot
    bot = commands.Bot(command_prefix='//', intents=intents)

    # korutina pro bota
    bot_thread = threading.Thread(target=_bot_run)
    bot_thread.start()
    _start_autoload()

def vypni_bota():
    global bot
    #TODO: unload all extensions
    bot.close()
    
def _bot_run():
    global bot

    token = None
    token_file_path = "tokeny.csv"

    try:
        with open(token_file_path, "r") as f:
            token = f.readline().strip()            
    except FileNotFoundError:
        print(f"File '{token_file_path}' not found.")
    except Exception as e:
        print("An error occurred:", e)

    if token is not None:
        bot.run(token)
    else:
        raise Exception("Token not found.")

async def _start_autoload():
    await bot.load_extension('cogs.loadcog')