from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from apps.api.routes.v1 import health, newsletter
from packages.core import settings

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR.parent / "web"
IMAGES_DIR = STATIC_DIR / "images"


app = FastAPI(title="Coado")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [settings.API_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/v1")
app.include_router(newsletter.router, prefix="/v1")


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="web")
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")


@app.get("/")
def main():
    return FileResponse(STATIC_DIR / "index.html")
