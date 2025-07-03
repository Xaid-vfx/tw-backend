from fastapi import FastAPI
from app.routers import auth, couples, messages

app = FastAPI(title="Couples Therapy MVP")

app.include_router(auth.router)
app.include_router(couples.router)
app.include_router(messages.router)