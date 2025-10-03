import os
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import psycopg
from psycopg.rows import dict_row

from app.core.config import settings

# Fix Windows event loop issue
if os.name == 'nt':  # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def _build_conn_kwargs() -> dict:
    # Prefer discrete env if provided
    if settings.db_host and settings.db_user and settings.db_password:
        return {
            "host": settings.db_host,
            "user": settings.db_user,
            "password": settings.db_password,
            "port": settings.db_port,
            "dbname": settings.db_database,
            "sslmode": "require",
        }
    if settings.database_url:
        return {"conninfo": settings.database_url, "sslmode": "require"}
    # Fallback to env DATABASE_URL if not captured
    url = os.getenv("DATABASE_URL")
    if url:
        return {"conninfo": url, "sslmode": "require"}
    raise RuntimeError("Database configuration missing: set DB_* or DATABASE_URL")


def _get_conn_kwargs() -> dict:
    """Lazy load connection kwargs to avoid import-time errors"""
    return _build_conn_kwargs()


@asynccontextmanager
async def get_connection() -> AsyncIterator[psycopg.AsyncConnection]:
    conn_kw = _get_conn_kwargs()
    async with await psycopg.AsyncConnection.connect(**conn_kw) as conn:
        yield conn


@asynccontextmanager
async def get_cursor() -> AsyncIterator[psycopg.AsyncCursor]:
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            yield cur


async def ping() -> str:
    async with get_cursor() as cur:
        await cur.execute("select now() as now")
        row = await cur.fetchone()
        return str(row["now"]) if row else "unknown"


