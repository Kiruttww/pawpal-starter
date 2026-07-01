"""PawPal system implementation generated from diagrams/uml_draft.mmd."""

from __future__ import annotations

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
        """Mark this task as completed."""
        self.completed = True


@dataclass
class AvailabilityWindow:
    day: DayOfWeek
    start: time
    end: time
    capacity_minutes: int
    scheduled: list["ScheduledTask"] = field(default_factory=list)

    def remaining_minutes(self) -> int:
        """Return the unused capacity of this window in minutes."""
        used = sum(st.task.duration_minutes for st in self.scheduled)
        return self.capacity_minutes - used

    def can_fit(self, task: "Task") -> bool:
        """Return True if the task fits in this window's remaining capacity."""
        return task.duration_minutes <= self.remaining_minutes()


@dataclass
class ScheduledTask:
    """A concrete occurrence of a Task assigned to a window on a date."""

    task: Task
    window: AvailabilityWindow
    date: datetime
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this occurrence and its underlying task as completed."""
        self.completed = True
        self.task.mark_complete()


@dataclass
class Pet:
    name: str
    type: str
    owner: "Owner | None" = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)
    availability: list[AvailabilityWindow] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and set the pet's owner back-reference."""
        pet.owner = self
        self.pets.append(pet)

    def add_availability(self, window: AvailabilityWindow) -> None:
        """Add an availability window to this owner's schedule."""
        self.availability.append(window)


@dataclass
class Scheduler:
    owner: Owner

    def _all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def _scheduled_tasks(self) -> set[int]:
        """Ids of tasks that already have a ScheduledTask on some window."""
        return {
            id(st.task)
            for window in self.owner.availability
            for st in window.scheduled
        }

    def pending_tasks(self) -> list[Task]:
        """Tasks that are neither completed nor already scheduled."""
        scheduled = self._scheduled_tasks()
        return [
            task
            for task in self._all_tasks()
            if not task.completed and id(task) not in scheduled
        ]

    def auto_assign(self) -> list[Task]:
        """Greedily place pending tasks into the first window with capacity.

        Higher-priority tasks are placed first. Returns the tasks that were
        successfully assigned.
        """
        assigned: list[Task] = []
        priority_rank = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

        pending = sorted(
            self.pending_tasks(),
            key=lambda t: priority_rank[t.priority],
        )

        for task in pending:
            for window in self.owner.availability:
                if window.can_fit(task):
                    scheduled = ScheduledTask(
                        task=task,
                        window=window,
                        date=datetime.combine(datetime.today(), window.start),
                    )
                    window.scheduled.append(scheduled)
                    task.scheduled_start = scheduled.date
                    assigned.append(task)
                    break

        return assigned

    def reschedule(self) -> None:
        """Drop all incomplete assignments and assign again from scratch."""
        for window in self.owner.availability:
            window.scheduled = [st for st in window.scheduled if st.completed]
        for task in self._all_tasks():
            if not task.completed:
                task.scheduled_start = None
        self.auto_assign()
