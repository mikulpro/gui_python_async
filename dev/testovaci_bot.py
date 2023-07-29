import discord                                                          # Discord API
import requests                                                         # knihovna pro HTTP requesty
from bs4 import BeautifulSoup                                           # knihovna pro parsovani HTML
from discord.ext.commands import Bot, has_permissions                   # knihovna pro Discord boty

intents = discord.Intents.all()                                         # Intents jsou "zapouzrena" nastaveni discord opravneni pro bota
intents.typing = True                                                   # Urcuje, jestli bot muze psat zpravy
intents.presences = True                                                # Urcuje, jestli muze bot videt, kdyz se nekdo pripoji nebo odpoji

bot = Bot(command_prefix='/', intents=intents)                          # Urci, jaky prefix musi byt pred kazdou zpravou, aby na ni bot reagoval

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')                      # Jakmile prijde zprava, ze se bot pripojil, vypise se tento text

@bot.command(name='gas_prices')                                         # Pri napsani zpravy "/gas_prices" se spusti tato funkce
async def gas_prices(ctx):                                              # Jakmile prijde ocekavana zprava, spusti se tato funkce
    url = 'https://gasprices.aaa.com/?state=VA'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')               # Ziskani HTML kodu stranky
    gas_prices = soup.find_all('PRICE_ELEMENT', class_='PRICE_CLASS')   # Ziskani vsech elementu s tridou "PRICE_CLASS"
    prices = '\n'.join([price.get_text() for price in gas_prices])      # Ziskani textu z kazdeho elementu
    await ctx.send(f'**Gas Prices:**\n{prices}')                        # Odeslani zpravy s cenami


if __name__ == '__main__':
    TOKEN = ''
    bot.run(TOKEN)
