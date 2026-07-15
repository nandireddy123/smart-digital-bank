"""
main.py
-------
FastAPI application entrypoint. Wires up routers, CORS, and a global
exception handler that converts our Custom Exceptions
(core/exceptions.py) into clean JSON error responses -- so every
router function can just `raise InsufficientFundsError(...)` and
trust that the client gets a proper 400 with a readable message,
instead of every route having its own try/except boilerplate.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.core.exceptions import BankingException

from app.routers import auth_router, profile_router, customer_router, employee_router, manager_router

# Import every ORM model module so Base.metadata knows about all tables
# before create_all() runs (only used for quick local bootstrapping --
# database/schema.sql is the source of truth for the real schema).
from app.models import user_orm, profile_orm, banking_orm  # noqa: F401

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BankingException)
async def banking_exception_handler(request: Request, exc: BankingException):
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.on_event("startup")
def on_startup():
    # Creates any tables that don't exist yet. Safe to run alongside
    # database/schema.sql, which you should run first in MySQL Workbench.
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(customer_router.router)
app.include_router(employee_router.router)
app.include_router(manager_router.router)


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} API is running", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
