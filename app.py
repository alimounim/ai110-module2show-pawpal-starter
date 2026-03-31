import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session state init ────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", "jordan@email.com", 2.0)

owner = st.session_state.owner

# ── Owner info ────────────────────────────────────────────────────────────────
st.subheader("Owner")
st.write(f"**{owner.name}** — {owner.email}")

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
    new_pet = Pet(name=pet_name, specie=species, age=age, weight=0.0)
    owner.add_pet(new_pet)
    st.success(f"{pet_name} added!")

# ── Show pets ─────────────────────────────────────────────────────────────────
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

    frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])

    if st.button("Add task"):
        new_task = Task(
            name=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
        )
        selected_pet.add_task(new_task)
        st.success(f'"{task_title}" added to {selected_pet.name}!')

    # Show current tasks for selected pet
    if selected_pet.tasks:
        st.write(f"**{selected_pet.name}'s tasks:**")
        st.table([
            {"task": t.name, "duration (min)": t.duration_minutes, "priority": t.priority, "done": t.completed}
            for t in selected_pet.tasks
        ])
    else:
        st.info(f"No tasks for {selected_pet.name} yet.")

# ── Generate schedule ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not owner.pets or not any(p.tasks for p in owner.pets):
        st.warning("Add at least one pet with a task first.")
    else:
        scheduler = Scheduler(owner)
        pending = scheduler.get_pending_tasks()
        st.write(f"**{len(pending)} pending task(s):**")
        for pet, task in pending:
            st.write(f"- [{pet.name}] **{task.name}** — {task.duration_minutes} min ({task.priority} priority, {task.frequency})")
        fits = scheduler.fits_in_schedule()
        daily_mins = scheduler.total_daily_minutes()
        available_mins = owner.time_available_per_day * 60
        if fits:
            st.success(f"Fits in schedule: {daily_mins} min / {available_mins:.0f} min available.")
        else:
            st.error(f"Over schedule: {daily_mins} min needed, only {available_mins:.0f} min available.")
