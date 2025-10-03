from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.services.room_service import list_rooms as svc_list_rooms, create_room as svc_create_room, get_room_summary as svc_get_summary
from datetime import datetime


router = APIRouter(prefix="/rooms", tags=["rooms"])


class CreateRoomBody(BaseModel):
    id: str
    title: str
    start_time_utc: str
    host_user_id: str


@router.get("")
async def get_rooms():
    return {"rooms": await svc_list_rooms()}


@router.post("")
async def post_room(body: CreateRoomBody):
    room = await svc_create_room(body.id, body.title, body.start_time_utc, body.host_user_id)
    return room


@router.get("/{room_id}/summary")
async def get_summary(room_id: str, request: Request):
    """Get room summary including selected content, votes, members, start time"""
    manager = request.app.state.manager
    room_users = list(manager.get_room_users(room_id))
    summary = await svc_get_summary(room_id)
    summary["members"] = room_users
    summary["member_count"] = len(room_users)
    return summary


@router.post("/{room_id}/remind")
async def send_reminder(room_id: str, request: Request):
    """Mock reminder - simulate push notification 1 hour before event"""
    manager = request.app.state.manager
    room_users = list(manager.get_room_users(room_id))
    summary = await svc_get_summary(room_id)
    
    # Mock notification
    notification = {
        "status": "ok",
        "type": "reminder",
        "message": f"🔔 {summary.get('title', 'İzleme etkinliği')} 1 saat içinde başlıyor!",
        "room_id": room_id,
        "selected_content": summary.get("selected_content"),
        "start_at": summary.get("start_at"),
        "member_count": len(room_users),
        "timestamp": datetime.now().isoformat()
    }
    
    # In production, this would send actual push notifications
    return notification


