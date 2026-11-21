# Bútorpiaci kutatás – eszközök

A heti ügynökkör szkriptjei. Az adatbázis NEM itt van, hanem a gépen: `Dokumentumok\Piackutatás\adatbazis`.

| Fájl | Mire való |
|---|---|
| `ld.py` | böngészőből kimentett listák (`b*.txt`) → nyers JSONL |
| `p.py` | árak kiolvasása, pénznemek (FX), típus- és ársáv-besorolás |
| `feldolgoz.py` | nyers JSONL → `termekek.csv`, `kepek_lista.csv`, `arelozmeny.csv`; ismert linknél csak árfrissítés |
| `web_epit.py` | `termekek.csv` + képek → weboldal `termekek.json` + `th/` bélyegképek |
| `terkep_frissit.py` | a bútorpiac-térkép beágyazott adatainak frissítése (`terkep_sablon.html`) |
| `riport_pdf.py` + `i18n3.py` | háromnyelvű PDF-kimutatás (HU/EN/DE) |

`b*.txt` formátum: fejléc `ORSZÁG|Áruház|https://alap.url`, utána soronként `/utvonal | látható szöveg árakkal [KARTYA kártyás ár] | kép URL`.
