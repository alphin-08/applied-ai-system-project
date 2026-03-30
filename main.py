from datetime import datetime
from pawpal_system import CareTask, Owner, Pet, Scheduler

# ── Setup ──────────────────────────────────────────────────────────────────────

owner = Owner(name="Jordan", email="jordan@email.com")

mochi = Pet(name="Mochi", species="dog", age=3, health_notes="Allergic to chicken")
luna  = Pet(name="Luna",  species="cat", age=5, health_notes="Needs thyroid meds")

owner.add_pet(mochi)
owner.add_pet(luna)

# ── Tasks for Mochi (dog) ──────────────────────────────────────────────────────

mochi.add_task(CareTask(
    title="Morning walk",
    task_type="walk",
    duration_minutes=30,
    priority="high",
    scheduled_time=datetime.today().replace(hour=7, minute=0, second=0, microsecond=0),
))

mochi.add_task(CareTask(
    title="Breakfast feeding",
    task_type="feeding",
    duration_minutes=10,
    priority="high",
    scheduled_time=datetime.today().replace(hour=7, minute=30, second=0, microsecond=0),
))

mochi.add_task(CareTask(
    title="Evening walk",
    task_type="walk",
    duration_minutes=45,
    priority="medium",
    scheduled_time=datetime.today().replace(hour=18, minute=0, second=0, microsecond=0),
))

# ── Tasks for Luna (cat) ───────────────────────────────────────────────────────

luna.add_task(CareTask(
    title="Thyroid medication",
    task_type="medication",
    duration_minutes=5,
    priority="high",
    scheduled_time=datetime.today().replace(hour=8, minute=0, second=0, microsecond=0),
))

luna.add_task(CareTask(
    title="Lunch feeding",
    task_type="feeding",
    duration_minutes=10,
    priority="medium",
    scheduled_time=datetime.today().replace(hour=12, minute=0, second=0, microsecond=0),
))

luna.add_task(CareTask(
    title="Vet check-up",
    task_type="appointment",
    duration_minutes=60,
    priority="high",
    scheduled_time=datetime.today().replace(hour=14, minute=0, second=0, microsecond=0),
))

# ── Build and display the schedule ────────────────────────────────────────────

scheduler = Scheduler(owner=owner)
scheduler.build_plan()

print("=" * 55)
print(f"  PawPal+ — Today's Schedule ({datetime.today().strftime('%A, %b %d %Y')})")
print("=" * 55)
print(scheduler.explain_plan())
print("=" * 55)

# ── Demo: mark one task complete and show next task ───────────────────────────

print("\n-- Marking 'Morning walk' as complete... --\n")
mochi.tasks[0].mark_complete()
scheduler.build_plan()  # rebuild so plan reflects updated status

next_up = scheduler.get_next_task()
if next_up:
    pet, task = next_up
    print(f"Next task: [{pet.name}] {task}")
else:
    print("All tasks complete!")

print()
print(scheduler.explain_plan())
print("=" * 55)
