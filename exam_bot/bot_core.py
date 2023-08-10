import discord                                                          # Discord API
import requests                                                         # knihovna pro HTTP requesty
from bs4 import BeautifulSoup                                           # knihovna pro parsovani HTML
from discord.ext.commands import Bot, has_permissions                   # knihovna pro Discord boty
from main import rectangles

class BotCore:
    _instance = None

    def __new__(cls, in_token):
        if cls._instance is None:
            cls._instance = super(BotCore, cls).__new__(cls)
        return cls._instance

    def __init__(self, in_token):
        self.token = in_token

        intents = discord.Intents.all()                                         # Intents jsou "zapouzrena" nastaveni discord opravneni pro bota
        intents.typing = True                                                   # Urcuje, jestli bot muze psat zpravy
        intents.presences = True                                                # Urcuje, jestli muze bot videt, kdyz se nekdo pripoji nebo odpoji

        bot = Bot(command_prefix='/', intents=intents)

        @bot.event
        async def on_ready():
            print(f'{bot.user} has connected to Discord!')

        bot.run(self.token)

    async def setup_hook(self):
        global rectangles
        for item in rectangles:
            if item.is_active:
                await self.load_extension(item.associated_file)