"""PawPal demo: build an owner with pets and tasks, then print today's schedule."""

from datetime import datetime, time

from pawpal_system import (
    AvailabilityWindow,
    DayOfWeek,
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    ScheduledTask,
    Task,
)


def main() -> None:
    # Owner and pets.
    owner = Owner(name="Alex")
    rex = Pet(name="Rex", type="dog")
    milo = Pet(name="Milo", type="cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Four tasks total, two per pet — added deliberately out of time order so
    # sorting has something to fix (evening task added before morning, etc.).
    rex.add_task(Task("Evening walk", 30, Frequency.DAILY, Priority.MEDIUM))
    milo.add_task(Task("Litter cleanup", 10, Frequency.DAILY, Priority.LOW))
    rex.add_task(Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH))
    milo.add_task(Task("Feed breakfast", 15, Frequency.DAILY, Priority.HIGH))

    # Availability windows so tasks land at different times of day.
    owner.add_availability(
        AvailabilityWindow(DayOfWeek.MONDAY, time(8, 0), time(9, 0), 60)
    )
    owner.add_availability(
        AvailabilityWindow(DayOfWeek.MONDAY, time(18, 0), time(19, 0), 60)
    )

    # Let the scheduler place tasks into windows.
    scheduler = Scheduler(owner)
    scheduler.auto_assign()

    # Map each task back to its pet (Task has no pet back-reference in the model).
    pet_by_task = {id(task): pet for pet in owner.pets for task in pet.tasks}

    # Mark one task done so the completion filter has something to show.
    for task in rex.tasks:
        if task.description == "Morning walk":
            task.mark_complete()

    # Print today's schedule.
    print(f"Today's schedule for {owner.name} ({datetime.today():%Y-%m-%d}):")
    print("-" * 40)
    for window in owner.availability:
        print(f"{window.start:%H:%M}-{window.end:%H:%M}")
        for st in window.scheduled:
            pet = pet_by_task[id(st.task)]
            print(f"  • {st.task.description} "
                  f"[{st.task.priority.value}, {st.task.duration_minutes} min] "
                  f"— {pet.name} ({pet.type})")
        print(f"  ({window.remaining_minutes()} min free)")

    # Tasks were added out of order — sort_by_time() rebuilds the timeline.
    print("\nTasks sorted by time:")
    print("-" * 40)
    for task in scheduler.sort_by_time():
        when = task.scheduled_start.strftime("%H:%M") if task.scheduled_start else "—"
        print(f"  {when}  {task.description} [{task.priority.value}]")

    # Filter by completion status.
    print("\nPending tasks (filter completed=False):")
    print("-" * 40)
    for task in scheduler.filter_tasks(completed=False):
        print(f"  • {task.description}")

    print("\nCompleted tasks (filter completed=True):")
    print("-" * 40)
    for task in scheduler.filter_tasks(completed=True):
        print(f"  • {task.description}")

    # Filter by pet name.
    print("\nMilo's tasks (filter pet_name='Milo'):")
    print("-" * 40)
    for task in scheduler.filter_tasks(pet_name="Milo"):
        print(f"  • {task.description}")

    # --- Conflict detection demo (isolated scenario) -------------------
    # Deliberately book two tasks into the exact same 08:00 slot to prove the
    # scheduler reports a warning instead of silently double-booking.
    print("\nConflict detection:")
    print("-" * 40)
    demo_owner = Owner(name="Sam")
    fido = Pet(name="Fido", type="dog")
    demo_owner.add_pet(fido)
    window = AvailabilityWindow(DayOfWeek.MONDAY, time(8, 0), time(9, 0), 60)
    demo_owner.add_availability(window)

    same_time = datetime.combine(datetime.today(), time(8, 0))
    for desc in ("Brush teeth", "Play fetch"):
        task = Task(desc, 15, Frequency.DAILY, Priority.MEDIUM, scheduled_start=same_time)
        fido.add_task(task)
        window.scheduled.append(ScheduledTask(task=task, window=window, date=same_time))

    demo_scheduler = Scheduler(demo_owner)
    conflicts = demo_scheduler.detect_conflicts()
    if conflicts:
        for msg in conflicts:
            print(msg)
    else:
        print("  No conflicts detected.")


if __name__ == "__main__":
    main()
