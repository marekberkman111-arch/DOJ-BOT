"""Návrh původního herního trestního zákoníku San Andreas; nikoli právo Kalifornie."""
ARTICLES = {
 "1": ("Obecná ustanovení", "Tento zákoník upravuje výhradně pravidla trestní odpovědnosti v RP. O vině rozhoduje příslušný RP soud."),
 "2": ("Presumpce neviny", "Obviněný je považován za nevinného, dokud nebyla vina prokázána v řádném RP řízení."),
 "3": ("Právo na obhajobu", "Obviněný má právo znát obvinění, vyjádřit se a využít advokáta."),
 "4": ("Přiměřenost sankcí", "Sankce musí být přiměřená závažnosti, okolnostem a následkům skutku."),
 "101": ("Krádež", "Neoprávněné přisvojení cizí věci. Orientační RP sankce: pokuta 2 000–10 000 herních dolarů nebo 5–15 minut RP vězení."),
 "102": ("Loupež", "Přisvojení cizí věci za použití násilí či bezprostřední pohrůžky. Orientační RP sankce: 15–35 minut RP vězení."),
 "103": ("Podvod", "Úmyslné uvedení jiné osoby v omyl za účelem majetkového prospěchu. Orientační RP sankce: pokuta 5 000–25 000 herních dolarů nebo 10–25 minut RP vězení."),
 "104": ("Ublížení na zdraví", "Úmyslné způsobení újmy na zdraví jiné osoby. Orientační RP sankce: 10–30 minut RP vězení."),
 "105": ("Vražda", "Úmyslné usmrcení jiné osoby. Orientační RP sankce: 40–90 minut RP vězení."),
 "106": ("Útěk z vazby", "Úmyslný útěk z řádně nařízené RP vazby. Orientační RP sankce: 10–25 minut RP vězení."),
 "107": ("Maření výkonu úředního rozhodnutí", "Úmyslné porušení vykonatelného rozhodnutí RP soudu. Orientační RP sankce: 10–20 minut RP vězení."),
 "108": ("Úplatkářství", "Nabídnutí, poskytnutí či přijetí prospěchu za zneužití úřední pravomoci. Orientační RP sankce: 15–40 minut RP vězení."),
 "201": ("Soudní příkaz k prohlídce", "Prohlídka vyžadující soudní příkaz musí vycházet z konkrétních důvodů a vymezit místo a předmět. NO-KNOCK ENTRY musí být výslovně schváleno soudcem."),
 "202": ("Zatýkací příkaz", "Zatýkací příkaz identifikuje hledanou osobu, důvody vydání a schvalujícího soudce."),
 "203": ("Odvolání", "Účastník řízení může podat odvolání podle pravidel serveru; o odvolání nesmí rozhodovat stejný soudce, pokud pravidla nestanoví jinak."),
}

def get_article(number: str):
    return ARTICLES.get(number.strip().removeprefix("§").strip())
