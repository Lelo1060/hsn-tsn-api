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

    prompt = f"""Fahrzeuginformationen für HSN: {data.hsn}, TSN: {data.tsn}, VIN: {data.vin or "nicht angegeben"}

Gib die Daten wie folgt aus:

Fahrzeug: [Marke Modell]
Motortyp: [z. B. 1.9 TDI]
Ölmenge: [z. B. 4,5 Liter]
Ölsorte: [z. B. 5W-30]
Produktionszeitraum: [z. B. 1999–2003]"""

    print("🚀 Sende Anfrage an GPT...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=250
        )
        answer = response.choices[0].message["content"].strip()
        print("✅ GPT-Antwort erhalten")
        return answer
    except Exception as e:
        print("❌ GPT-Fehler:", e)
        raise HTTPException(status_code=500, detail=str(e))
