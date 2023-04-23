import requests
from bs4 import BeautifulSoup
from os import remove
import time

def ziskej_stranku_v_html(url_stranky):
    navratova_hodnota = requests.get(url_stranky)
    if navratova_hodnota.status_code == 200:    # 200 je podle HTTProtokolu odpoved, ze vse probehlo v poradku
        return navratova_hodnota.text
    else:
        print(f"Error: Nebylo mozne ziskat data z {url_stranky}")
        return None
    
def scrapni_stranku(url, cislo_stranky=None):
    stranka_v_html = ziskej_stranku_v_html(url)

    if stranka_v_html is not None:

        # vymazani predesleho docasneho ulozeni stranky
        try:
            remove('temp.html')
        except:
            pass

        # ukladani do temp.html pro debugovani
        with open('temp.html', 'x', encoding='utf-8') as docasny_soubor:
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


def main():
    try:
        remove('episode_titles.csv')
    except:
        pass

    uplynuly_cas = -1
    urls = []
    for i in range(0, 80): # pro ucely zrychleni demonstrace snizeno ze 413 na 80
        urls.append(f'https://talkpython.fm/{i}')
    
    pocatecni_cas = time.time()    
    for i in range(len(urls)):
        scrapni_stranku(urls[i], i)
    koncovy_cas = time.time()

    uplynuly_cas = koncovy_cas - pocatecni_cas
    print(f"Od zacatku do konce main() ubehlo {uplynuly_cas} sekund.")

if __name__ == '__main__':
    main()