from typing import Dict, List, Tuple, Optional
from collections import Counter
from .db import get_cursor


async def list_candidates(room_id: str) -> List[Dict[str, str]]:
    """Get voting candidates from database only"""
    async with get_cursor() as cur:
        await cur.execute(
            """
            SELECT c.content_id, cat.title, cat.type, cat.duration_min, cat.tags 
            FROM candidates c 
            JOIN catalog cat ON c.content_id = cat.content_id 
            WHERE c.room_id = %s 
            ORDER BY cat.title
            """,
            (room_id,)
        )
        rows = await cur.fetchall()
        return [
            {
                "content_id": row["content_id"],
                "title": row["title"],
                "type": row["type"],
                "duration_min": str(row["duration_min"]),
                "tags": row["tags"]
            }
            for row in rows
        ]


async def record_vote(room_id: str, content_id: str, user_id: str) -> Dict[str, str]:
    async with get_cursor() as cur:
        # Delete existing vote for this user in this room
        await cur.execute(
            "DELETE FROM votes WHERE room_id = %s AND user_id = %s",
            (room_id, user_id)
        )
        # Insert new vote
        await cur.execute(
            "INSERT INTO votes (room_id, content_id, user_id) VALUES (%s, %s, %s)",
            (room_id, content_id, user_id)
        )
        await cur.connection.commit()
    
    return {"room_id": room_id, "content_id": content_id, "user_id": user_id}


async def tally_votes(room_id: str) -> List[Dict[str, str]]:
    async with get_cursor() as cur:
        await cur.execute(
            "SELECT content_id, COUNT(*) as vote_count "
            "FROM votes WHERE room_id = %s "
            "GROUP BY content_id "
            "ORDER BY vote_count DESC",
            (room_id,)
        )
        rows = await cur.fetchall()
        return [
            {"content_id": row["content_id"], "votes": str(row["vote_count"])}
            for row in rows
        ]


async def get_winner(room_id: str, room_user_count: int = 0) -> Tuple[Optional[Dict[str, str]], int]:
    """Get the winning content (highest votes) with full details
    Returns: (winner_dict or None, total_voted_count)
    Only returns winner if ALL users in room have voted (when room_user_count >= 2)
    """
    async with get_cursor() as cur:
        # Count total votes in this room
        await cur.execute(
            "SELECT COUNT(DISTINCT user_id) as total_voted FROM votes WHERE room_id = %s",
            (room_id,)
        )
        vote_row = await cur.fetchone()
        total_voted = vote_row["total_voted"] if vote_row else 0
        
        # Only return winner if:
        # 1. Room has at least 2 users
        # 2. All users have voted
        if room_user_count < 2 or total_voted < room_user_count:
            return (None, total_voted)
        
        # Get the winning content
        await cur.execute(
            "SELECT v.content_id, cat.title, cat.type, cat.duration_min, COUNT(*) as vote_count "
            "FROM votes v "
            "JOIN catalog cat ON v.content_id = cat.content_id "
            "WHERE v.room_id = %s "
            "GROUP BY v.content_id, cat.title, cat.type, cat.duration_min "
            "ORDER BY vote_count DESC "
            "LIMIT 1",
            (room_id,)
        )
        row = await cur.fetchone()
        if row:
            winner = {
                "content_id": row["content_id"],
                "title": row["title"],
                "type": row["type"],
                "duration_min": str(row["duration_min"]),
                "votes": str(row["vote_count"])
            }
            return (winner, total_voted)
        return (None, total_voted)



