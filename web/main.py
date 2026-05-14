from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from web.api.v1 import health

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR /"static"


app = FastAPI(title="Coffee Newsletter")

app.include_router(health.router, prefix="/v1")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def main():
    return FileResponse(STATIC_DIR / "index.html")
