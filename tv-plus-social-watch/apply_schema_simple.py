#!/usr/bin/env python3
"""
Apply database schema to Supabase - Simple version
"""
import os
import asyncio
import psycopg
from dotenv import load_dotenv

# Fix Windows event loop issue
if os.name == 'nt':  # Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

async def apply_schema():
    """Apply the database schema"""
    # Build connection
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DATABASE", "postgres")
    port = int(os.getenv("DB_PORT", "5432"))

    if host and user and password:
        conn_kwargs = {
            "host": host,
            "user": user,
            "password": password,
            "dbname": database,
            "port": port,
            "sslmode": "require",
        }
    else:
        connection_string = os.getenv("DATABASE_URL")
        if not connection_string:
            print("❌ Database configuration missing")
            return 1
        conn_kwargs = {"conninfo": connection_string, "sslmode": "require"}

    try:
        # Read schema file
        with open("schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()

        async with await psycopg.AsyncConnection.connect(**conn_kwargs) as conn:
            async with conn.cursor() as cur:
                await cur.execute(schema_sql)
                await conn.commit()
                print("✅ Schema applied successfully")
    except Exception as err:
        print(f"❌ Schema application error: {err}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(apply_schema())
    if exit_code:
        exit(exit_code)
