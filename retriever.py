"""
Retriever for the PawPal+ RAG pipeline.

retrieve_context(pet, task_types) is the single public function.
It looks up the knowledge base using the pet's profile and today's task
types, then returns a formatted string of relevant guidelines ready to
be injected into the Claude prompt as context.
"""

from pawpal_system import Pet
from pet_care_kb import (
    AGE_GUIDELINES,
    HEALTH_GUIDELINES,
    SPECIES_GUIDELINES,
    TASK_GUIDELINES,
    age_bracket,
)


def retrieve_context(pet: Pet, task_types: list[str]) -> str:
    """
    Return relevant care guidelines for a pet given today's task types.

    Lookup order:
      1. Species      — always included
      2. Age bracket  — always included
      3. Task types   — one entry per unique task type in today's schedule
      4. Health notes — scanned for keyword matches against HEALTH_GUIDELINES

    Each section is labelled so Claude can distinguish guideline sources.
    """
    sections: list[str] = []

    # 1. Species
    species_key = pet.species.lower()
    if species_key not in SPECIES_GUIDELINES:
        species_key = "other"
    sections.append(
        f"[Species — {pet.species}]\n{SPECIES_GUIDELINES[species_key]}"
    )

    # 2. Age bracket
    bracket = age_bracket(pet.species.lower(), pet.age)
    sections.append(
        f"[Age — {bracket} ({pet.age} yr)]\n{AGE_GUIDELINES[bracket]}"
    )

    # 3. Task types (deduplicated, only known types included)
    seen: set[str] = set()
    for task_type in task_types:
        key = task_type.lower()
        if key in TASK_GUIDELINES and key not in seen:
            sections.append(f"[Task — {task_type}]\n{TASK_GUIDELINES[key]}")
            seen.add(key)

    # 4. Health notes — scan for keyword matches
    if pet.health_notes:
        notes_lower = pet.health_notes.lower()
        for keyword, guideline in HEALTH_GUIDELINES.items():
            if keyword in notes_lower:
                sections.append(f"[Health — {keyword}]\n{guideline}")

    return "\n\n".join(sections)
