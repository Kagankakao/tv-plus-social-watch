from fastapi import APIRouter
from app.services.db import ping as db_ping

router = APIRouter(prefix="/db", tags=["db"])


@router.get("/ping")
async def ping():
    now = await db_ping()
    return {"status": "ok", "now": now}


