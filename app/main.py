from fastapi import FastAPI
from app.routers import auth, couples, messages, users
from app.database import init_db, close_db
from contextlib import asynccontextmanager

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

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(couples.router)
app.include_router(messages.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Third Wheel - Couples Therapy Platform"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}