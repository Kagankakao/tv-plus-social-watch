#!/usr/bin/env python3
"""
Add mock data for testing the TV+ Social Watch app
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

async def add_mock_data():
    """Add mock users, rooms, and catalog data"""
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
        async with await psycopg.AsyncConnection.connect(**conn_kwargs) as conn:
            async with conn.cursor() as cur:
                # Add mock users
                users = [
                    ("user_1", "Ali", "👨"),
                    ("user_2", "Ayşe", "👩"),
                    ("user_3", "Mehmet", "🧑"),
                    ("host_1", "Moderatör", "👑")
                ]
                
                for user_id, name, avatar in users:
                    await cur.execute(
                        "INSERT INTO users (user_id, name, avatar) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                        (user_id, name, avatar)
                    )
                
                # Add mock catalog
                catalog = [
                    ("interstellar", "Yıldızlararası", "movie", 169, "bilim-kurgu,dram,macera"),
                    ("fight_club", "Fight Club", "movie", 139, "dram,gerilim,aksiyon"),
                    ("star_wars", "Star Wars", "movie", 121, "bilim-kurgu,macera,fantazi"),
                    ("film_1", "Aksiyon Filmi", "film", 120, "aksiyon,gerilim"),
                    ("film_2", "Komedi Filmi", "film", 90, "komedi,aile"),
                    ("series_1", "Drama Dizisi", "series", 45, "drama,romantik"),
                    ("documentary_1", "Doğa Belgeseli", "documentary", 60, "doğa,belgesel")
                ]
                
                for content_id, title, content_type, duration, tags in catalog:
                    await cur.execute(
                        "INSERT INTO catalog (content_id, title, type, duration_min, tags) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (content_id) DO NOTHING",
                        (content_id, title, content_type, duration, tags)
                    )
                
                # Add mock room
                await cur.execute(
                    "INSERT INTO rooms (room_id, title, start_at, host_id) VALUES (%s, %s, %s, %s) ON CONFLICT (room_id) DO NOTHING",
                    ("room_1", "Akşam Film Gecesi", "2025-10-02 21:00:00", "host_1")
                )
                
                # Add candidates for voting (the 3 requested movies)
                candidates = [
                    ("room_1", "interstellar"),
                    ("room_1", "fight_club"),
                    ("room_1", "star_wars")
                ]
                
                for room_id, content_id in candidates:
                    await cur.execute(
                        "INSERT INTO candidates (room_id, content_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        (room_id, content_id)
                    )
                
                await conn.commit()
                print("✅ Mock data added successfully")
                
    except Exception as err:
        print(f"❌ Error adding mock data: {err}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(add_mock_data())
    if exit_code:
        exit(exit_code)
