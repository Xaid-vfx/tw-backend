from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "first_name" VARCHAR(100) NOT NULL,
    "last_name" VARCHAR(100) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_verified" BOOL NOT NULL DEFAULT False,
    "phone_number" VARCHAR(20),
    "date_of_birth" DATE,
    "gender" VARCHAR(20),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMPTZ,
    "partner_id" INT
);
CREATE TABLE IF NOT EXISTS "couples" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user1_id" INT NOT NULL,
    "user2_id" INT NOT NULL,
    "session_id" INT NOT NULL,
    "relationship_start_date" DATE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL DEFAULT True,
    CONSTRAINT "uid_couples_user1_i_357496" UNIQUE ("user1_id", "user2_id", "session_id")
);
CREATE TABLE IF NOT EXISTS "sessions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "session_code" VARCHAR(8) NOT NULL UNIQUE,
    "creator_user_id" INT NOT NULL,
    "session_mode" VARCHAR(10) NOT NULL DEFAULT 'couple',
    "couple_id" INT,
    "current_participants" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "session_participants" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "session_id" INT NOT NULL,
    "user_id" INT NOT NULL,
    "role" VARCHAR(20) NOT NULL DEFAULT 'participant',
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL DEFAULT True,
    CONSTRAINT "uid_session_par_session_4bbf7e" UNIQUE ("session_id", "user_id")
);
CREATE TABLE IF NOT EXISTS "messages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "session_id" INT NOT NULL,
    "user_id" INT NOT NULL,
    "content" TEXT NOT NULL,
    "sender_type" VARCHAR(10) NOT NULL,
    "message_status" VARCHAR(20) NOT NULL DEFAULT 'sent',
    "reply_to_message_id" INT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
