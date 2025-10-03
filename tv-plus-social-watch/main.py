from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

from app.api.room_routes import router as room_router
from app.api.vote_routes import router as vote_router
from app.api.expense_routes import router as expense_router
from app.api.chat_routes import router as chat_router
from app.api.user_routes import router as user_router
from app.api import router as db_router
from app.core.config import settings
from app.websockets.room_manager import RoomManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all data on startup - database only"""
    from app.services.db import get_cursor
    from datetime import datetime, timedelta
    
    print("\n" + "="*60)
    print("🚀 INITIALIZING DATABASE...")
    print("="*60 + "\n")
    
    try:
        async with get_cursor() as cur:
            # 1. Create users
            print("👥 Creating users...")
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
            print(f"   ✅ {len(users)} users added")
            
            # 2. Create catalog
            print("\n🎬 Creating catalog...")
            catalog = [
                ("interstellar", "Yıldızlararası", "movie", 169, "bilim-kurgu,dram,macera"),
                ("fight_club", "Fight Club", "movie", 139, "dram,gerilim,aksiyon"),
                ("star_wars", "Star Wars", "movie", 121, "bilim-kurgu,macera,fantazi")
            ]
            for content_id, title, content_type, duration, tags in catalog:
                await cur.execute(
                    "INSERT INTO catalog (content_id, title, type, duration_min, tags) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (content_id) DO NOTHING",
                    (content_id, title, content_type, duration, tags)
                )
            print(f"   ✅ {len(catalog)} movies added to catalog")
            
            # 3. Create room
            print("\n🏠 Creating room...")
            start_time = datetime.now() + timedelta(hours=1)
            await cur.execute(
                "INSERT INTO rooms (room_id, title, start_at, host_id) VALUES (%s, %s, %s, %s) ON CONFLICT (room_id) DO UPDATE SET title = EXCLUDED.title, start_at = EXCLUDED.start_at",
                ("room_1", "Akşam Film Gecesi", start_time, "host_1")
            )
            print("   ✅ room_1 created")
            
            # 4. Create candidates (voting options)
            print("\n🗳️  Creating voting candidates...")
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
            print(f"   ✅ {len(candidates)} voting candidates added")
            
            await cur.connection.commit()
            
            print("\n" + "="*60)
            print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
            print("="*60)
            print("\n📊 Available data:")
            print(f"   - {len(users)} users")
            print(f"   - {len(catalog)} movies")
            print(f"   - 1 room (room_1)")
            print(f"   - {len(candidates)} voting candidates")
            print("\n🎉 Ready to use at: http://localhost:8000/app\n")
            
    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    # Cleanup (if needed)


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
manager = RoomManager()

# Store manager in app state so routes can access it
app.state.manager = manager

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(room_router)
app.include_router(vote_router)
app.include_router(expense_router)
app.include_router(chat_router)
app.include_router(db_router)


@app.get("/")
def root():
    return FileResponse('static/login.html')

@app.get("/app")
def app_page():
    return FileResponse('static/index.html')

@app.get("/login")
def login():
    return FileResponse('static/login.html')

@app.get("/register")
def register():
    return FileResponse('static/register.html')


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/rooms/{room_id}/status")
def get_room_status(room_id: str):
    users = manager.get_room_users(room_id)
    return {
        "room_id": room_id,
        "user_count": len(users),
        "users": list(users)
    }


@app.websocket("/ws/{room_id}/{user_id}")
async def ws_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await websocket.accept()
    await manager.join(room_id, user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                await manager.handle_message(room_id, user_id, message_data)
            except json.JSONDecodeError:
                # Invalid JSON, ignore
                pass
    except WebSocketDisconnect:
        await manager.leave(room_id, user_id)


