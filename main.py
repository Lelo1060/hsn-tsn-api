
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class VehicleRequest(BaseModel):
    hsn: str
    tsn: str

def ask_gpt(hsn, tsn):
    prompt = (
        f"Ich habe die Schlüsselnummer HSN {hsn} und TSN {tsn}. "
        f"Bitte nenne mir das Fahrzeugmodell, Baujahre, Leistung, Hubraum, Kraftstoffart, "
        f"und wenn möglich auch Ölmenge und technische Daten. "
        f"Formatiere die Antwort als JSON-ähnliche Liste mit klaren Werten."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei GPT-Anfrage: {str(e)}"

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest):
    gpt_response = ask_gpt(data.hsn, data.tsn)
    return {"Antwort": gpt_response}
