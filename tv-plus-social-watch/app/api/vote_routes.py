from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.services.voting_service import list_candidates, record_vote, tally_votes, get_winner


router = APIRouter(prefix="/votes", tags=["votes"])


class VoteBody(BaseModel):
    room_id: str
    content_id: str
    user_id: str


class AddCandidatesBody(BaseModel):
    items: list[str]  # List of content_ids


@router.get("/{room_id}/candidates")
async def get_candidates(room_id: str):
    return {"candidates": await list_candidates(room_id)}


@router.post("/{room_id}/candidates")
async def add_candidates(room_id: str, body: AddCandidatesBody):
    """Add candidate contents to a room for voting"""
    from app.services.db import get_cursor
    
    async with get_cursor() as cur:
        for content_id in body.items:
            await cur.execute(
                "INSERT INTO candidates (room_id, content_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (room_id, content_id)
            )
        await cur.connection.commit()
    
    return {"status": "ok", "added": len(body.items)}


@router.get("/{room_id}/tally")
async def get_tally(room_id: str):
    return {"tally": await tally_votes(room_id)}


@router.get("/{room_id}/winner")
async def get_vote_winner(room_id: str, request: Request):
    # Get room user count from manager
    manager = request.app.state.manager
    room_users = manager.get_room_users(room_id)
    room_user_count = len(room_users)
    
    winner, total_voted = await get_winner(room_id, room_user_count)
    return {
        "winner": winner,
        "room_user_count": room_user_count,
        "total_voted": total_voted,
        "voting_status": "complete" if winner else "pending"
    }


@router.post("")
async def post_vote(body: VoteBody):
    return await record_vote(body.room_id, body.content_id, body.user_id)


