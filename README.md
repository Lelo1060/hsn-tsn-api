
# GPT-gestützte Fahrzeug-API (HSN/TSN → Fahrzeuginfo)

## Beschreibung
Diese FastAPI nutzt die OpenAI GPT-API, um zu HSN/TSN-Kombinationen Fahrzeugdaten zu ermitteln.

## Endpunkt
POST /vehicle-info

### Beispiel JSON-Body:
{
  "hsn": "0583",
  "tsn": "aaw"
}

## Antwort
Ein von GPT generierter Text mit technischen Fahrzeuginformationen.

## .env
Leg eine Datei `.env` an mit:
OPENAI_API_KEY=dein_api_key
