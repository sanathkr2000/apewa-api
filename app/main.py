
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, FileResponse
from fastapi.exception_handlers import http_exception_handler
from asgiref.wsgi import WsgiToAsgi
from starlette.staticfiles import StaticFiles

from app.db.database import database
from app.logging_conf import configure_logging
from app.routers import forgot_password_router

# Routers
from app.routers.register import register_router
from app.routers.userlogin import user_login_router
from app.routers.admin import admin_router
from app.routers.user_routes import user_router
from app.routers.password_routes import password_router
from app.routers.forgot_password_router import forgot_password_router  # FIXED
from app.config import base_config  # import the resolved config object
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()

# FastAPI app setup
app = FastAPI(
    title="APEWA Backend APIs",
    version="1.0.0",
    description="Official API for APEWA platform",
    docs_url="/docs" if base_config.ENV_STATE == "dev" else None,
    redoc_url="/redoc" if base_config.ENV_STATE == "dev" else None,
    openapi_url="/openapi.json" if base_config.ENV_STATE == "dev" else None,
    lifespan=lifespan,
    root_path="/api"
)

# Allow all CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "APEWA Backend APIs"}

# Routers - no need to prefix with `/api`
app.include_router(register_router, prefix="/register")
app.include_router(user_login_router, prefix="/user", tags=["User Login"])
app.include_router(admin_router, prefix="/admin", tags=["Admin Users"])
app.include_router(user_router)
app.include_router(password_router)
app.include_router(forgot_password_router)

# Serve static files from 'apewa-api/uploads'

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)

# Required if using WSGI hosting (e.g., cPanel)
application = WsgiToAsgi(app)