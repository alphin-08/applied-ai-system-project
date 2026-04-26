"""
Gemini API layer for the PawPal+ RAG pipeline.

generate_care_advice() is the single public function.
It receives the pet profile, today's scheduled plan, any detected conflicts,
and the retrieved care guidelines, then calls Gemini to produce a short
personalised care summary.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from pawpal_system import CareTask, Pet

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    system_instruction=(
        "You are a knowledgeable and caring pet care advisor. "
        "You will be given evidence-based care guidelines retrieved specifically "
        "for the pet described, followed by their schedule for today. "
        "Write a short, personalised care summary that is grounded in the "
        "provided guidelines. Do not give generic advice that ignores the "
        "retrieved guidelines or the schedule."
    ),
)


def _build_schedule_summary(
    pet: Pet,
    plan: list[tuple[Pet, CareTask]],
    conflicts: list[tuple[CareTask, CareTask]],
) -> str:
    """Format today's schedule as plain text for the Gemini prompt."""
    if not plan:
        return f"No tasks scheduled for {pet.name} today."

    lines = [
        f"Today's schedule for {pet.name} "
        f"({pet.age}yr {pet.species}) — {len(plan)} task(s):"
    ]

    for i, (_, task) in enumerate(plan, 1):
        lines.append(
            f"  {i}. [{task.priority.upper()}] {task.title} ({task.task_type})"
            f" — {task.scheduled_time.strftime('%H:%M')}–{task.end_time().strftime('%H:%M')}"
            f" ({task.duration_minutes} min)"
        )

    if conflicts:
        lines.append("\n⚠️ Schedule conflicts detected:")
        for a, b in conflicts:
            lines.append(
                f"  • '{a.title}' "
                f"({a.scheduled_time.strftime('%H:%M')}–{a.end_time().strftime('%H:%M')})"
                f" overlaps with '{b.title}' "
                f"({b.scheduled_time.strftime('%H:%M')}–{b.end_time().strftime('%H:%M')})"
            )

    return "\n".join(lines)


def generate_care_advice(
    pet: Pet,
    plan: list[tuple[Pet, CareTask]],
    conflicts: list[tuple[CareTask, CareTask]],
    retrieved_context: str,
) -> str:
    """
    Call Gemini to generate personalised care advice for a pet's daily schedule.

    Parameters
    ----------
    pet               : the Pet whose schedule is being reviewed
    plan              : list of (Pet, CareTask) tuples from Scheduler.plan
    conflicts         : list of conflicting (CareTask, CareTask) pairs
    retrieved_context : formatted guidelines string from retrieve_context()

    Returns a plain-text care summary, or an error message if the API call fails.
    """
    schedule_summary = _build_schedule_summary(pet, plan, conflicts)

    prompt = (
        f"Pet profile:\n"
        f"  Name:         {pet.name}\n"
        f"  Species:      {pet.species}\n"
        f"  Age:          {pet.age} years\n"
        f"  Health notes: {pet.health_notes or 'none'}\n\n"
        f"Retrieved care guidelines:\n{retrieved_context}\n\n"
        f"{schedule_summary}\n\n"
        "Please provide a concise, personalised care summary for today. "
        "Reference the retrieved guidelines directly where relevant. "
        "Flag any schedule conflicts or health-related concerns the owner should act on."
    )

    try:
        response = _model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Could not generate care advice: {e}"
