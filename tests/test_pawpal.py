"""Tests for the PawPal system.

Organized by feature:
  - TestSorting          : sort_by_time ordering
  - TestRecurrence       : _next_occurrence date math + complete_task spawning
  - TestConflictDetection: overlap detection and its boundaries
  - TestAutoAssign       : greedy placement, capacity, priority ordering
"""

from datetime import datetime, time, timedelta

from pawpal_system import (
    AvailabilityWindow,
    DayOfWeek,
    Frequency,
    Owner,
    Pet,
    Priority,
    ScheduledTask,
    Scheduler,
    Task,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def make_owner_with_pet(pet_name="Rex", pet_type="dog"):
    """Return (owner, pet) with the pet already attached to the owner."""
    owner = Owner(name="Alex")
    pet = Pet(name=pet_name, type=pet_type)
    owner.add_pet(pet)
    return owner, pet


def place(window, pet, description, start, duration=30):
    """Manually add a ScheduledTask to a window at an exact start datetime."""
    task = Task(description, duration, Frequency.ONCE, Priority.MEDIUM,
                scheduled_start=start)
    pet.add_task(task)
    window.scheduled.append(ScheduledTask(task=task, window=window, date=start))
    return task


# --------------------------------------------------------------------------- #
# Sorting
# --------------------------------------------------------------------------- #

class TestSorting:
    def test_scheduled_tasks_sorted_ascending_by_time(self):
        owner, pet = make_owner_with_pet()
        today = datetime.today()
        pet.add_task(Task("Evening", 30, Frequency.DAILY, Priority.LOW,
                          scheduled_start=datetime.combine(today, time(18, 0))))
        pet.add_task(Task("Morning", 30, Frequency.DAILY, Priority.HIGH,
                          scheduled_start=datetime.combine(today, time(8, 0))))
        pet.add_task(Task("Noon", 30, Frequency.DAILY, Priority.MEDIUM,
                          scheduled_start=datetime.combine(today, time(12, 0))))

        ordered = [t.description for t in Scheduler(owner).sort_by_time()]

        assert ordered == ["Morning", "Noon", "Evening"]

    def test_unscheduled_tasks_sort_last(self):
        owner, pet = make_owner_with_pet()
        today = datetime.today()
        pet.add_task(Task("No time", 30, Frequency.DAILY, Priority.LOW))
        pet.add_task(Task("Has time", 30, Frequency.DAILY, Priority.HIGH,
                          scheduled_start=datetime.combine(today, time(9, 0))))

        ordered = [t.description for t in Scheduler(owner).sort_by_time()]

        assert ordered == ["Has time", "No time"]


# --------------------------------------------------------------------------- #
# Recurrence
# --------------------------------------------------------------------------- #

class TestRecurrence:
    def test_once_has_no_next_occurrence(self):
        assert Scheduler._next_occurrence(datetime(2026, 6, 30), Frequency.ONCE) is None

    def test_daily_advances_one_day(self):
        base = datetime(2026, 6, 30, 8, 0)
        assert Scheduler._next_occurrence(base, Frequency.DAILY) == base + timedelta(days=1)

    def test_monthly_clamps_jan31_to_feb29_leap_year(self):
        nxt = Scheduler._next_occurrence(datetime(2024, 1, 31), Frequency.MONTHLY)
        assert (nxt.year, nxt.month, nxt.day) == (2024, 2, 29)

    def test_monthly_december_rolls_over_year(self):
        nxt = Scheduler._next_occurrence(datetime(2026, 12, 10), Frequency.MONTHLY)
        assert (nxt.year, nxt.month, nxt.day) == (2027, 1, 10)

    def test_complete_task_spawns_next_occurrence_on_same_pet(self):
        owner, pet = make_owner_with_pet()
        task = Task("Walk", 30, Frequency.DAILY, Priority.HIGH,
                   scheduled_start=datetime(2026, 6, 30, 8, 0))
        pet.add_task(task)

        nxt = Scheduler(owner).complete_task(task)

        assert task.completed is True
        assert nxt is not None and nxt.completed is False
        assert nxt.scheduled_start == datetime(2026, 7, 1, 8, 0)
        assert nxt in pet.tasks

    def test_complete_task_once_does_not_spawn(self):
        owner, pet = make_owner_with_pet()
        task = Task("Vet visit", 60, Frequency.ONCE, Priority.HIGH,
                   scheduled_start=datetime(2026, 6, 30, 8, 0))
        pet.add_task(task)

        nxt = Scheduler(owner).complete_task(task)

        assert nxt is None
        assert task.completed is True
        assert len(pet.tasks) == 1


# --------------------------------------------------------------------------- #
# Conflict detection
# --------------------------------------------------------------------------- #

class TestConflictDetection:
    def _setup(self):
        owner, pet = make_owner_with_pet()
        window = AvailabilityWindow(DayOfWeek.MONDAY, time(8, 0), time(12, 0), 240)
        owner.add_availability(window)
        return owner, pet, window

    def test_no_conflicts_returns_empty_list(self):
        owner, pet, window = self._setup()
        today = datetime.today()
        place(window, pet, "A", datetime.combine(today, time(8, 0)), 30)
        place(window, pet, "B", datetime.combine(today, time(9, 0)), 30)

        assert Scheduler(owner).detect_conflicts() == []

    def test_partial_overlap_conflicts(self):
        owner, pet, window = self._setup()
        today = datetime.today()
        place(window, pet, "A", datetime.combine(today, time(8, 0)), 30)   # 8:00-8:30
        place(window, pet, "B", datetime.combine(today, time(8, 15)), 30)  # 8:15-8:45

        assert len(Scheduler(owner).detect_conflicts()) == 1

    def test_back_to_back_does_not_conflict(self):
        # Key boundary: one ends exactly when the next begins => no conflict.
        owner, pet, window = self._setup()
        today = datetime.today()
        place(window, pet, "A", datetime.combine(today, time(8, 0)), 30)   # 8:00-8:30
        place(window, pet, "B", datetime.combine(today, time(8, 30)), 30)  # 8:30-9:00

        assert Scheduler(owner).detect_conflicts() == []


# --------------------------------------------------------------------------- #
# Auto-assignment / capacity
# --------------------------------------------------------------------------- #

class TestAutoAssign:
    def test_task_placed_reduces_remaining_capacity(self):
        owner, pet = make_owner_with_pet()
        window = AvailabilityWindow(DayOfWeek.MONDAY, time(8, 0), time(9, 0), 60)
        owner.add_availability(window)
        pet.add_task(Task("Walk", 20, Frequency.DAILY, Priority.HIGH))

        assigned = Scheduler(owner).auto_assign()

        assert len(assigned) == 1
        assert window.remaining_minutes() == 40

    def test_task_too_large_stays_pending(self):
        owner, pet = make_owner_with_pet()
        window = AvailabilityWindow(DayOfWeek.MONDAY, time(8, 0), time(9, 0), 60)
        owner.add_availability(window)
        big = Task("Grooming", 90, Frequency.ONCE, Priority.HIGH)
        pet.add_task(big)

        scheduler = Scheduler(owner)
        assigned = scheduler.auto_assign()

        assert assigned == []
        assert big in scheduler.pending_tasks()

    def test_higher_priority_placed_first(self):
        owner, pet = make_owner_with_pet()
        # Only room for one 40-min task.
        window = AvailabilityWindow(DayOfWeek.MONDAY, time(8, 0), time(9, 0), 40)
        owner.add_availability(window)
        pet.add_task(Task("Low job", 40, Frequency.DAILY, Priority.LOW))
        pet.add_task(Task("High job", 40, Frequency.DAILY, Priority.HIGH))

        Scheduler(owner).auto_assign()

        assert len(window.scheduled) == 1
        assert window.scheduled[0].task.description == "High job"

    def test_sequential_tasks_get_distinct_start_times(self):
        owner, pet = make_owner_with_pet()
        window = AvailabilityWindow(DayOfWeek.MONDAY, time(8, 0), time(12, 0), 240)
        owner.add_availability(window)
        pet.add_task(Task("First", 30, Frequency.DAILY, Priority.HIGH))
        pet.add_task(Task("Second", 30, Frequency.DAILY, Priority.HIGH))

        Scheduler(owner).auto_assign()

        starts = sorted(st.date.time() for st in window.scheduled)
        assert starts == [time(8, 0), time(8, 30)]
