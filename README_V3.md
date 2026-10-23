# DOJ Management V3 – první vývojová verze

Centrální RP systém pro Government a Department of Justice na Discordu.

## Stav
Tato větev obsahuje **první funkční základ**, nikoli hotovou produkční verzi.
Zatím fungují: instalační příkaz, základní soudní případ s oznámením termínu,
vyhledání spisu a návrh státní vyhlášky jako Discord embed.

## Spuštění
1. Python 3.11+; `pip install -r requirements.txt`.
2. Nastavte `DISCORD_TOKEN`, `DISCORD_GUILD_ID=1558209495841243136`.
3. `python main.py`.
4. Přidejte bota na server s scopes `bot` a `applications.commands`, oprávněními Manage Channels, Manage Roles, View Channels, Send Messages a Embed Links.
5. Administrátor ručně spustí `/instalovat_server`. Instalace je opakovatelná a nesmaže stávající kanály.

## Příkazy
- `/instalovat_server` – administrátorská instalace kategorií, kanálů a rolí
- `/soudni_pripad` – formulář soudního případu, jednání do jiného kanálu
- `/spis` – vyhledání případu
- `/vyhlaska` – návrh vyhlášky jako Discord zpráva

## Bezpečnost a omezení
- Nahrávejte token jen do Railway Variables, nikdy do GitHubu.
- SQLite je vhodná pro lokální vývoj; pro Railway produkci použijeme PostgreSQL.
- Přístupová práva a schvalování vyhlášek ještě vyžadují dopracování.
- PDF budou **výhradně** pro Search Warrant a Arrest Warrant, zatím nejsou implementovány.
- Původní SW/AW grafické předlohy zatím nejsou integrovány.
- RP legislativa, odvolání, rozsudky, změny termínů a auditní UI jsou plánované.
- Dokumenty a ustanovení mají pouze RP účel.

## Druhá etapa – nové příkazy
- `/paragraf` – zobrazení ustanovení RP zákoníku
- `/zakonik` – přehled návrhu paragrafů
- `/zmenit_jednani` – změna termínu s novým oznámením
- `/rozsudek` – zveřejnění rozsudku jako Discord embed
- `/schvalit_vyhlasku` – guvernér schválí návrh, výsledek je Discord embed

Zákoník je **neodsouhlasený RP návrh** s orientačními herními sankcemi.
Soudní spisy mohou vyhledávat pouze oprávněné role.
Zatím nejsou implementovány: editace starých oznámení, soudní odvolání, úplné schvalovací workflow,
produkční PostgreSQL, SW/AW PDF a integrační testy.
