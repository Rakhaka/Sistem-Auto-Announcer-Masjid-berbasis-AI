import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import APP_PORT
from app.routers import (
    auth_router, health, status, announce,
    playback, studio, schedules, logs, audio, data,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import init_db, catat_log
    from app.scheduler_service import start_scheduler
    init_db()
    catat_log("sistem", "Sistem Dinyalakan", "Server Announcer Pro Berhasil Booting.", "System")
    start_scheduler()
    print(f"\n[SYSTEM] Announcer Pro API siap di port {APP_PORT}")
    yield
    from app.scheduler_service import scheduler
    scheduler.shutdown(wait=False)

app = FastAPI(
    title="Announcer Pro API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [auth_router, health, status, announce, playback, studio, schedules, logs, audio, data]
for r in routers:
    app.include_router(r.router, prefix="/api", tags=getattr(r, "tags", []))
