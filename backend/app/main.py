from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import datasets, dashboards, insights
from app.core.config import settings
from app.core.logging import setup_logging
from app.api import users,auth
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

from app.core.database import get_users_collection




app = FastAPI(
    title="Smart Dashboard Backend",
    description="Backend system for auto-generating dashboards and insights from datasets",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(dashboards.router)
app.include_router(insights.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.on_event("startup")
def on_startup():
    settings.DATA_DIR.mkdir(exist_ok=True)
    settings.DATASET_DIR.mkdir(exist_ok=True)
    settings.DASHBOARD_DIR.mkdir(exist_ok=True)
    setup_logging()


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/db")
def db_health():
    users = get_users_collection()
    users.find_one()
    return {"db": "connected"}

