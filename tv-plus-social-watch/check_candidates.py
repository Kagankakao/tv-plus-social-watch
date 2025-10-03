#!/usr/bin/env python3
"""
Quick check for voting candidates in database
"""
import os
import asyncio
import psycopg
from dotenv import load_dotenv

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

async def check_and_fix_candidates():
    """Check if candidates exist and add if missing"""
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
                
                print("\n🔍 Checking candidates in database...\n")
                
                # Check current candidates
                await cur.execute(
                    """
                    SELECT c.room_id, c.content_id, cat.title, cat.type, cat.duration_min
                    FROM candidates c
                    JOIN catalog cat ON c.content_id = cat.content_id
                    WHERE c.room_id = 'room_1'
                    """
                )
                existing = await cur.fetchall()
                
                if existing:
                    print(f"✅ Found {len(existing)} candidates for room_1:")
                    for room_id, content_id, title, content_type, duration in existing:
                        print(f"   - {title} ({content_type}, {duration} min) [{content_id}]")
                else:
                    print("⚠️  No candidates found for room_1. Adding them now...")
                    
                    # First, ensure the 3 movies exist in catalog
                    movies = [
                        ("interstellar", "Yıldızlararası", "movie", 169, "bilim-kurgu,dram,macera"),
                        ("fight_club", "Fight Club", "movie", 139, "dram,gerilim,aksiyon"),
                        ("star_wars", "Star Wars", "movie", 121, "bilim-kurgu,macera,fantazi")
                    ]
                    
                    for content_id, title, content_type, duration, tags in movies:
                        await cur.execute(
                            "INSERT INTO catalog (content_id, title, type, duration_min, tags) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (content_id) DO NOTHING",
                            (content_id, title, content_type, duration, tags)
                        )
                    
                    # Add candidates
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
                    print("✅ Added 3 candidates to room_1")
                
                # Verify candidates are now there
                print("\n📊 Current candidates for room_1:")
                await cur.execute(
                    """
                    SELECT c.room_id, c.content_id, cat.title, cat.type, cat.duration_min
                    FROM candidates c
                    JOIN catalog cat ON c.content_id = cat.content_id
                    WHERE c.room_id = 'room_1'
                    ORDER BY cat.title
                    """
                )
                final = await cur.fetchall()
                
                for room_id, content_id, title, content_type, duration in final:
                    print(f"   ✅ {title} ({content_type}, {duration} min)")
                
                print(f"\n🎬 Total candidates: {len(final)}")
                print("\n✅ Database check complete!\n")
                
                return 0
                
    except Exception as err:
        print(f"\n❌ Error: {err}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(check_and_fix_candidates())
    exit(exit_code)
