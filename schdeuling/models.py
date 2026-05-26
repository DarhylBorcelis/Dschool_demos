"""
models.py — In-memory data store (no database needed for the demo).
Replace with SQLAlchemy / SQLite later by swapping out Store methods only.
"""

from dataclasses import dataclass, field
from typing import Optional, List
import re


# ── Constants ──────────────────────────────────────────────────────────────

ACCOUNT_TYPES = ["wish", "eiken", "power"]
DAYS = ["mon", "tue", "wed"]          # the rolling 3-day window


# ── Slot helpers ───────────────────────────────────────────────────────────

def parse_range(time_str: str):
    """
    Accept '9-12', '10-11', '9:30-11' etc.
    Returns (start_hour_float, end_hour_float) or raises ValueError.
    """
    m = re.match(r"^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$", time_str.strip())
    if not m:
        raise ValueError(f"Invalid time range '{time_str}'. Use format like '9-12' or '10-11'.")
    start, end = float(m.group(1)), float(m.group(2))
    if start >= end:
        raise ValueError("Start time must be before end time.")
    if start < 0 or end > 24:
        raise ValueError("Hours must be between 0 and 24.")
    return start, end


def expand_to_slots(time_str: str) -> List[str]:
    """
    '9-12' → ['9-10', '10-11', '11-12']
    Each slot is exactly 1 hour wide.
    """
    start, end = parse_range(time_str)
    slots = []
    h = start
    while h < end:
        slots.append(f"{int(h)}-{int(h+1)}")
        h += 1
    return slots


def slots_overlap(a: str, b: str) -> bool:
    """True if two slot strings share any time."""
    sa, ea = parse_range(a)
    sb, eb = parse_range(b)
    return sa < eb and sb < ea


# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class Teacher:
    teacher_id: str          # e.g. "jason", "me"
    name: str


@dataclass
class ScheduleSlot:
    slot_id: int
    teacher_id: str
    day: str                 # 'mon' | 'tue' | 'wed'
    time: str                # '10-11'  (always 1-hour after expansion)
    account_type: Optional[str] = None   # None = teacher availability block
    is_rest: bool = False


# ── In-memory store ─────────────────────────────────────────────────────────

class Store:
    """All application state lives here during the demo."""

    def __init__(self):
        self._teachers: dict[str, Teacher] = {}
        self._slots: List[ScheduleSlot] = []
        self._next_id = 1

        # Seed a couple of teachers
        self.add_teacher("jason", "Jason")
        self.add_teacher("maria", "Maria")
        self.add_teacher("dar", "Dar")

    # ── Teachers ────────────────────────────────────────────────────────────

    def add_teacher(self, teacher_id: str, name: str):
        teacher_id = teacher_id.strip().lower()
        self._teachers[teacher_id] = Teacher(teacher_id, name)

    def get_teachers(self) -> List[Teacher]:
        return list(self._teachers.values())

    def teacher_exists(self, teacher_id: str) -> bool:
        return teacher_id.strip().lower() in self._teachers

    # ── Availability (teacher side) ─────────────────────────────────────────

    def add_availability(self, teacher_id: str, day: str, time_range: str) -> List[ScheduleSlot]:
        """
        Teacher marks themselves free for a range like '9-12'.
        Expands to 1-hour slots.  Skips duplicates.
        Returns the list of created slots.
        """
        teacher_id = teacher_id.strip().lower()
        if not self.teacher_exists(teacher_id):
            raise ValueError(f"Teacher '{teacher_id}' not found.")
        day = day.strip().lower()
        if day not in DAYS:
            raise ValueError(f"Day must be one of {DAYS}.")

        created = []
        for slot_str in expand_to_slots(time_range):
            # Skip if already exists
            if self._slot_exists(teacher_id, day, slot_str):
                continue
            s = ScheduleSlot(
                slot_id=self._next_id,
                teacher_id=teacher_id,
                day=day,
                time=slot_str,
                account_type=None,
                is_rest=False,
            )
            self._slots.append(s)
            self._next_id += 1
            created.append(s)
        return created

    def _slot_exists(self, teacher_id, day, time) -> bool:
        return any(
            s.teacher_id == teacher_id and s.day == day and s.time == time
            for s in self._slots
        )

    # ── Assignments (admin side) ────────────────────────────────────────────

    def assign_class(self, teacher_id: str, day: str, time_str: str, account_type: str) -> ScheduleSlot:
        """
        Admin assigns a class to a teacher.
        Teacher must have an availability slot that covers the requested time.
        """
        teacher_id = teacher_id.strip().lower()
        if not self.teacher_exists(teacher_id):
            raise ValueError(f"Teacher '{teacher_id}' not found.")
        day = day.strip().lower()
        if day not in DAYS:
            raise ValueError(f"Day must be one of {DAYS}.")
        account_type = account_type.strip().lower()
        if account_type not in ACCOUNT_TYPES:
            raise ValueError(f"Account type must be one of {ACCOUNT_TYPES}.")

        # Validate the time is a single 1-hour slot
        slots = expand_to_slots(time_str)
        if len(slots) != 1:
            raise ValueError("Admin assignment must be exactly 1 hour (e.g. '10-11').")
        slot_str = slots[0]

        # Check teacher has that availability
        available = self._slot_exists(teacher_id, day, slot_str)
        if not available:
            raise ValueError(
                f"Teacher '{teacher_id}' is NOT available on {day} at {slot_str}."
            )

        # Check not already assigned
        already = next(
            (s for s in self._slots
             if s.teacher_id == teacher_id and s.day == day
             and s.time == slot_str and s.account_type is not None),
            None
        )
        if already:
            raise ValueError(f"That slot is already assigned as '{already.account_type}'.")

        # Update the availability slot in-place (mark it as assigned)
        avail_slot = next(
            s for s in self._slots
            if s.teacher_id == teacher_id and s.day == day and s.time == slot_str
        )
        avail_slot.account_type = account_type
        return avail_slot

    # ── Queries ─────────────────────────────────────────────────────────────

    def get_available_teachers(self, day: str, time_str: str) -> List[Teacher]:
        """Return teachers who have a free (unassigned) slot covering time_str on day."""
        day = day.strip().lower()
        slots_needed = expand_to_slots(time_str)
        result = []
        for teacher in self._teachers.values():
            if all(
                any(
                    s.teacher_id == teacher.teacher_id
                    and s.day == day
                    and s.time == needed
                    and s.account_type is None   # still free
                    for s in self._slots
                )
                for needed in slots_needed
            ):
                result.append(teacher)
        return result

    def get_schedule(self, day: Optional[str] = None, teacher_id: Optional[str] = None) -> List[ScheduleSlot]:
        slots = self._slots
        if day:
            slots = [s for s in slots if s.day == day.strip().lower()]
        if teacher_id:
            slots = [s for s in slots if s.teacher_id == teacher_id.strip().lower()]
        return sorted(slots, key=lambda s: (s.day, s.teacher_id, s.time))

    def remove_availability(self, teacher_id: str, day: str, time_str: str):
        """Remove an availability slot (only if unassigned)."""
        teacher_id = teacher_id.strip().lower()
        slots = expand_to_slots(time_str)
        for slot_str in slots:
            target = next(
                (s for s in self._slots
                 if s.teacher_id == teacher_id and s.day == day and s.time == slot_str),
                None
            )
            if target is None:
                raise ValueError(f"Slot {slot_str} on {day} not found for {teacher_id}.")
            if target.account_type is not None:
                raise ValueError(f"Slot {slot_str} is already assigned; unassign it first.")
            self._slots.remove(target)
