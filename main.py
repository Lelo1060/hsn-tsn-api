
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion: hier nur deine Domain erlauben!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VehicleRequest(BaseModel):
    hsn: str
    tsn: str
    vin: str = ""

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest):
    print(f"📥 Eingabe empfangen: {{'hsn': '{data.hsn}', 'tsn': '{data.tsn}', 'vin': '{data.vin}'}}")
    try:
        prompt = f""" 
Du bist ein technischer Assistent mit spezialisiertem Wissen über die deutsche Fahrzeugdatenbank und die Webseite hsn-tsn.de.

Du kennst typische Fahrzeugzuordnungen anhand der Schlüsselnummern:

- HSN = Herstellerschlüsselnummer (z. B. 0603)
- TSN = Typschlüsselnummer (z. B. 471)
- Diese Kombination ergibt ein eindeutiges Fahrzeugmodell.

🔍 Eingabe vom Nutzer:
HSN: {data.hsn}
TSN: {data.tsn}
VIN: {data.vin or "nicht angegeben"}

Deine Aufgabe:
1. Erkenne das Fahrzeugmodell anhand von HSN & TSN
2. Gib die wichtigsten technischen Werkstattdaten an
3. Falls dir die Kombination nicht eindeutig bekannt ist: Sag klar, dass du keine genaue Info liefern kannst, und verweise auf hsn-tsn.de

📦 Format der Antwort:
Fahrzeug:  
Produktionszeitraum:  
Motortyp:  
Kraftstoffart:  
Getriebe:  
Leistung:  
Hubraum:  
Zylinder:  
Antrieb:  
Ölmenge:  
Ölsorte:  
Intervall Ölwechsel:  
Steuerkette/Zahnriemen:  
Bekannte Schwächen:  
Empfohlene Ersatzteile:  

⚠️ Wichtige Regeln:
- Wenn du die Kombination nicht kennst, **nicht raten**
- Antworte sachlich, wie ein Werkstattmeister
- Verwende keine Fantasie, nur bekannte Daten aus deiner GPT-Trainingserfahrung
"""

        print("🚀 Sende Anfrage an GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        result = response.choices[0].message["content"]
        print("✅ GPT-Antwort empfangen.")
        return {"result": result}

    except Exception as e:
        print(f"❌ GPT-Fehler: {str(e)}")
        return {"error": "Fehler beim Abrufen der Fahrzeugdaten."}
