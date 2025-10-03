#!/usr/bin/env python3
"""
Verify that all code matches the database schema exactly
"""
import os
import asyncio
import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

async def verify_schema():
    """Verify database schema matches expectations"""
    
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
            async with conn.cursor(row_factory=dict_row) as cur:
                
                print("\n" + "="*70)
                print("🔍 VERIFYING DATABASE SCHEMA")
                print("="*70 + "\n")
                
                # Define expected schema
                expected_tables = {
                    "users": ["user_id", "name", "avatar"],
                    "rooms": ["room_id", "title", "start_at", "host_id"],
                    "catalog": ["content_id", "title", "type", "duration_min", "tags"],
                    "candidates": ["room_id", "content_id"],
                    "votes": ["room_id", "content_id", "user_id"],
                    "chat": ["room_id", "user_id", "message", "created_at"],
                    "emojis": ["room_id", "user_id", "emoji", "created_at"],
                    "expenses": ["expense_id", "room_id", "user_id", "amount", "note", "weight"],
                    "sync_events": ["room_id", "user_id", "action", "ts", "position_sec"]
                }
                
                all_match = True
                
                for table_name, expected_columns in expected_tables.items():
                    # Check if table exists
                    await cur.execute(
                        """
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s
                        ORDER BY ordinal_position
                        """,
                        (table_name,)
                    )
                    columns = await cur.fetchall()
                    
                    if not columns:
                        print(f"❌ Table '{table_name}' NOT FOUND!")
                        all_match = False
                        continue
                    
                    actual_columns = [col["column_name"] for col in columns]
                    
                    # Check if all expected columns exist
                    missing = set(expected_columns) - set(actual_columns)
                    extra = set(actual_columns) - set(expected_columns)
                    
                    if missing or extra:
                        print(f"\n⚠️  Table '{table_name}' column mismatch:")
                        if missing:
                            print(f"   Missing columns: {', '.join(missing)}")
                        if extra:
                            print(f"   Extra columns: {', '.join(extra)}")
                        all_match = False
                    else:
                        print(f"✅ Table '{table_name}' - All columns match")
                        for col in columns:
                            print(f"   - {col['column_name']}: {col['data_type']}")
                
                print("\n" + "="*70)
                if all_match:
                    print("✅ ALL TABLES MATCH SCHEMA PERFECTLY!")
                else:
                    print("⚠️  SCHEMA MISMATCHES FOUND - CHECK ABOVE")
                print("="*70 + "\n")
                
                # Test insert/select on each table
                print("\n" + "="*70)
                print("🧪 TESTING BASIC OPERATIONS")
                print("="*70 + "\n")
                
                # Test users table
                test_user_id = "test_user_verify"
                await cur.execute(
                    "INSERT INTO users (user_id, name, avatar) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                    (test_user_id, "Test User", "🧪")
                )
                await cur.execute("SELECT * FROM users WHERE user_id = %s", (test_user_id,))
                user = await cur.fetchone()
                if user and user["user_id"] == test_user_id:
                    print("✅ users table: INSERT & SELECT working")
                else:
                    print("❌ users table: Failed")
                
                # Test rooms table
                await cur.execute(
                    "INSERT INTO rooms (room_id, title, start_at, host_id) VALUES (%s, %s, %s, %s) ON CONFLICT (room_id) DO NOTHING",
                    ("test_room", "Test Room", "2025-10-15T20:00:00Z", test_user_id)
                )
                await cur.execute("SELECT * FROM rooms WHERE room_id = 'test_room'")
                room = await cur.fetchone()
                if room and room["room_id"] == "test_room":
                    print("✅ rooms table: INSERT & SELECT working")
                else:
                    print("❌ rooms table: Failed")
                
                # Test catalog table
                await cur.execute(
                    "INSERT INTO catalog (content_id, title, type, duration_min, tags) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (content_id) DO NOTHING",
                    ("test_content", "Test Movie", "movie", 120, "test,movie")
                )
                await cur.execute("SELECT * FROM catalog WHERE content_id = 'test_content'")
                content = await cur.fetchone()
                if content and content["content_id"] == "test_content":
                    print("✅ catalog table: INSERT & SELECT working")
                else:
                    print("❌ catalog table: Failed")
                
                # Test expenses table
                await cur.execute(
                    "INSERT INTO expenses (expense_id, room_id, user_id, amount, note, weight) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (expense_id) DO NOTHING",
                    ("test_exp", "test_room", test_user_id, 100.50, "Test Expense", 1.0)
                )
                await cur.execute("SELECT * FROM expenses WHERE expense_id = 'test_exp'")
                expense = await cur.fetchone()
                if expense and expense["expense_id"] == "test_exp":
                    print("✅ expenses table: INSERT & SELECT working")
                    print(f"   Amount: {expense['amount']}, Weight: {expense['weight']}")
                else:
                    print("❌ expenses table: Failed")
                
                await conn.commit()
                
                print("\n" + "="*70)
                print("✅ SCHEMA VERIFICATION COMPLETE!")
                print("="*70 + "\n")
                
                return 0
                
    except Exception as err:
        print(f"\n❌ ERROR: {err}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(verify_schema())
    exit(exit_code)
