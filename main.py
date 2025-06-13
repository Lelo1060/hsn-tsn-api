
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class VehicleRequest(BaseModel):
    hsn: str
    tsn: str

def ask_gpt(hsn, tsn):
    prompt = (
        f"Ich habe die Schlüsselnummer HSN {hsn} und TSN {tsn}. "
        f"Bitte nenne mir das Fahrzeugmodell, Baujahre, Leistung, Hubraum, Kraftstoffart, "
        f"und wenn möglich auch Ölmenge und technische Daten. "
        f"Gib die Antwort im JSON-ähnlichen Format."
    )

    try:
        chat = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei GPT-Anfrage: {str(e)}"

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest):
    gpt_response = ask_gpt(data.hsn, data.tsn)
    return {"Antwort": gpt_response}
