from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class VehicleRequest(BaseModel):
    hsn: str
    tsn: str
    vin: str = None
    language: str = "de"

@app.post("/vehicle-info")
async def get_vehicle_info(data: VehicleRequest):
    if data.language == "de":
        prompt = f"""Gib mir bitte alle verfügbaren technischen und fahrzeugspezifischen Informationen zum Fahrzeug mit:
- HSN: {data.hsn}
- TSN: {data.tsn}""" + (f"\n- VIN: {data.vin}" if data.vin else "") + """

Bitte liefere die Antwort strukturiert und gegliedert mit folgenden Punkten (sofern verfügbar):

1. Marke, Modell, Baujahr, Typ, Fahrzeugklasse  
2. Motorcode, Getriebetyp, Leistung, Drehmoment  
3. Kraftstoffart, Abgasnorm, Katalysator  
4. Motoröl-Spezifikation, Motorölmenge (mit/ohne Filter)  
5. Getriebeöl, Kühlmittel, Bremsflüssigkeit, Servoöl  
6. Zündkerzen, Luftfilter, Innenraumfilter, Kraftstofffilter  
7. Reifendruck vorne/hinten, Reifengröße, Felgengröße  
8. Wartungsintervalle (Öl, Bremsflüssigkeit, Zahnriemen etc.)  
9. Batteriegröße, Lichtmaschine, Klimaanlage  
10. Sonstige technische Hinweise oder Besonderheiten

Antworte auf Deutsch.
"""
    else:
        prompt = f"""Give me all available technical and vehicle-specific information for:
- HSN: {data.hsn}
- TSN: {data.tsn}""" + (f"\n- VIN: {data.vin}" if data.vin else "") + """

Please return a structured and organized response with these points (if available):

1. Make, model, year, type, vehicle class  
2. Engine code, transmission type, power, torque  
3. Fuel type, emission standard, catalytic converter  
4. Engine oil specification, engine oil quantity (with/without filter)  
5. Gearbox oil, coolant, brake fluid, power steering fluid  
6. Spark plugs, air filter, cabin filter, fuel filter  
7. Tire pressure front/rear, tire size, rim size  
8. Maintenance intervals (oil, brake fluid, timing belt etc.)  
9. Battery size, alternator, air conditioning system  
10. Other technical notes or special features

Respond in English.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000
    )

    return {"data": response.choices[0].message["content"]}
