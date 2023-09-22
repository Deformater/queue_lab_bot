from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chats" ADD "datetime" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "chats" DROP COLUMN "datetime";"""
