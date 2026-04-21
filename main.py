import os
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from api import data_url

# -------------------------
# LOGGING
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI()

# MAIN PAGE (world map)
@app.get("/", response_class=HTMLResponse)
async def main_page():
    try:
        with open("world.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>world.html не найден</h1>", status_code=404)

#  WEATHER API (координаты с карты)

class Coords(BaseModel):
    lat: float
    lon: float

@app.post("/weather")
async def weather(coords: Coords):
    try:
        return data_url(f"{coords.lat},{coords.lon}")
    except Exception as e:
        logger.exception("Ошибка погоды")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))

    logger.info(f"Запуск на {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)