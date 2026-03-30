import streamlit as st
from datetime import datetime
from pawpal_system import CareTask, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("PawPal+")
st.caption("Smart pet care scheduling — powered by priority, conflict detection, and recurring tasks.")

# ── Session state ──────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="jordan@email.com")
if "pets" not in st.session_state:
    st.session_state.pets: dict[str, Pet] = {}

owner: Owner = st.session_state.owner

# ── Sidebar: owner profile + register pets ────────────────────────────────────
with st.sidebar:
    st.header("Owner & Pets")

    new_name = st.text_input("Owner name", value=owner.name)
    if new_name != owner.name:
        owner.name = new_name

    st.divider()
    st.subheader("Register a pet")
    pet_name = st.text_input("Pet name", value="Mochi")
    species  = st.selectbox("Species", ["dog", "cat", "other"])
    age      = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    health   = st.text_input("Health notes", value="")

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
        st.subheader("Your pets")
        for pet in owner.get_pets():
            note = f" — _{pet.health_notes}_" if pet.health_notes else ""
            st.markdown(f"- **{pet.name}** ({pet.species}, {pet.age}yr){note}")

# ── Main layout: two columns ───────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

# ── Left: Add a task ──────────────────────────────────────────────────────────
with left:
    st.subheader("Add a Task")

    if not owner.get_pets():
        st.info("Register at least one pet in the sidebar first.")
    else:
        pet_names    = [p.name for p in owner.get_pets()]
        selected_pet = st.selectbox("For which pet?", pet_names)
        task_title   = st.text_input("Task title", value="Morning walk")
        task_type    = st.selectbox("Task type", ["walk", "feeding", "medication", "appointment"])
        priority     = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        duration     = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        task_time    = st.time_input("Scheduled time", value=datetime.now().replace(second=0, microsecond=0))
        recurrence   = st.selectbox("Recurrence", ["none", "daily", "weekly"])

        if st.button("Add task", use_container_width=True):
            pet = st.session_state.pets[selected_pet]
            scheduled_dt = datetime.combine(datetime.today().date(), task_time)
            pet.add_task(CareTask(
                title=task_title,
                task_type=task_type,
                duration_minutes=int(duration),
                priority=priority,
                scheduled_time=scheduled_dt,
                recurrence=recurrence,
            ))
            st.success(f"'{task_title}' added to {selected_pet}!")

# ── Right: Schedule builder ───────────────────────────────────────────────────
with right:
    st.subheader("Today's Schedule")

    pet_names_all = ["All pets"] + [p.name for p in owner.get_pets()]
    filter_pet    = st.selectbox("Filter by pet", pet_names_all, key="filter_pet")
    hide_done     = st.checkbox("Hide completed tasks", value=False)
    sort_mode     = st.radio("Sort by", ["Priority (smart)", "Time (chronological)"], horizontal=True)

    if st.button("Build schedule", use_container_width=True):
        scheduler = Scheduler(owner=owner)
        pet_filter = None if filter_pet == "All pets" else filter_pet
        scheduler.build_plan(pet_filter=pet_filter, show_completed=not hide_done)
        st.session_state.last_plan      = scheduler.plan
        st.session_state.last_conflicts = scheduler.conflicts
        st.session_state.last_scheduler = scheduler

    # ── Render plan from session state so it survives reruns ──────────────────
    if "last_plan" in st.session_state and st.session_state.last_plan is not None:
        scheduler = st.session_state.last_scheduler

        # Re-run build so completion status is always fresh
        pet_filter = None if filter_pet == "All pets" else filter_pet
        scheduler.build_plan(pet_filter=pet_filter, show_completed=not hide_done)
        st.session_state.last_plan      = scheduler.plan
        st.session_state.last_conflicts = scheduler.conflicts

        if not scheduler.plan:
            st.info("No tasks scheduled for today with the current filters.")
        else:
            # ── Conflict warnings ──────────────────────────────────────────────
            if scheduler.conflicts:
                for task_a, task_b in scheduler.conflicts:
                    st.warning(
                        f"**Schedule conflict:** '{task_a.title}' "
                        f"({task_a.scheduled_time.strftime('%H:%M')}–{task_a.end_time().strftime('%H:%M')}) "
                        f"overlaps with '{task_b.title}' "
                        f"({task_b.scheduled_time.strftime('%H:%M')}–{task_b.end_time().strftime('%H:%M')}). "
                        f"Consider rescheduling one of these tasks."
                    )
            else:
                st.success(f"{len(scheduler.plan)} task(s) scheduled — no conflicts detected.")

            # ── Choose sort order ──────────────────────────────────────────────
            ordered = (
                scheduler.get_tasks_by_time()
                if sort_mode == "Time (chronological)"
                else scheduler.plan
            )

            badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}

            for i, (pet, task) in enumerate(ordered, start=1):
                status_icon = "✅" if task.completed else "⬜"
                recur_label = f" ({task.recurrence})" if task.recurrence != "none" else ""

                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(
                            f"{status_icon} **{i}. {task.title}**{recur_label}  \n"
                            f"{badge[task.priority]} `{task.priority.upper()}` &nbsp;|&nbsp; "
                            f"**{pet.name}** &nbsp;|&nbsp; "
                            f"{task.task_type} &nbsp;|&nbsp; "
                            f"{task.scheduled_time.strftime('%H:%M')}–{task.end_time().strftime('%H:%M')} "
                            f"({task.duration_minutes} min)"
                        )
                    with col_b:
                        if not task.completed:
                            if st.button("Mark done", key=f"done_{i}_{task.title}"):
                                for p in owner.get_pets():
                                    if task in p.get_tasks():
                                        p.complete_task(task)
                                        break
                                st.rerun()
