"""PawPal system skeleton generated from diagrams/uml_draft.mmd."""

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum


class Frequency(Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DayOfWeek(Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


@dataclass
class Task:
    description: str
    duration_minutes: int
    frequency: Frequency
    priority: Priority
    scheduled_start: datetime | None = None
    completed: bool = False

    def mark_complete(self) -> None:
        ...


@dataclass
class AvailabilityWindow:
    day: DayOfWeek
    start: time
    end: time
    capacity_minutes: int
    scheduled: list["ScheduledTask"] = field(default_factory=list)

    def remaining_minutes(self) -> int:
        ...


@dataclass
class ScheduledTask:
    """A concrete occurrence of a Task assigned to a window on a date."""

    task: Task
    window: AvailabilityWindow
    date: datetime
    completed: bool = False

    def mark_complete(self) -> None:
        ...


@dataclass
class Pet:
    name: str
    type: str
    owner: "Owner | None" = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        ...


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)
    availability: list[AvailabilityWindow] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        ...

    def add_availability(self, window: AvailabilityWindow) -> None:
        ...


@dataclass
class Scheduler:
    owner: Owner

    def auto_assign(self) -> list[Task]:
        ...

    def pending_tasks(self) -> list[Task]:
        ...

    def reschedule(self) -> None:
        ...
