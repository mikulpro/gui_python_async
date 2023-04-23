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

def main():
    url =  'http://books.toscrape.com/'
    stranka_v_html = ziskej_stranku_v_html(url)
    uplynuly_cas = -1
    
    if stranka_v_html is not None:

        # vymazani predesleho docasneho ulozeni stranky
        try:
            remove('temp.html')
            remove('book_prices.csv')
        except:
            pass

        pocatecni_cas = time.time()

        # ukladani do temp.html pro debugovani
        with open('temp.html', 'x', encoding='utf-8') as docasny_soubor:
            docasny_soubor.write(stranka_v_html)

        # hledani knih na strance a nacitani jejich nazvu a cen
        obsah = BeautifulSoup(stranka_v_html, 'html.parser')
        nalezene_knihy = []

        for kniha in obsah.find_all('article', class_='product_pod'):
            nazev = kniha.find('h3').find('a')['title']
            cena = kniha.find('p', class_='price_color').text
            nalezene_knihy.append({'nazev': nazev, 'cena': cena})

        # analyya cen knih
        with open('book_prices.csv', 'x', encoding='utf-8') as prehled_cen:
            for kniha in nalezene_knihy:
                prehled_cen.write(f"{kniha['nazev']} : {kniha['cena']}\n")

        koncovy_cas = time.time()
        uplynuly_cas = koncovy_cas - pocatecni_cas

    else:
        print("Neco se pokazilo.")

    print(f"Od zacatku do konce main() ubehlo {uplynuly_cas} sekund.")

if __name__ == '__main__':
    main()