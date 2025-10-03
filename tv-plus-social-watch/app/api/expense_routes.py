from fastapi import APIRouter
from pydantic import BaseModel
from app.services.split_service import list_expenses, add_expense, calc_balances


router = APIRouter(tags=["expenses"])


class ExpenseBody(BaseModel):
    user_id: str
    amount: float
    note: str
    weight: float = 1.0


@router.get("/rooms/{room_id}/expenses")
async def get_expenses(room_id: str):
    return {"expenses": await list_expenses(room_id)}


@router.get("/rooms/{room_id}/balances")
async def get_balances(room_id: str):
    totals = await calc_balances(room_id)
    return {
        "totals": sum(float(b["net"]) for b in totals),
        "per_user": totals
    }


@router.post("/rooms/{room_id}/expenses")
async def post_expense(room_id: str, body: ExpenseBody):
    import time
    expense_id = f"exp_{int(time.time() * 1000)}"
    return await add_expense(
        expense_id,
        room_id,
        body.user_id,
        body.amount,
        body.note,
        body.weight,
    )


