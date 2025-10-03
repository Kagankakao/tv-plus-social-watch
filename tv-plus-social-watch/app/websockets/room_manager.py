from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class RoomManager:
    def __init__(self) -> None:
        self._rooms: Dict[str, Dict[str, WebSocket]] = {}
        self._user_last_message: Dict[str, float] = {}

    async def join(self, room_id: str, user_id: str, websocket: WebSocket) -> None:
        if room_id not in self._rooms:
            self._rooms[room_id] = {}
        self._rooms[room_id][user_id] = websocket
        
        # Notify others about new user
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }, exclude_user=user_id)

    async def leave(self, room_id: str, user_id: str) -> None:
        if room_id in self._rooms and user_id in self._rooms[room_id]:
            del self._rooms[room_id][user_id]
            if not self._rooms[room_id]:
                del self._rooms[room_id]
            
            # Notify others about user leaving
            await self.broadcast_to_room(room_id, {
                "type": "user_left", 
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })

    def get_room_users(self, room_id: str) -> Set[str]:
        return set(self._rooms.get(room_id, {}).keys())

    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None) -> None:
        if room_id not in self._rooms:
            return
            
        message_str = json.dumps(message)
        disconnected_users = []
        
        for user_id, websocket in self._rooms[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue
                
            try:
                await websocket.send_text(message_str)
            except Exception:
                # Connection is broken, mark for removal
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.leave(room_id, user_id)

    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user can send message (2 second rate limit)"""
        now = asyncio.get_event_loop().time()
        last_time = self._user_last_message.get(user_id, 0)
        
        if now - last_time < 2.0:
            return False
            
        self._user_last_message[user_id] = now
        return True

    async def handle_message(self, room_id: str, user_id: str, message_data: dict) -> None:
        """Handle incoming WebSocket message"""
        message_type = message_data.get("type")
        
        if message_type in ["chat", "emoji"]:
            # Apply rate limiting
            if not self.check_rate_limit(user_id):
                # Send rate limit warning to user
                websocket = self._rooms.get(room_id, {}).get(user_id)
                if websocket:
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "rate_limit",
                            "message": "Çok hızlı mesaj gönderiyorsunuz. 2 saniye bekleyin."
                        }))
                    except Exception:
                        pass
                return
        
        # Add timestamp and user info
        message_data["user_id"] = user_id
        message_data["timestamp"] = datetime.now().isoformat()
        
        # Broadcast to all users in room
        await self.broadcast_to_room(room_id, message_data)

    async def sync_video_state(self, room_id: str, user_id: str, action: str, position: int) -> None:
        """Sync video playback state across room"""
        await self.broadcast_to_room(room_id, {
            "type": "video_sync",
            "action": action,
            "position": position,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })


