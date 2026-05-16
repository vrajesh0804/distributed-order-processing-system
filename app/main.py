"""
FastAPI application entry point.

main.py should stay small. It creates the FastAPI app, configures middleware,
creates database tables, and includes route modules.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import event, order, product, user
from app.core.config import settings
from app.db.database import Base, engine
from app.services.cache_service import check_rate_limit

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A production-style FastAPI backend showing PostgreSQL, Redis, Kafka, and event-driven order processing.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Basic Redis-backed rate limiting middleware.

    It limits each client IP to 30 requests per 60 seconds.
    """
    client_ip = request.client.host if request.client else "unknown"
    try:
        allowed = check_rate_limit(client_ip)
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
    except Exception:
        # If Redis is down, do not block normal learning/demo flow.
        pass

    return await call_next(request)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"message": "Distributed Order Backend is running"}


app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(event.router)
