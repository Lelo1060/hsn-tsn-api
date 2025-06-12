from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class VehicleRequest(BaseModel):
    hsn: str
    tsn: str
    vin: str = ""

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest):
    prompt = f"""
Ich bin ein deutscher Kfz-Meister. Ich möchte ein Fahrzeug anhand folgender HSN/TSN identifizieren:

HSN: {data.hsn}
TSN: {data.tsn}

Gib mir basierend auf diesen Informationen bitte folgende Daten aus:
- Hersteller, Modell, genaue Motorbezeichnung
- Bauzeitraum (von/bis)
- Karosserieform
- Kraftstoffart
- Leistung (kW/PS)
- Hubraum
- Anzahl Türen & Sitze
- Getriebeart
- Besonderheiten oder bekannte Merkmale dieses Fahrzeugs

Wenn du keine passenden Daten findest, gib an: 'Fahrzeugdaten konnten nicht eindeutig ermittelt werden.'
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein hilfreicher Fahrzeug-Experte."},
                {"role": "user", "content": prompt}
            ]
        )
        return {"response": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": str(e)}
