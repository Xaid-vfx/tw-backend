from tortoise import Tortoise
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

# Tortoise ORM expects the PostgreSQL scheme to be "postgres://".
# Supabase and some other providers, however, expose the connection string using
# the "postgresql://" scheme. If we detect the unsupported scheme we rewrite it
# on the fly so that the application can start without requiring the developer
# to manually edit their environment variables.

if SUPABASE_DB_URL and SUPABASE_DB_URL.startswith("postgresql://"):
    SUPABASE_DB_URL = SUPABASE_DB_URL.replace("postgresql://", "postgres://", 1)

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
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        # await Tortoise.generate_schemas() // we will only rely on migrations for now
        print("Database initialized")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise e

async def close_db():
    await Tortoise.close_connections()
