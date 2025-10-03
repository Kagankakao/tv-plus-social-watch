#!/usr/bin/env python3
"""
Verify all database connections and data integrity
"""
import os
import asyncio
import psycopg
from dotenv import load_dotenv
from datetime import datetime

# Fix Windows event loop issue
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

async def verify_database():
    """Verify database connection and data"""
    print("\n" + "="*60)
    print("🔍 DATABASE VERIFICATION STARTED")
    print("="*60 + "\n")
    
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
                
                # 1. Check connection
                print("1️⃣  Testing database connection...")
                await cur.execute("SELECT version()")
                version = await cur.fetchone()
                print(f"   ✅ Connected to: {version[0][:50]}...")
                
                # 2. Check all required tables
                print("\n2️⃣  Verifying table structure...")
                required_tables = [
                    'users', 'rooms', 'catalog', 'candidates', 
                    'votes', 'expenses', 'chat', 'emojis', 'sync_events'
                ]
                
                for table in required_tables:
                    await cur.execute(
                        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = %s",
                        (table,)
                    )
                    exists = (await cur.fetchone())[0]
                    if exists:
                        await cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = (await cur.fetchone())[0]
                        print(f"   ✅ Table '{table}' exists with {count} rows")
                    else:
                        print(f"   ❌ Table '{table}' NOT FOUND!")
                
                # 3. Verify users
                print("\n3️⃣  Checking users...")
                await cur.execute("SELECT user_id, name, avatar FROM users")
                users = await cur.fetchall()
                print(f"   Total users: {len(users)}")
                for user_id, name, avatar in users[:5]:  # Show first 5
                    print(f"   - {user_id}: {name} {avatar}")
                
                # 4. Verify rooms
                print("\n4️⃣  Checking rooms...")
                await cur.execute("SELECT room_id, title, host_id, start_at FROM rooms")
                rooms = await cur.fetchall()
                print(f"   Total rooms: {len(rooms)}")
                for room_id, title, host_id, start_at in rooms:
                    print(f"   - {room_id}: '{title}' hosted by {host_id}")
                    print(f"     Start time: {start_at}")
                
                # 5. Verify catalog
                print("\n5️⃣  Checking content catalog...")
                await cur.execute("SELECT content_id, title, type, duration_min FROM catalog")
                catalog = await cur.fetchall()
                print(f"   Total content items: {len(catalog)}")
                for content_id, title, content_type, duration in catalog:
                    print(f"   - {content_id}: '{title}' ({content_type}, {duration} min)")
                
                # 6. Verify candidates (for voting)
                print("\n6️⃣  Checking voting candidates...")
                await cur.execute(
                    """
                    SELECT c.room_id, c.content_id, cat.title 
                    FROM candidates c 
                    JOIN catalog cat ON c.content_id = cat.content_id
                    """
                )
                candidates = await cur.fetchall()
                print(f"   Total candidates: {len(candidates)}")
                for room_id, content_id, title in candidates:
                    print(f"   - Room '{room_id}': '{title}' ({content_id})")
                
                # 7. Verify votes
                print("\n7️⃣  Checking votes...")
                await cur.execute("SELECT room_id, COUNT(*) FROM votes GROUP BY room_id")
                votes = await cur.fetchall()
                if votes:
                    print(f"   Votes by room:")
                    for room_id, count in votes:
                        print(f"   - Room '{room_id}': {count} votes")
                else:
                    print("   ℹ️  No votes cast yet")
                
                # 8. Verify expenses
                print("\n8️⃣  Checking expenses...")
                await cur.execute("SELECT COUNT(*) FROM expenses")
                expense_count = (await cur.fetchone())[0]
                print(f"   Total expenses: {expense_count}")
                
                # 9. Check foreign key relationships
                print("\n9️⃣  Verifying data integrity...")
                
                # Check if all candidates reference valid content
                await cur.execute(
                    """
                    SELECT COUNT(*) FROM candidates c
                    LEFT JOIN catalog cat ON c.content_id = cat.content_id
                    WHERE cat.content_id IS NULL
                    """
                )
                orphaned_candidates = (await cur.fetchone())[0]
                if orphaned_candidates == 0:
                    print("   ✅ All candidates reference valid content")
                else:
                    print(f"   ⚠️  {orphaned_candidates} orphaned candidates found!")
                
                # Check if all votes reference valid rooms
                await cur.execute(
                    """
                    SELECT COUNT(*) FROM votes v
                    LEFT JOIN rooms r ON v.room_id = r.room_id
                    WHERE r.room_id IS NULL
                    """
                )
                orphaned_votes = (await cur.fetchone())[0]
                if orphaned_votes == 0:
                    print("   ✅ All votes reference valid rooms")
                else:
                    print(f"   ⚠️  {orphaned_votes} orphaned votes found!")
                
                # 10. API Endpoint Simulation
                print("\n🔟  Simulating API queries...")
                
                # Simulate GET /votes/{room_id}/candidates
                test_room = 'room_1'
                await cur.execute(
                    """
                    SELECT c.content_id, cat.title, cat.type, cat.duration_min, cat.tags 
                    FROM candidates c 
                    JOIN catalog cat ON c.content_id = cat.content_id 
                    WHERE c.room_id = %s
                    """,
                    (test_room,)
                )
                api_candidates = await cur.fetchall()
                print(f"   GET /votes/{test_room}/candidates")
                print(f"   Result: {len(api_candidates)} candidates")
                
                # Simulate GET /votes/{room_id}/tally
                await cur.execute(
                    """
                    SELECT content_id, COUNT(*) as vote_count 
                    FROM votes WHERE room_id = %s 
                    GROUP BY content_id 
                    ORDER BY vote_count DESC
                    """,
                    (test_room,)
                )
                tally = await cur.fetchall()
                print(f"   GET /votes/{test_room}/tally")
                print(f"   Result: {len(tally)} items with votes")
                
                print("\n" + "="*60)
                print("✅ DATABASE VERIFICATION COMPLETED SUCCESSFULLY!")
                print("="*60 + "\n")
                
                return 0
                
    except Exception as err:
        print(f"\n❌ ERROR: {err}")
        print("\n" + "="*60)
        print("❌ DATABASE VERIFICATION FAILED!")
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(verify_database())
    exit(exit_code)
