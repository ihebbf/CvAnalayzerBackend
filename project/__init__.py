from fastapi import FastAPI
from starlette.middleware import Middleware

from fastapi.middleware.cors import CORSMiddleware

from project.utils.config import settings

app = FastAPI()

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
from project.Controllers import *
from project.models import *