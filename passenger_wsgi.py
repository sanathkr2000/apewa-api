# # # passenger_wsgi.py (Root-level)
# # from fastapi import FastAPI
# # from starlette.middleware.wsgi import WSGIMiddleware
# # from flask import Flask
# #
# # # Import your FastAPI app
# # from app.main import app as fastapi_app
# #
# # # Wrap FastAPI with Flask + WSGIMiddleware
# # flask_app = Flask(__name__)
# # flask_app.wsgi_app = WSGIMiddleware(fastapi_app)
# #
# # # cPanel looks for 'application'
# # application = flask_app
#
#
# from fastapi import FastAPI
# from asgiref.wsgi import WsgiToAsgi
#
# app = FastAPI()
#
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
#
# application = WsgiToAsgi(app)



# import logging
# from contextlib import asynccontextmanager
# from fastapi import FastAPI, HTTPException
# from starlette.responses import JSONResponse
# from fastapi.exception_handlers import http_exception_handler
# from asgiref.wsgi import WsgiToAsgi
#
# from app.db.database import database
# from app.logging_conf import configure_logging
#
# # Routers
# from app.routers.register import register_router
# from app.routers.userlogin import user_login_router
# from app.routers.admin import admin_router
# from app.routers.user_routes import user_router
#
# logger = logging.getLogger(__name__)
#
# # Lifespan for startup and shutdown tasks
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     configure_logging()
#     await database.connect()
#     yield
#     await database.disconnect()
#
# # Main FastAPI app
# app = FastAPI(
#     title="APEWA Backend APIs",
#     version="1.0.0",
#     description="Official API for APEWA platform",
#     openapi_url="/apewa/openapi.json",
#     docs_url="/docs",
#     redoc_url="/redoc",
#     lifespan=lifespan,
#     root_path="/api"  # Central prefix for all routes
# )
#
# # Root endpoint (optional)
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
#
# # Routers - no need to prefix with `/api`
# app.include_router(register_router, prefix="/register")
# app.include_router(user_login_router, prefix="/user", tags=["User Login"])
# app.include_router(admin_router, prefix="/admin", tags=["Admin Users"])
# app.include_router(user_router)
#
# # Exception handler
# @app.exception_handler(HTTPException)
# async def http_exception_handle_logging(request, exc):
#     logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
#     return await http_exception_handler(request, exc)
#
# # Required if using WSGI hosting (e.g., cPanel)
# application = WsgiToAsgi(app)

