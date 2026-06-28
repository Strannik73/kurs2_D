import io
import os
import logging
import ssl
import sys
import threading
import webbrowser
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from api import data_url
from crt import generate_key_and_cert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

def resource_path(path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, path)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Weather Map API")
app.mount("/static",StaticFiles(directory=os.path.join(BASE_DIR, "static")),name="static")
templates = Jinja2Templates(directory=resource_path("templates"))

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("world.html", {"request": request})

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


@app.get("/weather_popup", response_class=HTMLResponse)
async def weather_popup(request: Request, lat: float, lon: float):
    try:
        data = data_url(f"{lat},{lon}")

        return templates.TemplateResponse(
            "popup.html",
            {
                "request": request,
                "coords": {"lat": lat, "lon": lon},
                "data": data
            }
        )
    except Exception as e:
        logger.exception("Popup error")
        return HTMLResponse(f"<div>Ошибка: {e}</div>", status_code=500)
    
def open_browser():
    webbrowser.open("https://127.0.0.1:8000")


def run_server():
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
    
if __name__ == "__main__":
    if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):
        generate_key_and_cert()


    threading.Timer(1.2, open_browser).start()

    run_server()