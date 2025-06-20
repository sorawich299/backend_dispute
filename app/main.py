from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routes import upload, dashboard, export
from app.auth import IPBlockerMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secret-key")
app.add_middleware(IPBlockerMiddleware)

app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(export.router)