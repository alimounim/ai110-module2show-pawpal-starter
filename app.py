import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session state init ────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", "jordan@email.com", 2.0)

owner: Owner = st.session_state.owner

# ── Owner info ────────────────────────────────────────────────────────────────
st.subheader("Owner")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Name", owner.name)
with col2:
    st.metric("Email", owner.email)
with col3:
    st.metric("Time available", f"{owner.time_available_per_day} hrs/day")

# ── Add a pet ─────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    if pet_name.strip() == "":
        st.warning("Please enter a pet name.")
    elif any(p.name == pet_name for p in owner.pets):
        st.warning(f"A pet named '{pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=pet_name, specie=species, age=age, weight=0.0))
        st.success(f"{pet_name} added!")
        st.rerun()

if owner.pets:
    st.write("**Pets:**", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# ── Add a task ────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    selected_pet_name = st.selectbox("Assign to pet", [p.name for p in owner.pets])
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly", "as needed"])
    with col5:
        scheduled_time = st.time_input("Scheduled time", value=None, help="When should this task happen?")

    if st.button("Add task"):
        time_str = scheduled_time.strftime("%H:%M") if scheduled_time else "00:00"
        new_task = Task(
            name=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            scheduled_time=time_str,
        )
        selected_pet.add_task(new_task)
        st.success(f'"{task_title}" added to {selected_pet.name} at {time_str}!')
        st.rerun()

    if selected_pet.tasks:
        st.write(f"**{selected_pet.name}'s tasks:**")
        st.table([
            {
                "Task": t.name,
                "Time": t.scheduled_time,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Frequency": t.frequency,
                "Done": "✓" if t.completed else "—",
            }
            for t in selected_pet.tasks
        ])
    else:
        st.info(f"No tasks for {selected_pet.name} yet.")

# ── Schedule view ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Daily Schedule")

if not owner.pets or not any(p.tasks for p in owner.pets):
    st.info("Add at least one pet with a task to generate a schedule.")
else:
    scheduler = Scheduler(owner)

    # ── Conflict warnings ─────────────────────────────────────────────────────
    conflicts = scheduler.get_conflicts()
    if conflicts:
        st.markdown("#### ⚠️ Scheduling Conflicts Detected")
        for msg in conflicts:
            if msg.startswith("[HARD"):
                st.error(
                    f"**HARD conflict** — two tasks for the *same pet* overlap. "
                    f"You cannot do both at once.\n\n{msg}",
                    icon="🚫",
                )
            else:
                st.warning(
                    f"**Soft conflict** — tasks for *different pets* overlap. "
                    f"This may still be manageable.\n\n{msg}",
                    icon="⚠️",
                )
    else:
        st.success("No scheduling conflicts — all tasks fit neatly into the day.", icon="✅")

    # ── Capacity check ────────────────────────────────────────────────────────
    daily_mins = scheduler.total_daily_minutes()
    available_mins = owner.time_available_per_day * 60
    if scheduler.fits_in_schedule():
        st.success(
            f"Daily load: **{daily_mins} min** of {available_mins:.0f} min available "
            f"({available_mins - daily_mins:.0f} min to spare).",
            icon="🕐",
        )
    else:
        st.error(
            f"Over capacity: **{daily_mins} min** needed but only {available_mins:.0f} min available. "
            f"Consider removing or rescheduling some tasks.",
            icon="🔴",
        )

    # ── Sorted schedule table ─────────────────────────────────────────────────
    sorted_tasks = scheduler.sort_by_time()
    pending = [(p, t) for p, t in sorted_tasks if not t.completed]
    done    = [(p, t) for p, t in sorted_tasks if t.completed]

    st.markdown("#### Pending Tasks (chronological)")
    if not pending:
        st.info("All tasks are complete — great job!")
    else:
        for pet, task in pending:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"{priority_icon} **{task.scheduled_time}** &nbsp; [{pet.name}] "
                    f"**{task.name}** — {task.duration_minutes} min "
                    f"*({task.priority} · {task.frequency})*"
                )
            with col_btn:
                if st.button("Done ✓", key=f"done_{pet.name}_{task.name}_{task.scheduled_time}"):
                    next_task = scheduler.complete_task(pet, task)
                    if next_task:
                        st.toast(f"'{task.name}' done! Next occurrence queued.", icon="🔁")
                    else:
                        st.toast(f"'{task.name}' marked complete.", icon="✅")
                    st.rerun()

    if done:
        with st.expander(f"Completed tasks ({len(done)})"):
            st.table([
                {
                    "Time": t.scheduled_time,
                    "Pet": p.name,
                    "Task": t.name,
                    "Duration (min)": t.duration_minutes,
                    "Frequency": t.frequency,
                }
                for p, t in done
            ])
