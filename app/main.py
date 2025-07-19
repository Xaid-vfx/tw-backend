from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, couples, messages, users, sessions
from app.database import init_db, close_db
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Third Wheel - Couples Therapy MVP",
    description="A couples therapy platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(couples.router)
app.include_router(messages.router)
app.include_router(sessions.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Third Wheel - Couples Therapy Platform"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}