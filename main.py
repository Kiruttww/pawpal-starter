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
    Task,
)


def main() -> None:
    # Owner and pets.
    owner = Owner(name="Alex")
    rex = Pet(name="Rex", type="dog")
    milo = Pet(name="Milo", type="cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Four tasks total, two per pet.
    rex.add_task(Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH))
    rex.add_task(Task("Evening walk", 30, Frequency.DAILY, Priority.MEDIUM))
    milo.add_task(Task("Feed breakfast", 15, Frequency.DAILY, Priority.HIGH))
    milo.add_task(Task("Litter cleanup", 10, Frequency.DAILY, Priority.LOW))

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


if __name__ == "__main__":
    main()
