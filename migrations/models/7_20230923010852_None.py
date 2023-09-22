from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "chats" (
    "tg_id" BIGSERIAL NOT NULL PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS "records" (
    "uuid" UUID NOT NULL  PRIMARY KEY,
    "student_name" VARCHAR(255) NOT NULL,
    "student_group" VARCHAR(255) NOT NULL,
    "lab_name" VARCHAR(255) NOT NULL,
    "lab_date" DATE NOT NULL,
    "stream" VARCHAR(20) NOT NULL  DEFAULT 'Change',
    "datetime" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
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
