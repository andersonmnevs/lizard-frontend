from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import ops, hides, exports, images
from .db import get_db_connection

app = FastAPI(title="Lizard Web API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(ops.router)
app.include_router(hides.router)
app.include_router(exports.router)
app.include_router(images.router)


@app.get("/health")
def health_check():
    db_ok = False
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_ok = True
    except Exception:
        pass
    return {"status": "ok", "db_ok": db_ok}


# StaticFiles MUST be mounted after all API routers.
# html=True serves index.html for unmatched routes (required for react-router SPA).
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
