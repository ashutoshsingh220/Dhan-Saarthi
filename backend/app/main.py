from contextlib import asynccontextmanager

import time
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Dhan Saarthi API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic IP-based Rate Limiter (60 requests per minute)
rate_limit_store = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if client_ip == "testclient":
        return await call_next(request)
        
    now = time.time()
    
    # Clean up old requests for this IP
    rate_limit_store[client_ip] = [req_time for req_time in rate_limit_store[client_ip] if now - req_time < 60]
    
    if len(rate_limit_store[client_ip]) >= 60:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests. Please try again later."}
        )
        
    rate_limit_store[client_ip].append(now)
    return await call_next(request)
app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
