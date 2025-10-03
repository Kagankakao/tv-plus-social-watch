from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.db import get_cursor
import uuid

router = APIRouter(prefix="/api/users", tags=["users"])


class RegisterRequest(BaseModel):
    name: str
    avatar: str = "👤"


class LoginRequest(BaseModel):
    user_id: str


class UserResponse(BaseModel):
    user_id: str
    name: str
    avatar: str


@router.post("/register", response_model=UserResponse)
async def register_user(request: RegisterRequest):
    """Register a new user"""
    # Generate unique user ID
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    async with get_cursor() as cur:
        try:
            # Insert new user
            await cur.execute(
                "INSERT INTO users (user_id, name, avatar) VALUES (%s, %s, %s)",
                (user_id, request.name, request.avatar)
            )
            await cur.connection.commit()
            
            return UserResponse(
                user_id=user_id,
                name=request.name,
                avatar=request.avatar
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")


@router.post("/login", response_model=UserResponse)
async def login_user(request: LoginRequest):
    """Login existing user"""
    async with get_cursor() as cur:
        await cur.execute(
            "SELECT user_id, name, avatar FROM users WHERE user_id = %s",
            (request.user_id,)
        )
        user = await cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            user_id=user["user_id"],
            name=user["name"],
            avatar=user["avatar"]
        )


@router.get("/list")
async def list_users():
    """List all users"""
    async with get_cursor() as cur:
        await cur.execute("SELECT user_id, name, avatar FROM users ORDER BY name")
        users = await cur.fetchall()
        return {"users": [dict(u) for u in users]}
