import streamlit as st
from datetime import time

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

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.markdown("### Pets")
st.caption("Add one or more pets. Each pet is attached to the owner and persists across reruns.")

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, type=species))

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": pet.name, "species": pet.type} for pet in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Availability")
st.caption("Add time windows the owner has free. The scheduler places tasks into these windows.")

acol1, acol2, acol3, acol4 = st.columns(4)
with acol1:
    day = st.selectbox("Day", list(DayOfWeek), format_func=lambda d: d.value.title())
with acol2:
    start = st.time_input("Start", value=time(9, 0))
with acol3:
    end = st.time_input("End", value=time(17, 0))
with acol4:
    capacity = st.number_input("Capacity (min)", min_value=1, max_value=1440, value=120)

if st.button("Add availability"):
    owner.add_availability(
        AvailabilityWindow(day=day, start=start, end=end, capacity_minutes=int(capacity))
    )

if owner.availability:
    st.write("Current availability:")
    st.table(
        [
            {
                "day": w.day.value.title(),
                "start": w.start.strftime("%H:%M"),
                "end": w.end.strftime("%H:%M"),
                "capacity": w.capacity_minutes,
                "remaining": w.remaining_minutes(),
            }
            for w in owner.availability
        ]
    )
else:
    st.info("No availability windows yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add care tasks for a pet. These feed into the scheduler.")

PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

if not owner.pets:
    st.info("Add a pet before creating tasks.")
else:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        frequency = st.selectbox(
            "Frequency", list(Frequency), format_func=lambda f: f.value.title()
        )
    with col5:
        pet_index = st.selectbox(
            "For pet", range(len(owner.pets)), format_func=lambda i: owner.pets[i].name
        )

    if st.button("Add task"):
        owner.pets[pet_index].add_task(
            Task(
                description=task_title,
                duration_minutes=int(duration),
                frequency=frequency,
                priority=PRIORITY_MAP[priority],
            )
        )

task_rows = [
    {
        "pet": pet.name,
        "task": task.description,
        "minutes": task.duration_minutes,
        "priority": task.priority.value,
        "frequency": task.frequency.value,
        "scheduled": task.scheduled_start.strftime("%H:%M") if task.scheduled_start else "—",
        "done": task.completed,
    }
    for pet in owner.pets
    for task in pet.tasks
]

if task_rows:
    st.write("Current tasks:")
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Places pending tasks into availability windows, highest priority first.")

bcol1, bcol2 = st.columns(2)
with bcol1:
    generate = st.button("Generate schedule")
with bcol2:
    redo = st.button("Reschedule (clear incomplete & redo)")

if generate:
    assigned = scheduler.auto_assign()
    st.success(f"Assigned {len(assigned)} task(s).")
if redo:
    scheduler.reschedule()
    st.success("Cleared incomplete assignments and rescheduled from scratch.")

if generate or redo:
    scheduled_rows = [
        {
            "task": occurrence.task.description,
            "day": occurrence.window.day.value.title(),
            "start": occurrence.date.strftime("%H:%M"),
            "minutes": occurrence.task.duration_minutes,
        }
        for window in owner.availability
        for occurrence in window.scheduled
    ]
    if scheduled_rows:
        st.write("Planned schedule:")
        st.table(scheduled_rows)

    pending = scheduler.pending_tasks()
    if pending:
        st.warning(
            "Could not place: "
            + ", ".join(t.description for t in pending)
            + " — not enough availability capacity."
        )
    elif not scheduled_rows:
        st.info("Nothing to schedule yet. Add pets, tasks, and availability first.")
