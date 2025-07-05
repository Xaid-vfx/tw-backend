from tortoise import Tortoise
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

TORTOISE_ORM = {
    "connections": {
        "default": SUPABASE_DB_URL
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.couple",
                "app.models.session",
                "app.models.session_participant",
                "app.models.message",
                "aerich.models"
            ],
            "default_connection": "default",
        }
    }
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
