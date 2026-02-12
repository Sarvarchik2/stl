"""Main FastAPI Application."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from .config import settings
from .database import init_db
from .api import auth, users, cars, applications, payments, documents, blacklist, admin, stories, admin_stories

# Create App
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Car Dealership Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3003",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3003",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (uploads)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(cars.router, prefix=settings.API_V1_PREFIX)
app.include_router(applications.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.router, prefix=settings.API_V1_PREFIX)
app.include_router(payments.global_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(blacklist.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(stories.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_stories.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def on_startup():
    """Initialize database on startup."""
    await init_db()
    
    
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}
