# Asynchronní programování v Pythonu

## Úvod
Přestože se jedná o předmět s názvem GUI, tak dnešní téma nebude demonstrováno na žádném Python modulu vyloženě pro grafiku, spíš představíme techniku asynchronního programování jako takovou, která je velmi užitečná právě pro programování grafického rozhraní, protože umožňuje frontend a backend například oddělit a nahlížet na ně jako na dva souběžně běžící celky, které spolu komunikují, ale její samotné praktické využití ponecháme na vaší fantasii.

## Pojmy
Pojem **Asynchronie**, v počítačovém programování, označuje výskyt "událostí" nezávislých na běhu hlavního programu, dále toto označení zahrnuje způsoby, jak s těmito "událostmi" nakládat. Tyto "události" mohou být například příchozí zprávy, signály, změny stavu, nebo dokonce i chyby. Asynchronní programování je tedy programování, které umožňuje běh hlavního programu i při výskytu těchto "událostí".

Slovem **Konkurence** se nazývá situace, kdy je v daném okamžiku spuštěno více procesů, které se vzájemně ovlivňují. V případě, že se jedná o procesy, které běží na jednom fyzickém procesoru, ale využívají nějaký způsob časového dělení, tak se jedná o **konkurentní programování**. Konkurentní programování si můžeme představit tak, že ve chvíli, kdy jeden proces na něco čeká a jen by zabíral CPU prázdnými instrukcemi, tak je "odložen" vedle a místo něj využívá CPU jiný proces, který zrovna má na práci něco smysluplnějšího než na něco pouze čekat. Dokonce jsou i případy, kdy je konkurence naprosto nezbytná, neboť některé části programu většinu svého času pouze čekají - např. Discord bot neustále čeká, jestli ve zprávách nedostane příkaz, na který musí zareagovat, ale zároveň s tím musí plnit i všechny další úkoly, pro které byl stvořen, třeba ukazovat čas, nebo pouštět hudbu.

Slovem **Paralelizace** se nazývá situace, kdy je v daném okamžiku spuštěno více procesů, které běží na různých fyzických procesorech / jádrech. Použití paralelizace a konkurence zároveň může značně zefektivnit práci našeho programu.

## Možnosti implementace asynchronního programování v Pythnu
Pokud chci dělat více věcí najednou, můžu použít třeba knihovnu asyncio pro konkurentní programování, kdy vlastně mám nějakou hlavní část programu, obvykle nazývanou event loop, která využivá pro zpracování různých událostí/eventů takové funkce, které jsou schopné se v případě potřeby "odložit" a nechat tak místo pro jiné funkce. 

Pokud chci dělat více věcí najednou, můžu také použít nějakou knihovnu pro threading, která mi umožní rozsekat program do více na sobě nezávislých vláken, která potom běží konkurentně (jako by "souběžně"), tedy se překládají a posílají do procesoru řádky kódu z obou vláken tak nějak rovnoměrně / "spravedlivě", aby běžela obě vlákna zároveň víceméně plynule. 

Python je interpretovaný jazyk a jeho interpretr se snaží chránit programátora před chybným využíváním vláken (chybné využívání vláken ≈ vlákna se vájemně ovlivňují, nebo se "hádají" o nějakou část paměti) takzvaným Global Interpreter Lockem (GIL). GIL víceméně podkope veškerou naši snahu o paralelizaci Python kódu pomocí více vláken, která by se vykonávala na různých jádrech CPU, a pošle všechna vlákna na stejné jádro CPU, jako kdyby se jednalo pouze o jedno vlákno, takže pokud nevyužijeme nějaké knihovny, které GIL obejdou, tak se stále bude veškerý náš kód vykonávat pouze na jednom jádře procesoru -> tedy se ve výsledku stále jedná o konkurentní programování bez paralelizace.

Příkladem knihovny, která GIL obchází, je třeba numpy využívající nízkoúrovňové funkce napsané v jazyce C a následně zkompilované, které GIL obcházejí.

## Zadání úkolů
0. Ujistěte se, že máte nainstalovaný Python interpreter alespoň verze 3.7. (https://www.python.org/downloads/) či novější a že máte nainstalované všechny následující moduly: asyncio, discord, trio, unsync, uvloop, pycord
`python -m pip install asyncio`
`python -m pip install discord`
`python -m pip install trio`
`python -m pip install unsync`
`python -m pip install uvloop`
1. Naklonujte si tento repozitář, nebo si ho stáhněte jako zip soubor. Pro tento "kurz" nebude zapotřebí nic commitovat a pushovat.
2. V adresáři *presentation* se podívejte na rozdíly mezi implementací jednoduchého web-scrape skriptu bez využití asychronity a s jejím využitím.
3. V adresáři *metrials* naleznete připravené základní skripty pro zprovoznění Discord bota. Připojte se na náš testovací server pomocí tohoto odkazu:  https://discord.gg/7WJK57dcCv  Po připojení si řekněte Prokopovi nebo Filipovi o token pro jednoho z botů a zprovozněte ho tak, aby byl na Discordu zobrazený ve stavu *online*. (Stav online se značí tou zelenou tečkou vedle jména uživatele.)
4. Seznamte se s již implementovanými funkcemi vašeho bota a poté implementujte další konkurentně běžící funkce, které budou využívat Discord API. (Například příkaz, který bude zobrazovat aktuální počet uživatelů na serveru, nebo příkaz, který bude zobrazovat aktuální počet zpráv v kanálu.) Použijte oficiální Discord API dokumentaci: https://discord.com/developers/docs/intro Alternativně můžete použít modul Pycord, jehož dokumentace je dostupná zde: https://docs.pycord.dev/en/stable/ 
5. Zlatým hřebem dnešní GUI hodiny by mělo být to, že se vám podaří implementovat do bota nějaký web-scraper, který bude využívat asynchronního programování. (Například scraper, který bude zobrazovat aktuální kurz bitcoinu, nebo scraper, který bude zobrazovat aktuální ceny Natural95 v různých benzínkách fungujících na území ČR.)

# Asynchronous Programming in Python
This repository servers as material deployment place for student semestral project in GUI subject taught at Jan Evnagelista Purkyně's University.

Zatim tu máš cool script prokope, feel free to test (https://www.youtube.com/watch?v=ftmdDlwMwwQ)

Nevím jak moc jste na ujepu probírali paralelizaci takže ohledne prezentace:

slide n- paralelni a konkurentni programovani
slide n+1- threading multiproccesing, async GIL

Ideas-mužeme to udelat ve i formatu ipynb plus rovnou tam přidat i prezentaci. Zaleží na kodu, for now i am kinda lost tbh

# TODO:
Celky:
Uvedení do problematiky (prezentace)

-async

--gil, threading multiprocessing, paralelní, konkurentní

-ostatní

--discord api, api, web scraping

--(udelat mini dokumentaci jak delat s discord api, keywords a mechaniky)

Code na predstaveni problematiky.

-crawler

-scraper

-files work

Discord projekt

-setup 

--vytvořit 15 tokenu

--server

--test jestli fungují

-code

--simple commands

--on message

--interesting by bylo nechat boty mezi sebou comunicovat

--jedna z tasku muže byt nejakej level system nebo neco co uchovává data

--také nejaký reminder system

--callovat open ai api 

--scraper

--scraper into neco jako nafta

--scraper into youtubebot

--scraper into pulling memes or something like that

Navody a alternativy pastebinu

Pridat veci

For now budu prolly workovat na finkeři na test botovi, hodim ho sem asap.




