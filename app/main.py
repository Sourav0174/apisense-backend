from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.exception_handlers import register_exception_handlers
from app.api.health import router as health_router
from app.core.config import get_settings
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "APISense Backend is running 🚀"}