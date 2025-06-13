
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def scrape_from_hsn_tsn(hsn, tsn):
    url = f"http://www.hsn-tsn.de/{hsn.lower()}-{tsn.lower()}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"Fehler": "HSN/TSN-Seite nicht gefunden."}

    soup = BeautifulSoup(response.text, "html.parser")
    result = {}

    # Titel (z. B. "BMW 1er 118d")
    title = soup.find("h1")
    if title:
        result["Modell"] = title.get_text(strip=True)

    table = soup.find("table")
    if table:
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                val = cols[1].get_text(strip=True)
                result[key] = val

    return result

def scrape_additional_info(modellbezeichnung):
    query = modellbezeichnung + " technische daten"
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"Zusatzinfos": "Keine weiteren Infos abrufbar."}

    soup = BeautifulSoup(response.text, "html.parser")
    snippets = soup.find_all("span")

    ergebnisse = []
    for s in snippets:
        text = s.get_text(strip=True)
        if any(w in text.lower() for w in ["kw", "ps", "baujahr", "verbrauch", "hubraum"]):
            ergebnisse.append(text)

    if not ergebnisse:
        return {"Zusatzinfos": "Keine Details gefunden."}

    return {"Zusatzinfos": ergebnisse[:5]}  # max. 5 Zusatzinfos

@app.get("/hsn-tsn")
async def get_vehicle_data(hsn: str, tsn: str):
    basisdaten = scrape_from_hsn_tsn(hsn, tsn)

    if "Modell" in basisdaten:
        zusatzdaten = scrape_additional_info(basisdaten["Modell"])
    else:
        zusatzdaten = {"Zusatzinfos": "Modellname fehlt, keine Recherche möglich."}

    return {
        "Basisdaten": basisdaten,
        **zusatzdaten
    }
