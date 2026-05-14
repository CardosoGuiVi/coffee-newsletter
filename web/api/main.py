"""
FastAPI backend para a newsletter
POST /subscribe - inscreve email
GET /stats - retorna número de inscritos
POST /unsubscribe - desinscreve email
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
import sqlite3
from pathlib import Path
from contextlib import contextmanager


BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR /"static"


app = FastAPI(title="Coffee Newsletter")

# app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# app.mount("/src", StaticFiles(directory="src"), name="src")

# SOURCE_PATH: str = "/src/api"

# ── Banco de dados ──────────────────────────────────────────────────────────

DB_PATH = Path("newsletter.db")


def init_db():
    """Cria a tabela se não existir."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                subscribed INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                unsubscribed_at TIMESTAMP
            )
        """)
        conn.commit()


@contextmanager
def get_db():
    """Context manager para conexões com o banco."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


init_db()


# ── Models ──────────────────────────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    email: EmailStr


class UnsubscribeRequest(BaseModel):
    email: EmailStr


class StatsResponse(BaseModel):
    total_subscribers: int
    joined_this_week: int


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.post("/api/subscribe")
def subscribe(data: SubscribeRequest):
    """Inscreve um novo email na newsletter."""
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO subscribers (email, subscribed, created_at)
                VALUES (?, 1, CURRENT_TIMESTAMP)
            """, (data.email,))
            conn.commit()
        return {"message": "Inscrição realizada com sucesso!", "email": data.email}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Este email já está inscrito na newsletter"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats() -> StatsResponse:
    """Retorna estatísticas da newsletter."""
    with get_db() as conn:
        # Total de inscritos ativos
        total = conn.execute(
            "SELECT COUNT(*) as count FROM subscribers WHERE subscribed = 1"
        ).fetchone()["count"]
        
        # Inscritos nesta semana
        week = conn.execute("""
            SELECT COUNT(*) as count FROM subscribers 
            WHERE subscribed = 1 AND created_at >= datetime('now', '-7 days')
        """).fetchone()["count"]
    
    return StatsResponse(total_subscribers=total, joined_this_week=week)


@app.post("/api/unsubscribe")
def unsubscribe(data: UnsubscribeRequest):
    """Desinscreve um email da newsletter."""
    with get_db() as conn:
        result = conn.execute(
            "UPDATE subscribers SET subscribed = 0, unsubscribed_at = CURRENT_TIMESTAMP WHERE email = ?",
            (data.email,)
        )
        conn.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Email não encontrado na newsletter"
            )
    
    return {"message": "Você foi removido da newsletter", "email": data.email}


@app.get("/")
def root():
    """Serve a página principal."""
    return FileResponse(STATIC_DIR / "index.html")


# Serve os arquivos estáticos
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)