# SW / AW – schvalovací pravidla (potvrzeno uživatelem)

## Oprávnění
- Žadatel: role `LSPD`, `LSSD` nebo `State Prosecutor`.
- Schvalující: role `Judge`, `Supreme Judge`, `Chief Judge`.
- Administrátor má technické oprávnění pro správu a testování.
- Před ostrým nasazením ověřit, že jsou názvy rolí na serveru přesně shodné.

## Proces
1. Žadatel vyplní SW/AW a odešle žádost.
2. Bot vytvoří evidenční číslo, uloží obsah a odešle soudcům náhled bez data vystavení a podpisu.
3. Soudce zvolí Schválit nebo Zamítnout.
4. Zamítnutí **vyžaduje vyplnění důvodu**; žádost je uzavřena jako zamítnutá, bez finálního PDF.
5. Při schválení bot atomicky zaznamená identitu soudce a čas schválení; datum vystavení v dokumentu = datum schválení.
6. Teprve schválená žádost získá finální PDF a informaci o schválení.

## Search Warrant
- Volba `NO-KNOCK ENTRY` ANO/NE je součástí žádosti a viditelná soudci.
- Volba nesmí být změněna po schválení bez nové žádosti.

## Šablony
- Použít originální uživatelem dodané PNG jako podklad, nikoli překreslené obrázky.
- Nečitelné části SW nevydávat za původní text.
- AW: jméno soudce na původní pravé podpisové lince nad popiskem.
- Pouze SW/AW jsou PDF, ostatní dokumenty Discord embed.

## Stav implementace
Tento soubor je schválená specifikace. `warrant_policy.py` obsahuje kontrolu rolí a důvodu.
Celé Discord formuláře, persistence a PDF generátor zatím čekají na implementaci a testování.
