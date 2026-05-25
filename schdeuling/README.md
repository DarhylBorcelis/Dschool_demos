# Scheduling Demo

A PyQt5/PySide6 desktop scheduling app — **no database required**.

## Quick Start

```bash
# Install dependencies (pick one)
pip install PyQt5
# or
pip install PySide6

# Run
python main.py
```

## How it works

### Data model (models.py)

| Field         | Type              | Notes                                      |
|---------------|-------------------|--------------------------------------------|
| `teacher_id`  | str (FK-like)     | Unique key for a teacher                   |
| `day`         | str               | `mon`, `tue`, `wed`                        |
| `time`        | str               | Always 1-hour slot: `10-11`               |
| `account_type`| str \| None       | `wish`, `eiken`, `power` — None = free     |
| `is_rest`     | bool              | Reserved for future use                    |

### 2-way scheduling flow

**Teacher side:**
1. Go to *Availability* tab
2. Pick teacher, day, and a range like `9-12`
3. Backend auto-expands to slots: `9-10`, `10-11`, `11-12`

**Admin side:**
1. Go to *Admin Assign* tab
2. Choose day + a specific 1-hour slot (e.g. `10-11`)
3. Click **Search** → only teachers available that slot appear
4. Select a teacher, pick class type (wish/eiken/power), click **Assign**

### Range expansion

`9-12` → three 1-hour ScheduleSlot objects: `9-10`, `10-11`, `11-12`

The admin query checks whether the teacher has a **free** (unassigned) slot covering the requested time.

## Replacing the in-memory store

All state is in `models.py → Store`.  
Swap the `_teachers` dict and `_slots` list for SQLAlchemy session calls — the UI code in `main.py` never touches storage directly.
