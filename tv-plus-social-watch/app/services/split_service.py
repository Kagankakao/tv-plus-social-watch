from typing import List, Dict
from collections import defaultdict
from .db import get_cursor


async def list_expenses(room_id: str) -> List[Dict[str, str]]:
    async with get_cursor() as cur:
        await cur.execute(
            "SELECT expense_id, room_id, user_id, amount, note, weight FROM expenses WHERE room_id = %s ORDER BY expense_id",
            (room_id,)
        )
        rows = await cur.fetchall()
        return [
            {
                "expense_id": row["expense_id"],
                "room_id": row["room_id"],
                "user_id": row["user_id"],
                "amount": str(row["amount"]),
                "note": row["note"],
                "weight": str(row["weight"])
            }
            for row in rows
        ]


async def add_expense(expense_id: str, room_id: str, user_id: str, amount: float, description: str, weight: float) -> Dict[str, str]:
    async with get_cursor() as cur:
        await cur.execute(
            "INSERT INTO expenses (expense_id, room_id, user_id, amount, note, weight) VALUES (%s, %s, %s, %s, %s, %s)",
            (expense_id, room_id, user_id, amount, description, weight)
        )
        await cur.connection.commit()
    
    return {
        "expense_id": expense_id,
        "room_id": room_id,
        "user_id": user_id,
        "amount": str(amount),
        "note": description,
        "weight": str(weight)
    }


async def calc_balances(room_id: str) -> List[Dict[str, str]]:
    """
    Calculate balances using the formula:
    share_i = total * (weight_i / Σweight)
    net_i = paid_i - share_i
    
    Example from spec:
    U2 pays 120 (weight 1.0), U3 pays 60 (weight 0.5)
    Total = 180, Total weight = 1.5
    U2 owes: 180 * (1.0/1.5) = 120
    U3 owes: 180 * (0.5/1.5) = 60
    """
    async with get_cursor() as cur:
        await cur.execute(
            "SELECT user_id, amount, weight FROM expenses WHERE room_id = %s",
            (room_id,)
        )
        rows = await cur.fetchall()
    
    if not rows:
        return []
    
    # Calculate total amount and collect weights per user
    paid_by_user = defaultdict(float)
    weight_by_user = defaultdict(float)
    total_amount = 0.0
    
    for row in rows:
        user_id = row["user_id"]
        amount = float(row["amount"])
        weight = float(row["weight"])
        
        paid_by_user[user_id] += amount
        weight_by_user[user_id] += weight
        total_amount += amount
    
    # Calculate total weight (Σweight)
    total_weight = sum(weight_by_user.values())
    if total_weight == 0:
        total_weight = 1.0
    
    # Calculate each user's balance
    # Formula: share_i = total * (weight_i / Σweight)
    balances = []
    all_users = set(paid_by_user.keys()) | set(weight_by_user.keys())
    
    for user_id in all_users:
        paid = paid_by_user.get(user_id, 0.0)
        weight = weight_by_user.get(user_id, 0.0)
        
        # Calculate what this user owes based on their weight
        owed = total_amount * (weight / total_weight)
        
        # Net balance = what they paid - what they owe
        net = paid - owed
        
        balances.append({
            "user_id": user_id, 
            "paid": f"{paid:.2f}", 
            "owed": f"{owed:.2f}", 
            "net": f"{net:.2f}"
        })
    
    return balances



