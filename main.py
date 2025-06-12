
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    try:
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "user",
                "content": (
                    f"Du bist ein Experte für Fahrzeuginformationen. "
                    f"Ich gebe dir eine HSN und TSN (Schlüsselnummern aus einem deutschen Fahrzeugschein). "
                    f"""Bitte analysiere diese Kombination:

"
                    f"HSN: {hsn}
"
                    f"TSN: {tsn}
"
                    f"VIN (optional): {vin}

"
                    f"Antworte bitte wie im Chat mit allen relevanten Daten:
"
                    f"- Marke und Modell
"
                    f"- Baujahr oder Bauzeitraum
"
                    f"- Motortyp (z. B. 1.9 TDI)
"
                    f"- Leistung (kW/PS)
"
                    f"- Kraftstoffart
"
                    f"- Getriebeart (wenn möglich)
"
                    f"- Ölsorte (z. B. 5W-30)
"
                    f"- Ölmenge in Litern
"
                    f"- Besonderheiten oder bekannte Bauform

"
                    f"Falls du dir nicht sicher bist, dann sag:
"
                    f"„Die Schlüsselnummer {hsn}/{tsn} konnte nicht sicher zugeordnet werden. Bitte auf www.hsn-tsn.de prüfen.“
"
                    f"Sprich in natürlichem, klarem Deutsch wie in einem Chat."
                )
            }
        ]


