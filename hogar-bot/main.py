import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from bot.core import scheduler
from bot.db import migrations
from bot.db.database import create_tables
from bot.db.seed import run as run_seed
from bot.whatsapp.router import router as whatsapp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Arrancando hogar-bot...")
    os.makedirs("data", exist_ok=True)
    create_tables()
    migrations.run()
    run_seed()
    scheduler.setup()
    yield
    scheduler.shutdown()
    logger.info("hogar-bot apagado.")


app = FastAPI(title="hogar-bot", lifespan=lifespan)
app.include_router(whatsapp_router)


@app.get("/health")
def health():
    return {"status": "ok"}
