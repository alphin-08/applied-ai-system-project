import streamlit as st
from datetime import datetime
from pawpal_system import CareTask, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("PawPal+")

# ── Session state initialisation ──────────────────────────────────────────────
# Streamlit reruns the entire script on every interaction. Storing objects in
# st.session_state acts as a persistent "vault" — we only create them once,
# then reuse the same instance on every subsequent rerun.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="jordan@email.com")

if "pets" not in st.session_state:
    st.session_state.pets: dict[str, Pet] = {}   # keyed by pet name for quick lookup

# Convenience alias so the rest of the script reads cleanly
owner: Owner = st.session_state.owner

# ── Sidebar: register an owner & pets ─────────────────────────────────────────
with st.sidebar:
    st.header("Owner & Pets")

    new_owner_name = st.text_input("Owner name", value=owner.name)
    if new_owner_name != owner.name:
        owner.name = new_owner_name

    st.divider()
    st.subheader("Add a pet")
    pet_name  = st.text_input("Pet name",  value="Mochi")
    species   = st.selectbox("Species", ["dog", "cat", "other"])
    age       = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    health    = st.text_input("Health notes", value="")

    if st.button("Register pet"):
        if pet_name and pet_name not in st.session_state.pets:
            new_pet = Pet(name=pet_name, species=species, age=age, health_notes=health)
            owner.add_pet(new_pet)
            st.session_state.pets[pet_name] = new_pet
            st.success(f"{pet_name} registered!")
        elif pet_name in st.session_state.pets:
            st.warning(f"{pet_name} is already registered.")

    if owner.get_pets():
        st.divider()
        st.subheader("Registered pets")
        for pet in owner.get_pets():
            st.markdown(f"- **{pet.name}** ({pet.species}, {pet.age}yr)")

# ── Main area: add tasks ───────────────────────────────────────────────────────
st.subheader("Add a Task")

if not owner.get_pets():
    st.info("Register at least one pet in the sidebar before adding tasks.")
else:
    pet_names = [p.name for p in owner.get_pets()]

    col1, col2 = st.columns(2)
    with col1:
        selected_pet  = st.selectbox("For which pet?", pet_names)
        task_title    = st.text_input("Task title", value="Morning walk")
        task_type     = st.selectbox("Task type", ["walk", "feeding", "medication", "appointment"])
    with col2:
        priority      = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        duration      = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        task_time     = st.time_input("Scheduled time", value=datetime.now().replace(second=0, microsecond=0))

    if st.button("Add task"):
        pet = st.session_state.pets[selected_pet]
        scheduled_dt  = datetime.combine(datetime.today().date(), task_time)
        pet.add_task(CareTask(
            title=task_title,
            task_type=task_type,
            duration_minutes=int(duration),
            priority=priority,
            scheduled_time=scheduled_dt,
        ))
        st.success(f"Task '{task_title}' added to {selected_pet}!")

# ── Current tasks table ────────────────────────────────────────────────────────
st.divider()
st.subheader("Current Tasks")

all_tasks = [
    {
        "Pet":      pet.name,
        "Task":     task.title,
        "Type":     task.task_type,
        "Priority": task.priority,
        "Time":     task.scheduled_time.strftime("%H:%M"),
        "Duration": f"{task.duration_minutes} min",
        "Done":     task.completed,
    }
    for pet in owner.get_pets()
    for task in pet.get_tasks()
]

if all_tasks:
    st.table(all_tasks)
else:
    st.info("No tasks yet. Add one above.")

# ── Generate schedule ──────────────────────────────────────────────────────────
st.divider()
st.subheader("Build Today's Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner)
    scheduler.build_plan()

    if not scheduler.plan:
        st.warning("No tasks are scheduled for today.")
    else:
        st.success("Schedule built!")
        for i, (pet, task) in enumerate(scheduler.plan, start=1):
            status = "Done" if task.completed else "Pending"
            st.markdown(
                f"**{i}. [{task.priority.upper()}] {task.title}** — {pet.name}  \n"
                f"_{task.task_type} | {task.duration_minutes} min "
                f"@ {task.scheduled_time.strftime('%H:%M')} | {status}_"
            )
