# ✅ Database Schema Verification

## Your Schema - All Code Matches!

All services use the exact column names from your schema.

---

## 📊 Schema Mapping

### 1. users Table
```sql
user_id VARCHAR(255) PRIMARY KEY
name VARCHAR(255)
avatar VARCHAR(255)
```

**Code Usage:**
- ✅ `room_service.py`: `INSERT INTO users (user_id, name, avatar)`
- ✅ All queries use: `user_id`, `name`, `avatar`

---

### 2. rooms Table
```sql
room_id VARCHAR(255) PRIMARY KEY
title VARCHAR(255)
start_at TIMESTAMP
host_id VARCHAR(255)
```

**Code Usage:**
- ✅ `room_service.py`: `INSERT INTO rooms (room_id, title, start_at, host_id)`
- ✅ Query: `SELECT room_id, title, start_at, host_id FROM rooms`
- ✅ API returns: `host_user_id` (mapped from `host_id`)

---

### 3. catalog Table
```sql
content_id VARCHAR(255) PRIMARY KEY
title VARCHAR(255)
type VARCHAR(255)
duration_min INT
tags TEXT
```

**Code Usage:**
- ✅ `voting_service.py`: `INSERT INTO catalog (content_id, title, type, duration_min, tags)`
- ✅ All queries use exact column names

---

### 4. candidates Table
```sql
room_id VARCHAR(255)
content_id VARCHAR(255)
```

**Code Usage:**
- ✅ `voting_service.py`: `INSERT INTO candidates (room_id, content_id)`
- ✅ Query: `SELECT room_id, content_id FROM candidates`

---

### 5. votes Table
```sql
room_id VARCHAR(255)
content_id VARCHAR(255)
user_id VARCHAR(255)
```

**Code Usage:**
- ✅ `voting_service.py`: 
  - `INSERT INTO votes (room_id, content_id, user_id)`
  - `SELECT content_id, user_id FROM votes WHERE room_id = %s`

---

### 6. expenses Table  
```sql
expense_id VARCHAR(255) PRIMARY KEY
room_id VARCHAR(255)
user_id VARCHAR(255)
amount DECIMAL(10, 2)
note VARCHAR(255)
weight DECIMAL(3, 2)
```

**Code Usage:**
- ✅ `split_service.py`:
  - `INSERT INTO expenses (expense_id, room_id, user_id, amount, note, weight)`
  - `SELECT user_id, amount, weight FROM expenses WHERE room_id = %s`

---

### 7. chat Table
```sql
room_id VARCHAR(255)
user_id VARCHAR(255)
message TEXT
created_at TIMESTAMP
```

**Code Usage:**
- ✅ `chat_routes.py`: Uses all columns correctly

---

### 8. emojis Table
```sql
room_id VARCHAR(255)
user_id VARCHAR(255)
emoji VARCHAR(255)
created_at TIMESTAMP
```

**Code Usage:**
- ✅ `chat_routes.py`: Uses all columns correctly

---

### 9. sync_events Table
```sql
room_id VARCHAR(255)
user_id VARCHAR(255)
action VARCHAR(255)
ts TIMESTAMP
position_sec INT
```

**Code Usage:**
- ✅ WebSocket events log to this table

---

## ✅ Verification Script

Run this to verify everything matches:

```bash
python verify_schema_match.py
```

**Expected Output:**
```
✅ Table 'users' - All columns match
✅ Table 'rooms' - All columns match  
✅ Table 'catalog' - All columns match
✅ Table 'candidates' - All columns match
✅ Table 'votes' - All columns match
✅ Table 'chat' - All columns match
✅ Table 'emojis' - All columns match
✅ Table 'expenses' - All columns match
✅ Table 'sync_events' - All columns match
```

All code is using your exact schema! ✅
