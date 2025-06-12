
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VehicleInfoRequest(BaseModel):
    hsn: str
    tsn: str
    vin: str = ""

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleInfoRequest):
    hsn = data.hsn.strip()
    tsn = data.tsn.strip()
    vin = data.vin.strip()

    print(f"📥 Eingabe empfangen: HSN={hsn}, TSN={tsn}, VIN={vin}")

    # Verbessertes GPT-Prompt für Werkstattdaten
    prompt = f'''
Du bist ein Fahrzeugdaten-Experte für Werkstätten.
Identifiziere das Fahrzeug anhand der folgenden Schlüsselnummern:

HSN: {hsn}
TSN: {tsn}

Gib alle relevanten Daten für den Werkstattgebrauch aus:
- Hersteller und Modell
- Motortyp und Leistung (kW/PS)
- Baujahr oder Bauzeitraum
- Kraftstoffart
- Getriebeart (wenn bekannt)
- Ölmenge in Litern
- Ölsorte (z. B. 5W-30)
- Fahrgestellnummer (VIN), falls angegeben: {vin}

Antwort immer auf Deutsch.
'''

    try:
        print("🚀 Sende Anfrage an GPT...")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein präziser Fahrzeugdaten-Experte für HSN/TSN-Abfragen."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=700
        )
        result = response.choices[0].message.content.strip()
        print("✅ GPT-Antwort erhalten.")
        return {"response": result}

    except Exception as e:
        print(f"❌ GPT-Fehler: {str(e)}")
        return {"error": "Interner Fehler bei der Fahrzeugabfrage."}
