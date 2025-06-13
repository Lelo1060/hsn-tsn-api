
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

class VehicleRequest(BaseModel):
    hsn: str
    tsn: str

def scrape_from_hsn_tsn(hsn, tsn):
    url = f"https://www.hsn-tsn.de/{hsn.lower()}-{tsn.lower()}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return {"Fehler": f"Status {resp.status_code}"}
    soup = BeautifulSoup(resp.text, "html.parser")
    result = {}

    # Modell
    h1 = soup.find("h1")
    if h1:
        result["Modell"] = h1.text.strip()

    # Tabelle mit Details
    tbl = soup.find("table")
    if tbl:
        for tr in tbl.find_all("tr"):
            td = tr.find_all("td")
            if len(td) == 2:
                result[td[0].text.strip()] = td[1].text.strip()

    # Falls keine Tabelle, versuche <li>-Elemente
    if not result.get("Leistung"):
        for li in soup.find_all("li"):
            txt = li.text.strip()
            if "/" in txt and tsn.upper() in txt:
                parts = txt.split(",")
                result["Details"] = parts[0].strip() + ": " + " / ".join(parts[1:])
                break

    return result if result else {"Fehler": "Keine Daten extrahiert"}

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

    return {"Zusatzinfos": ergebnisse[:5]} if ergebnisse else {"Zusatzinfos": "Keine Details gefunden."}

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest):
    basisdaten = scrape_from_hsn_tsn(data.hsn, data.tsn)

    if "Modell" in basisdaten:
        zusatzdaten = scrape_additional_info(basisdaten["Modell"])
    else:
        zusatzdaten = {"Zusatzinfos": "Modellname fehlt, keine Recherche möglich."}

    return {
        "Basisdaten": basisdaten,
        **zusatzdaten
    }
