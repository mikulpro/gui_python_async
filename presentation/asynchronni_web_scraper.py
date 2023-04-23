from bs4 import BeautifulSoup
from os import remove
import time
import asyncio
import aiohttp # nahrada pro 'import requests' v pripade asyncu, tez mozno pouzit httpx, ale to mi moc nefungovalo

async def ziskej_stranku_v_html(url_stranky):
    async with aiohttp.ClientSession() as session:
        async with session.get(url_stranky) as http_odpoved:
            http_odpoved.raise_for_status()
            stranka_v_html = await http_odpoved.text()
            return stranka_v_html
    
async def scrapni_stranku(url, cislo_stranky=None):

    stranka_v_html = await ziskej_stranku_v_html(url)

    if stranka_v_html is not None:

        # ukladani do temp.html pro debugovani
        with open('temp.html', 'a+', encoding='utf-8') as docasny_soubor:
            docasny_soubor.write(stranka_v_html)

        # hledani nazvu epizod na strance
        obsah = BeautifulSoup(stranka_v_html, 'html.parser')
        titulek = obsah.select_one('h1')
        if titulek is None:
            titulek = "TITULEK NENALEZEN"
        with open('episode_titles.csv', 'a+', encoding='utf-8') as prehled_epizod:
            prehled_epizod.write(f"{titulek}\n")
    else:
        print(f"Stranku https://talkpython.fm/{cislo_stranky} se nepodarilo nacist.")

async def main_async(loop: asyncio.AbstractEventLoop):
    uplynuly_cas = -1
    try:
        remove('episode_titles.csv')
        remove('temp.html')
    except:
        pass
    
    tasky = []
    urls = []
    for i in range(0, 80): # pro ucely zrychleni demonstrace snizeno ze 413 na 80
        urls.append(f'https://talkpython.fm/{i}')
    for i in range(len(urls)):
        tasky.append( loop.create_task(scrapni_stranku(urls[i], i)) )

    pocatecni_cas = time.time()
    #
    for task in tasky:
        await task
    #
    koncovy_cas = time.time()
    uplynuly_cas = koncovy_cas - pocatecni_cas
    print(f"Od zacatku do konce main() ubehlo {uplynuly_cas} sekund.")

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_async(loop))

if __name__ == '__main__':
    main()