"""PawPal system implementation generated from diagrams/uml_draft.mmd."""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
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

    @property
    def end(self) -> datetime:
        """The datetime this occurrence finishes (start + task duration)."""
        return self.date + timedelta(minutes=self.task.duration_minutes)

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

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Both filters are optional. When a filter is ``None`` it is ignored, so
        calling with no arguments returns every task. ``pet_name`` matches
        case-insensitively.
        """
        results: list[Task] = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by their scheduled start time.

        Uses a lambda key that turns each task's ``scheduled_start`` into an
        ``"HH:MM"`` string and sorts on it. Tasks with no scheduled time sort
        last (they get the sentinel ``"99:99"``).
        """
        return sorted(
            self._all_tasks(),
            key=lambda t: t.scheduled_start.strftime("%H:%M")
            if t.scheduled_start
            else "99:99",
        )

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
                    # Start where the previous tasks in this window left off so
                    # each occurrence gets its own clock time (a real timeline)
                    # instead of every task sharing window.start.
                    used = sum(st.task.duration_minutes for st in window.scheduled)
                    start_dt = datetime.combine(
                        datetime.today(), window.start
                    ) + timedelta(minutes=used)
                    scheduled = ScheduledTask(
                        task=task,
                        window=window,
                        date=start_dt,
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

    @staticmethod
    def _next_occurrence(base: datetime, frequency: Frequency) -> datetime | None:
        """Return the next due datetime after ``base`` for a recurring task.

        Returns ``None`` for ``Frequency.ONCE`` (no recurrence). DAILY and
        WEEKLY use ``timedelta`` for exact day math; MONTHLY advances one
        calendar month and clamps the day to the last valid day of that month
        (e.g. Jan 31 -> Feb 28).
        """
        if frequency == Frequency.DAILY:
            return base + timedelta(days=1)
        if frequency == Frequency.WEEKLY:
            return base + timedelta(weeks=1)
        if frequency == Frequency.MONTHLY:
            month = base.month + 1
            year = base.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            last_day = calendar.monthrange(year, month)[1]
            return base.replace(year=year, month=month, day=min(base.day, last_day))
        return None  # ONCE

    def complete_task(self, task: Task) -> Task | None:
        """Mark ``task`` complete and spawn its next occurrence if it recurs.

        Returns the newly created next-occurrence Task, or ``None`` when the
        task was already complete or does not recur (``Frequency.ONCE``). The
        new task is a fresh, uncompleted copy whose ``scheduled_start`` is the
        computed next due date; it is appended to the same pet that owns
        ``task``.
        """
        if task.completed:
            return None
        task.mark_complete()

        # Base the next due date on when this task was scheduled, or midnight
        # today if it was never placed into a window.
        base = task.scheduled_start or datetime.combine(datetime.today(), time())
        next_start = self._next_occurrence(base, task.frequency)
        if next_start is None:
            return None

        next_task = Task(
            description=task.description,
            duration_minutes=task.duration_minutes,
            frequency=task.frequency,
            priority=task.priority,
            scheduled_start=next_start,
        )

        # Append to the same pet that owns the completed task.
        for pet in self.owner.pets:
            if any(t is task for t in pet.tasks):
                pet.add_task(next_task)
                break

        return next_task

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for scheduled tasks that overlap in time.

        Two occurrences conflict when their ``[start, end)`` intervals
        intersect (this covers identical start times), whether they belong to
        the same pet or different pets. Back-to-back tasks (one ends exactly
        when the next begins) do not conflict.

        Lightweight: occurrences are sorted by start time and swept once, so a
        task is only compared against later tasks until one starts after it
        ends. Returns an empty list when there are no conflicts — it never
        raises.
        """
        occurrences = [
            st for window in self.owner.availability for st in window.scheduled
        ]
        occurrences.sort(key=lambda st: st.date)

        pet_by_task = {
            id(task): pet for pet in self.owner.pets for task in pet.tasks
        }

        def label(st: "ScheduledTask") -> str:
            pet = pet_by_task.get(id(st.task))
            who = pet.name if pet else "unknown pet"
            return (
                f"'{st.task.description}' ({who}) "
                f"{st.date:%H:%M}-{st.end:%H:%M}"
            )

        warnings: list[str] = []
        for i, a in enumerate(occurrences):
            for b in occurrences[i + 1:]:
                # Sorted by start, so once b starts at/after a ends, neither b
                # nor any later occurrence can overlap a.
                if b.date >= a.end:
                    break
                warnings.append(f"⚠ Conflict: {label(a)} overlaps {label(b)}")

        return warnings
