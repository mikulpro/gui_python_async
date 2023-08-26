import tkinter as tk
from tkinter import filedialog
import discord
from discord.ext import commands
import re
import threading

def load():
    global bot
    global loaded_extensions

    #TODO: nakopirovat extension file do prislusne slozky

    cesta_k_souboru = filedialog.askopenfilename()
    cesta_k_extensionu = re.split(r'[.:\\/]', cesta_k_souboru)
    print(cesta_k_extensionu)
    temp = ""
    for i in cesta_k_extensionu:
        if i in ['','C','UJEP','GUI','semestralka','gui_python_async','demos','extensions_test_1','py']:
            continue
        else:
            if temp == "":
                temp += i
            else:
                temp += "." + i
        print(temp)
    cesta_k_extensionu = temp
    loaded_extensions.append(cesta_k_extensionu)
    finalize_loading(cesta_k_extensionu)
    return

async def finalize_loading(cesta_k_extensionu):
    global bot
    await bot.load_extension(cesta_k_extensionu)

def unload():
    global loaded_extensions
    global bot

    for item in loaded_extensions:
        bot.unload_extension(item)
    return

def runni_bota():
    intents = discord.Intents.default()  # Create default intents
    intents.typing = False  # You can adjust these intents based on your bot's needs
    intents.presences = False

    # Create a bot instance with intents and a command prefix
    global bot
    bot = commands.Bot(command_prefix='//', intents=intents)

    bot_thread = threading.Thread(target=bot_run)
    bot_thread.start()
    return
    
def bot_run():
    token = 'MTEzODAzNTA5ODE3Njk3ODk4Ng.GyYzC7.UkVwWbeqCRSmFg9nyXefRF7JrE0aNjVy9-LrqY'
    bot.run(token)

if __name__ == "__main__":
    global loaded_extensions 
    loaded_extensions = []

    # Create the main window
    root = tk.Tk()
    root.title("Cog Control Example")

    # Create buttons
    button1 = tk.Button(root, text="Load", command=load)
    button2 = tk.Button(root, text="Unload", command=unload)
    button3 = tk.Button(root, text="Bot", command=runni_bota)

    # Pack buttons into the window
    button1.pack(pady=10)
    button2.pack(pady=10)
    button3.pack(pady=10)

    # Start the main event loop
    root.mainloop()