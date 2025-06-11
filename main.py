import openai
import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS-Einstellungen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class VehicleRequest(BaseModel):
    hsn: str
    tsn: str
    vin: str = ""

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest, request: Request):
    print("📥 Eingabe empfangen:", data.model_dump())

    if not data.hsn or not data.tsn:
        print("⚠️ Fehlende Eingabe: HSN oder TSN")
        raise HTTPException(status_code=400, detail="HSN und TSN sind Pflichtfelder.")

    prompt = f"""Du bist ein technischer Assistent mit Zugriff auf Fahrzeuginformationen anhand von deutschen Schlüsselnummern.

Beachte:
- HSN steht für die Hersteller-Schlüsselnummer
- TSN ist die Typ-Schlüsselnummer
- Diese Kombination ist eindeutig einem Fahrzeugtyp in Deutschland zugeordnet

Deine Aufgabe ist:
→ Anhand der HSN/TSN möglichst exakt das Fahrzeug zu benennen und technische Daten bereitzustellen.

Angaben vom Kunden:
HSN: {data.hsn}
TSN: {data.tsn}
Fahrgestellnummer (VIN): {data.vin or "nicht angegeben"}

Wenn du diese Schlüsselnummer nicht eindeutig zuordnen kannst, sag das deutlich. Wenn sie plausibel sind, liefere bitte alle verfügbaren Werkstattdaten:

• Fahrzeug: Marke, Modell, Baureihe  
• Baujahr bzw. Produktionszeitraum  
• Motortyp und Motorcode  
• Kraftstoffart (Diesel, Benzin, etc.)  
• Getriebeart (Schaltgetriebe, Automatik etc.)  
• Leistungsangabe in kW/PS  
• Hubraum in ccm  
• Anzahl Zylinder  
• Antriebsart (z. B. Frontantrieb)  
• Ölmenge (in Litern)  
• Ölsorte (z. B. 5W-30 Longlife)  
• Inspektionsintervalle (km oder Monate)  
• Zahnriemen-/Steuerkette: Typ & Wechselintervall (falls bekannt)  
• Besonderheiten oder bekannte Schwachstellen  
• Beliebte Ersatzteile oder Wartungsaufwand

Format:  
Fahrzeug: ...  
Motortyp: ...  
Kraftstoffart: ...  
Ölmenge: ...  
Ölsorte: ...  
Getriebe: ...  
...

Wichtig:
- Antworte ausschließlich auf Basis deines Wissens über HSN/TSN
- Erfinde keine Daten, wenn du dir nicht sicher bist
- Gib bei Unsicherheit lieber realistische Standardwerte oder "nicht bekannt" an
- Verwende eine sachliche, technische Sprache wie unter Kfz-Meistern üblich
"""

    print("🚀 Sende Anfrage an GPT...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=700
        )
        answer = response.choices[0].message["content"].strip()
        print("✅ GPT-Antwort erhalten")
        return answer
    except Exception as e:
        print("❌ GPT-Fehler:", e)
        raise HTTPException(status_code=500, detail=str(e))
