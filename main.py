import os
import sys
import time
import logging
import threading

import webview
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from api import data_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")
HOST = "127.0.0.1"
PORT = 8000


def resource_path(path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, path)


app = FastAPI(title="Weather Map")
app.mount(
    "/static",
    StaticFiles(directory=resource_path("static")),
    name="static",
)

templates = Jinja2Templates(directory=resource_path("templates"))


@app.get("/")
async def main_page():
    return FileResponse(resource_path("templates/world.html"))

class Coords(BaseModel):
    lat: float
    lon: float

@app.post("/weather")
async def weather(coords: Coords):
    try:
        return data_url(f"{coords.lat},{coords.lon}")
    except Exception as e:
        logger.exception("Weather error")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/weather_popup", response_class=HTMLResponse)
async def weather_popup(request: Request, lat: float, lon: float):
    try:
        data = data_url(f"{lat},{lon}")

        return templates.TemplateResponse(
            request=request,
            name="popup.html",
            context={
                "request": request,
                "coords": {
                    "lat": lat,
                    "lon": lon
                },
                "data": data
            }
        )
    except Exception as e:
        logger.exception("Popup error")
        return HTMLResponse(
            f"<h2>Ошибка: {e}</h2>",
            status_code=500
        )

def run_server():
    import uvicorn

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

if __name__ == "__main__":
    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    time.sleep(2)
    webview.create_window(
        title="Weather Map",
        url=f"http://{HOST}:{PORT}",
        width=1280,
        height=800,
        min_size=(900, 600),
        resizable=True
    )

    webview.start()