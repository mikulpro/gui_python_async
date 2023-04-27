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

## Základní postup použití knihovny asyncio
Základem použití modulu asyncio je rozmyslet si, které úkony vašeho programu budou obsahovat vysoké procento prázdných / čekacích instrukcí. To jsou zpravidla úkony stahování něčeho z nějakého serveru, kde se musí poslat dotaz na server a čekat na odpověď ze serveru, také třeba v případě Discord bota čekání na zprávu od uživatele, nebo třeba čekání na odpověď od databáze. Všechny tyto úkony jsou ideální k tomu, aby se v případě potřeby odložily a nechalo se tak místo pro jiné úkony, které mohou být vykonány v mezidobí, kdy se čeká na odpověď ze serveru.

Tyhle úkony by se měly rozdělit do oddělených funkcí, jejichž struktura se od standardních funkcí liší ve dvou aspektech. Jednak se definují jako asynchronní, tedy místo "def" se napíše "async def", a jednak se v nich musí vyznačit místa, v nichž bude docházet k dlouhému čekání, příkazem "await". Slovo "await" lze přeložit do češtiny přeložit jako "očekávej", takže vlastně říkáme funkci, kde má "očekávat" nějakou návratovou hodnotu, která ale nepřijde hned.

Jakmile máte rozvržený program na funkce, jednou z možností je definovat jednotlivé úkony (nazývané "tasky"), naskládat je do seznamu a nechat program vykonat všechny tasky v seznamu s tím, že je může dělat asynchronně. To je možné udělat tak, že vytvoříte instanci objektu event loop, respektive získáte jedinou existující instanci objektu event loop, protože se jedná o singleton, pomocí `nazev = asyncio.get_event_loop()`, vytvoříte seznam tasků `moje_tasky = []; moje_tasky.append(nazev.create_task(moje_funkce()))` a následně pomocí `nazev.run_until_complete(funkce_s_mymi_tasky())` necháte vykonat všechny tasky v seznamu. `funkce_s_mymi_tasky()` by v tomto případě byla koncipovaná stylem `for task in moje_tasky: await task`.

## Zadání úkolů
0. Ujistěte se, že máte nainstalovaný Python interpreter alespoň verze 3.7. (https://www.python.org/downloads/) či novější a že máte nainstalované všechny následující moduly: asyncio, discord
`python -m pip install asyncio`
`python -m pip install discord`
1. Naklonujte si tento repozitář, nebo si ho stáhněte jako zip soubor. Pro tento "kurz" nebude zapotřebí nic commitovat a pushovat.
2. Vytvořte virtualní prostředí
```bash
py -m venv env
```
```bash
.\env\Scripts\activate
```
```bash
py -m pip install -r requirements.txt
```
3. Podle potřeby pip install potřebné knihovny
4. Připojte se na náš testovací server pomocí tohoto odkazu:  https://discord.gg/7WJK57dcCv
5. V adresáři *discordbot_templates* naleznete připravené základní skripty pro zprovoznění Discord bota.  Po připojení si řekněte Prokopovi nebo Filipovi o token pro jednoho z botů a zprovozněte ho tak, aby byl na Discordu zobrazený ve stavu *online*. (Stav online se značí tou zelenou tečkou vedle jména uživatele.)
6. (optional) V adresáři *presentation* se podívejte na rozdíly mezi implementací jednoduchého web-scrape skriptu bez využití asychronity a s jejím využitím.
7. (optional) Vytvořte si vlastní discord api token. https://discord.com/developers/docs/intro
8. Seznamte se s již implementovanými funkcemi vašeho bota a poté implementujte další konkurentně běžící funkce, které budou využívat Discord API. (Například příkaz, který bude zobrazovat aktuální počet uživatelů na serveru, nebo příkaz, který bude zobrazovat aktuální počet zpráv v kanálu.) Použijte Discord API dokumentaci: https://discordpy.readthedocs.io/en/stable/index.html . Alternativně můžete použít modul Pycord, jehož dokumentace je dostupná zde: https://docs.pycord.dev/en/stable/ 
9. Zlatým hřebem dnešní GUI hodiny by mělo být to, že se vám podaří implementovat bota, který bude využívat asynchronního programování. (Například scraper, který bude zobrazovat aktuální kurz bitcoinu, nebo scraper, který bude zobrazovat aktuální ceny Natural95 v různých benzínkách fungujících na území ČR.)
