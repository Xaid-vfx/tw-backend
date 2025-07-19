from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "sessions" ADD "status" VARCHAR(20) NOT NULL DEFAULT 'active';
        ALTER TABLE "sessions" ADD "max_participants" INT NOT NULL DEFAULT 2;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "sessions" DROP COLUMN "status";
        ALTER TABLE "sessions" DROP COLUMN "max_participants";"""
