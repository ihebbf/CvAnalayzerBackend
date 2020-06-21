
__author__ = "IhebBenFraj"
__version__ = "1"
__email__ = "ihebeddine.benfraj@sofrecom.com"

from starlette.middleware.cors import CORSMiddleware

from project import app
import uvicorn

app.add_middleware(
    CORSMiddleware,
    allow_origins={"*"},
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

