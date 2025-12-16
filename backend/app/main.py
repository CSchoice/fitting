from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_session, init_db
from app.logger import setup_logging
from app.routers import avatar_presets, clothes, fitting, session as session_router
from app.seeds import seed_avatar_presets


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    # Seed presets if empty
    async with get_session() as session:
        await seed_avatar_presets(session)
    yield


app = FastAPI(title="Virtual Fitting Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clothes.router)
app.include_router(avatar_presets.router)
app.include_router(fitting.router)
app.include_router(session_router.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

