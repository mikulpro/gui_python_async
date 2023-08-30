from discord.ext import commands
import threading
import discord
import os

# konstanty pro bota
FOLDER_WITH_COGS_PATH = "cogs"

# globalni promenne
global bot # <<< runni_bota()
global loaded_extensions
loaded_extensions = []
    
async def auto_load():
    global bot, loaded_extensions

    while True:
        try:
            for filename in os.listdir(FOLDER_WITH_COGS_PATH):
                file_path = os.path.join(FOLDER_WITH_COGS_PATH, filename)
                if os.path.isfile(file_path):
                    cog_name = file_path[:-3]
                    await _finalize_loading(cog_name)
                else:
                    continue
        except:
            pass # intentional pass

async def _finalize_loading(extension_path):
    global bot

    await _bot_load_extension(extension_path)
            
async def _bot_load_extension(extension_path):
    global bot

    try:
        await bot.load_extension(extension_path)
    except:
        pass # intentional pass
    return 0

def _unload():
    global bot, loaded_extensions

    for item in loaded_extensions:
        bot.unload_extension(item)

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

def storage_to_cogs_transfer():
    ...