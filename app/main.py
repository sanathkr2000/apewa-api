import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.db.database import database
from app.logging_conf import configure_logging
from fastapi.exception_handlers import http_exception_handler

from app.routers import userlogin
from app.routers.admin import admin_router
from app.routers.register import  register_router
from app.routers.user_routes import user_router
from app.routers.userlogin import user_login_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(register_router, prefix="/api/register")
app.include_router(user_login_router, prefix="/api/user", tags=["User Login"])
# app.include_router(admin_router, tags=["Admin"])  # ❌ Don't add a prefix here
app.include_router(user_router)

@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code}{exc.detail}")
    return await http_exception_handler(request, exc)