from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import ClassVar

from app.services.util import generate_unique_id, date_lower_than_today_error, event_not_found_error, \
    reminder_not_found_error, slot_not_available_error


from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Dict, Optional

from app.services.util import date_lower_than_today_error, event_not_found_error, reminder_not_found_error, slot_not_available_error

@dataclass
class Reminder:
    date_time: datetime
    type: str = field(default="email")

    def __str__(self) -> str:
        return f"Reminder on {self.date_time} of type {self.type}"

    EMAIL = "email"
    SYSTEM = "system"

@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time
    reminders: List[Reminder] = field(default_factory=list)
    id: str = field(default_factory=lambda: generate_unique_id())

    def add_reminder(self, date_time: datetime, type_: str = "email") -> None:
        reminder = Reminder(date_time, type_)
        self.reminders.append(reminder)

    def delete_reminder(self, reminder_index: int) -> None:
        if 0 <= reminder_index < len(self.reminders):
            del self.reminders[reminder_index]
        else:
            reminder_not_found_error()

    def __str__(self) -> str:
        return f"ID: {self.id}\nEvent title: {self.title}\nDescription: {self.description}\nTime: {self.start_at} - {self.end_at}"

class Day:
    def __init__(self, date_: date) -> None:
        self.date_ = date_
        self.slots: Dict[time, Optional[str]] = {}
        self._init_slots()

    def _init_slots(self) -> None:
        for hour in range(24):
            for minute in range(0, 60, 15):
                self.slots[time(hour, minute)] = None

    def add_event(self, event_id: str, start_at: time, end_at: time) -> None:
        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot]:
                    slot_not_available_error()
                else:
                    self.slots[slot] = event_id

    def delete_event(self, event_id: str) -> None:
        deleted = False
        for slot, saved_id in self.slots.items():
            if saved_id == event_id:
                self.slots[slot] = None
                deleted = True
        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time) -> None:
        for slot in self.slots:
            if self.slots[slot] == event_id:
                self.slots[slot] = None

        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot]:
                    slot_not_available_error()
                else:
                    self.slots[slot] = event_id

class Calendar:
    def __init__(self) -> None:
        self.days: Dict[date, Day] = {}
        self.events: Dict[str, Event] = {}

    def add_event(self, title: str, description: str, date_: date, start_at: time, end_at: time) -> str:
        if date_ < datetime.now().date():
            date_lower_than_today_error()

        if date_ not in self.days:
            self.days[date_] = Day(date_)

        event = Event(title, description, date_, start_at, end_at)
        self.days[date_].add_event(event.id, start_at, end_at)
        self.events[event.id] = event
        return event.id

    def add_reminder(self, event_id: str, date_time: datetime, type_: str = "email") -> None:
        if event_id not in self.events:
            event_not_found_error()

        self.events[event_id].add_reminder(date_time, type_)

    def find_available_slots(self, date_: date) -> List[time]:
        if date_ not in self.days:
            return [time(hour, minute) for hour in range(24) for minute in range(0, 60, 15)]

        day = self.days[date_]
        available_slots = []
        for slot, event_id in day.slots.items():
            if event_id is None:
                available_slots.append(slot)
        return available_slots

    def update_event(self, event_id: str, title: str, description: str, date_: date, start_at: time, end_at: time) -> None:
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()

        is_new_date = False

        if event.date_ != date_:
            self.delete
