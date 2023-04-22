import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

intents = discord.Intents.default()  # Use default intents
intents.typing = False  # Disable the 'typing' event
intents.presences = False  # Disable the 'presences' event

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='gas_prices')
async def gas_prices(ctx):
    url = 'URL_OF_WEBSITE_TO_SCRAPE'  # Replace with the URL of the website you want to scrape
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the gas prices on the website
    # Adjust the following code based on the structure of the website you're scraping
    gas_prices = soup.find_all('PRICE_ELEMENT', class_='PRICE_CLASS')  # Replace 'PRICE_ELEMENT' and 'PRICE_CLASS' with appropriate values

    # Extract the gas prices and format them as a string
    prices = '\n'.join([price.get_text() for price in gas_prices])

    # Send the gas prices to the Discord channel
    await ctx.send(f'**Gas Prices:**\n{prices}')

bot.run(TOKEN)
