# Webhooky DOJ V3 – návrh integrace

Webhook není náhradou bota: nemůže bezpečně obsluhovat soudní formuláře a schvalovací tlačítka.
Pro každý publikační kanál může administrátor vytvořit samostatný webhook, URL uložit
do Railway Variables a poté ho používat prostřednictvím `webhook_publisher.publish`.

## Proměnné
- `WEBHOOK_GOVERNMENT_DECREES` → `#státní-vyhlášky`
- `WEBHOOK_GOVERNMENT_LAWS` → `#státní-zákony`
- `WEBHOOK_GOVERNMENT_ANNOUNCEMENTS` → `#vládní-oznámení`
- `WEBHOOK_COURT_HEARINGS` → `#soudní-jednání`
- `WEBHOOK_COURT_VERDICTS` → `#soudní-rozsudky`
- `WEBHOOK_COURT_CASES` → `#soudní-případy`

Webhooky nejsou potřeba pro každý chat, auditní či soukromý kanál.
Nikdy nezveřejňovat webhook URL; kdo ji zná, může jejím prostřednictvím posílat zprávy.
Vytvoření webhooků na Discordu vyžaduje oprávnění `Manage Webhooks`.

**Stav:** Publikační modul je připraven, ale zatím není zapojený do všech příkazů,
automatické vytváření webhooků nebylo spuštěno a neproběhly integrační testy.
