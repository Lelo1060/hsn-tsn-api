
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

    # Suche nach <li> mit passender HSN/TSN-Kombi
    for li in soup.find_all("li"):
        text = li.text.strip()
        if text.startswith(f"{hsn}/{tsn.upper()}"):
            parts = [p.strip() for p in text.split(",")]
            if len(parts) >= 6:
                result["Modell"] = f"{parts[1]} {parts[2]}"
                result["Leistung"] = parts[3]
                result["Hubraum"] = parts[4]
                result["Kraftstoff"] = parts[5]
            result["Originalzeile"] = text
            break

    return result if result else {"Fehler": "Keine passenden Fahrzeugdaten gefunden."}

def scrape_additional_info(modellbezeichnung):
    query = modellbezeichnung + " ölmenge motor technische daten"
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
        if any(w in text.lower() for w in ["öl", "liter", "füllmenge", "ölmenge", "motoröl", "viskosität"]):
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
