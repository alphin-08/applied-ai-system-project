from datetime import datetime
from pawpal_system import CareTask, Owner, Pet, Scheduler

owner = Owner(name="Jordan", email="jordan@email.com")
mochi = Pet(name="Mochi", species="dog", age=3, health_notes="Allergic to chicken")
luna  = Pet(name="Luna",  species="cat", age=5, health_notes="Needs thyroid meds")
owner.add_pet(mochi)
owner.add_pet(luna)

today = datetime.today()
def t(h, m):
    """Helper: build a datetime for today at hour h, minute m."""
    return today.replace(hour=h, minute=m, second=0, microsecond=0)

# ── Add tasks INTENTIONALLY OUT OF ORDER ──────────────────────────────────────
# (evening walk added before morning walk to prove sorting works)
mochi.add_task(CareTask("Evening walk",      "walk",        45, "medium", t(18, 0), recurrence="daily"))
mochi.add_task(CareTask("Breakfast",         "feeding",     10, "high",   t(7, 30)))
mochi.add_task(CareTask("Morning walk",      "walk",        30, "high",   t(7, 0),  recurrence="daily"))

luna.add_task(CareTask("Lunch feeding",      "feeding",     10, "medium", t(12, 0)))
luna.add_task(CareTask("Vet check-up",       "appointment", 60, "high",   t(14, 0)))
# Thyroid medication at 07:10 deliberately overlaps Morning walk (07:00-07:30)
luna.add_task(CareTask("Thyroid medication", "medication",   5, "high",   t(7, 10)))

scheduler = Scheduler(owner=owner)

# ── 1. SORT BY TIME ───────────────────────────────────────────────────────────
print("=" * 60)
print("  1. SORT BY TIME  (tasks were added out of order above)")
print("=" * 60)
scheduler.build_plan()
for pet, task in scheduler.get_tasks_by_time():
    print(f"  {task.scheduled_time.strftime('%H:%M')}  [{pet.name:5}] {task.title}")
print()

# ── 2. FILTER BY PET ─────────────────────────────────────────────────────────
print("=" * 60)
print("  2. FILTER BY PET  (Luna only)")
print("=" * 60)
scheduler.build_plan(pet_filter="Luna")
print(scheduler.explain_plan())

# ── 3. CONFLICT DETECTION ─────────────────────────────────────────────────────
print("=" * 60)
print("  3. CONFLICT DETECTION  (full plan, two tasks overlap at 07:xx)")
print("=" * 60)
scheduler.build_plan()
print(scheduler.explain_plan())

# ── 4. FILTER BY STATUS (pending only) ────────────────────────────────────────
print("=" * 60)
print("  4. FILTER BY STATUS  (pending only, after completing Morning walk)")
print("=" * 60)
morning_walk = next(t for t in mochi.get_tasks() if t.title == "Morning walk" and t.is_due_today())
mochi.complete_task(morning_walk)          # marks done AND auto-schedules tomorrow

scheduler.build_plan(show_completed=False)
print(scheduler.explain_plan())

# ── 5. RECURRING: auto-created next occurrence ────────────────────────────────
print("=" * 60)
print("  5. RECURRING AUTO-SCHEDULE  (tomorrow's Morning walk was created)")
print("=" * 60)
tomorrow_walks = [
    t for t in mochi.get_tasks()
    if t.title == "Morning walk" and not t.is_due_today()
]
for task in tomorrow_walks:
    print(f"  Auto-scheduled: {task.scheduled_time.strftime('%A %b %d')}  {task}")
print("=" * 60)
