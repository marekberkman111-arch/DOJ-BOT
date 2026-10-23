"""Návrhový katalog RP předpisů inspirovaný právními oblastmi Kalifornie.

Nejde o doslovné znění ani závazný výklad California Codes.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Code:
    code: str
    title: str
    channel: str
    inspiration: str
    sections: tuple[str, ...]

CODES = (
    Code("UST", "Ústava státu San Andreas", "státní-zákony", "Principy dělby moci a základních práv", ("Základní práva", "Government", "Soudní moc", "Změny ústavy")),
    Code("TZ", "Trestní zákoník", "trestní-zákoník", "California Penal Code – tematická inspirace", ("Obecná část", "Majetkové činy", "Násilné činy", "Úřední činy", "Sankce")),
    Code("TR", "Trestní řád", "soudní-řád", "Kalifornské trestní řízení – tematická inspirace", ("Zadržení", "Obvinění", "Důkazy", "SW/AW", "Odvolání")),
    Code("SR", "Soudní řád", "soudní-řád", "California Rules of Court – tematická inspirace", ("Příslušnost soudů", "Jednání", "Rozsudky", "Opravné prostředky")),
    Code("OP", "Občanské právo", "státní-zákony", "California Civil Code – tematická inspirace", ("Smlouvy", "Vlastnictví", "Odpovědnost", "Náhrada škody")),
    Code("DP", "Dopravní předpisy", "státní-zákony", "California Vehicle Code – tematická inspirace", ("Řidičská oprávnění", "Provoz", "Přestupky", "Pokuty")),
    Code("PS", "Pravomoci státních složek", "státní-zákony", "Vybrané principy kalifornské veřejné správy", ("LSPD/LSSD", "SAHP", "LSFD/EMS", "Dispatch", "Kontrola pravomocí")),
    Code("VG", "Vládní a legislativní řád", "státní-zákony", "Principy legislativního procesu", ("Vyhlášky", "Nařízení", "Schvalování", "Účinnost", "Zrušení")),
)

def get_code(code: str):
    return next((item for item in CODES if item.code == code.strip().upper()), None)
