from typing import List, Dict
from .db import get_cursor


async def list_rooms() -> List[Dict[str, str]]:
    async with get_cursor() as cur:
        await cur.execute("SELECT room_id, title, start_at, host_id FROM rooms ORDER BY start_at DESC")
        rows = await cur.fetchall()
        return [
            {
                "id": row["room_id"],
                "title": row["title"], 
                "start_time_utc": str(row["start_at"]),
                "host_user_id": row["host_id"]
            }
            for row in rows
        ]


async def create_room(room_id: str, title: str, start_time_utc: str, host_user_id: str) -> Dict[str, str]:
    """Create room in database only"""
    async with get_cursor() as cur:
        await cur.execute(
            "INSERT INTO rooms (room_id, title, start_at, host_id) VALUES (%s, %s, %s, %s) ON CONFLICT (room_id) DO UPDATE SET title = EXCLUDED.title, start_at = EXCLUDED.start_at",
            (room_id, title, start_time_utc, host_user_id)
        )
        await cur.connection.commit()
    
    return {
        "id": room_id,
        "title": title,
        "start_time_utc": start_time_utc,
        "host_user_id": host_user_id,
    }


async def get_room_summary(room_id: str) -> Dict:
    """Get room summary with selected content and vote tallies"""
    async with get_cursor() as cur:
        # Get room info
        await cur.execute(
            "SELECT room_id, title, start_at, host_id FROM rooms WHERE room_id = %s",
            (room_id,)
        )
        room_row = await cur.fetchone()
        
        if not room_row:
            return {"error": "Room not found"}
        
        # Get winning content
        await cur.execute(
            """
            SELECT v.content_id, cat.title, cat.type, cat.duration_min, COUNT(*) as vote_count
            FROM votes v
            JOIN catalog cat ON v.content_id = cat.content_id
            WHERE v.room_id = %s
            GROUP BY v.content_id, cat.title, cat.type, cat.duration_min
            ORDER BY vote_count DESC
            LIMIT 1
            """,
            (room_id,)
        )
        winner_row = await cur.fetchone()
        
        # Get all vote tallies
        await cur.execute(
            """
            SELECT content_id, COUNT(*) as vote_count
            FROM votes
            WHERE room_id = %s
            GROUP BY content_id
            """,
            (room_id,)
        )
        vote_rows = await cur.fetchall()
        
        votes_dict = {row["content_id"]: int(row["vote_count"]) for row in vote_rows}
        
        selected_content = None
        if winner_row:
            selected_content = {
                "content_id": winner_row["content_id"],
                "title": winner_row["title"],
                "type": winner_row["type"],
                "duration_min": int(winner_row["duration_min"])
            }
        
        return {
            "room_id": room_row["room_id"],
            "title": room_row["title"],
            "start_at": str(room_row["start_at"]),
            "host_id": room_row["host_id"],
            "selected_content": selected_content,
            "votes": votes_dict
        }



