#!/usr/bin/env python3
"""
Test database connection to Supabase
Based on the Node.js example provided
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

def build_client():
    """Build database client based on environment variables"""
    # Prefer discrete env if provided
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DATABASE", "postgres")
    port = int(os.getenv("DB_PORT", "5432"))

    if host and user and password:
        print(f"Using discrete env → host: {host}, user: {user}, db: {database}, port: {port}")
        return {
            "host": host,
            "user": user,
            "password": password,
            "dbname": database,
            "port": port,
            "sslmode": "require",
        }

    connection_string = os.getenv("DATABASE_URL")
    if connection_string:
        # Debug: show parsed host/user (no password)
        try:
            from urllib.parse import urlparse
            url = urlparse(connection_string)
            print(f"Using DATABASE_URL → host: {url.hostname}, user: {url.username}")
        except Exception as e:
            print(f"DATABASE_URL present but could not be parsed: {e}")
        return {"conninfo": connection_string, "sslmode": "require"}

    print("Missing DB_HOST/DB_USER/DB_PASSWORD or DATABASE_URL in .env")
    return None

async def main():
    """Test database connection"""
    conn_kwargs = build_client()
    if not conn_kwargs:
        print("❌ Database configuration missing")
        return

    try:
        async with await psycopg.AsyncConnection.connect(**conn_kwargs) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT now() as now")
                row = await cur.fetchone()
                print(f"✅ Connected. Server time: {row[0]}")
    except Exception as err:
        print(f"❌ Connection/query error: {err}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    if exit_code:
        exit(exit_code)
