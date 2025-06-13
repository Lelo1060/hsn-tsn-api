
# CarDecoder Backend mit Webscraper

Dieses FastAPI-Backend nutzt zwei Webscraper:
1. Holt Fahrzeugdaten anhand von HSN/TSN von https://hsn-tsn.de
2. Recherchiert zusätzliche technische Infos per Google-Suche

## Endpunkt
`GET /hsn-tsn?hsn=0005&tsn=BLH`

## Start (lokal)
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
