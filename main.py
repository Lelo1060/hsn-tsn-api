
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen (API-Schlüssel etc.)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS-Konfiguration (für die Android-App)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion begrenzen!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datenmodell für den POST-Body
class VehicleRequest(BaseModel):
    hsn: str
    tsn: str
    vin: str = ""

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest):
    print(f"📥 Anfrage erhalten: HSN={data.hsn}, TSN={data.tsn}, VIN={data.vin}")
    try:
        # Perfekter Prompt für realistische GPT-Antwort
        prompt = f"""
Du bist ein technischer Fahrzeugdaten-Assistent mit speziellem Wissen über die deutsche Fahrzeugdatenbank und die Website hsn-tsn.de.

Deine Aufgabe ist es, ein Fahrzeug anhand der HSN- und TSN-Kombination möglichst genau zu identifizieren. Wenn möglich, liefere bitte auch technische Werkstattinformationen.

🔎 Eingabe:
HSN: {data.hsn}
TSN: {data.tsn}
VIN: {data.vin or "nicht angegeben"}

Wenn du dir nicht sicher bist, gib dies bitte ehrlich an.

📋 Format der Antwort:
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

Regeln:
- Keine Vermutungen. Nur antworten, wenn du dir sicher bist.
- Wenn die Kombination unbekannt ist, bitte auf hsn-tsn.de verweisen.
- Sprich wie ein Werkstattmeister, nicht wie ein Chatbot.
"""

        print("🚀 GPT-Anfrage wird gesendet...")

        # GPT-Anfrage mit GPT-4 und niedriger Kreativität
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        antwort = response.choices[0].message["content"]
        print("✅ GPT-Antwort erhalten")
        return {"result": antwort}

    except Exception as e:
        print(f"❌ Fehler bei der GPT-Abfrage: {e}")
        return {"error": "Interner Fehler bei der Verarbeitung der Fahrzeugdaten."}
