from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from app.services.db import get_cursor
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    room_id: str
    user_id: str
    message: str


class EmojiMessage(BaseModel):
    room_id: str
    user_id: str
    emoji: str


@router.get("/{room_id}/messages")
async def get_chat_messages(room_id: str, limit: int = 50) -> Dict[str, List[Dict]]:
    """Get recent chat messages for a room"""
    async with get_cursor() as cur:
        await cur.execute(
            "SELECT user_id, message, created_at FROM chat "
            "WHERE room_id = %s ORDER BY created_at DESC LIMIT %s",
            (room_id, limit)
        )
        messages = await cur.fetchall()
        
        await cur.execute(
            "SELECT user_id, emoji, created_at FROM emojis "
            "WHERE room_id = %s ORDER BY created_at DESC LIMIT %s",
            (room_id, limit)
        )
        emojis = await cur.fetchall()
    
    # Combine and sort by timestamp
    all_messages = []
    
    for msg in messages:
        all_messages.append({
            "type": "chat",
            "user_id": msg["user_id"],
            "content": msg["message"],
            "timestamp": msg["created_at"].isoformat()
        })
    
    for emoji in emojis:
        all_messages.append({
            "type": "emoji", 
            "user_id": emoji["user_id"],
            "content": emoji["emoji"],
            "timestamp": emoji["created_at"].isoformat()
        })
    
    # Sort by timestamp (newest first)
    all_messages.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"messages": all_messages[:limit]}


@router.post("/message")
async def send_chat_message(message: ChatMessage):
    """Send a chat message (usually called via WebSocket, but available as REST too)"""
    async with get_cursor() as cur:
        await cur.execute(
            "INSERT INTO chat (room_id, user_id, message, created_at) VALUES (%s, %s, %s, %s)",
            (message.room_id, message.user_id, message.message, datetime.now())
        )
        await cur.connection.commit()
    
    return {"status": "sent", "timestamp": datetime.now().isoformat()}


@router.post("/emoji")
async def send_emoji(emoji: EmojiMessage):
    """Send an emoji (usually called via WebSocket, but available as REST too)"""
    async with get_cursor() as cur:
        await cur.execute(
            "INSERT INTO emojis (room_id, user_id, emoji, created_at) VALUES (%s, %s, %s, %s)",
            (emoji.room_id, emoji.user_id, emoji.emoji, datetime.now())
        )
        await cur.connection.commit()
    
    return {"status": "sent", "timestamp": datetime.now().isoformat()}
