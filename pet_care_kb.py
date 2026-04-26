"""
Pet care knowledge base for PawPal+ RAG pipeline.

Organised into four lookup tables:
  SPECIES_GUIDELINES  — care rules by species
  AGE_GUIDELINES      — care rules by age bracket (young / adult / senior)
  TASK_GUIDELINES     — best-practice tips by task type
  HEALTH_GUIDELINES   — warnings/adjustments keyed to health-note keywords

The retriever reads these dicts and returns only the entries that match
the current pet's profile and today's task types.
"""

# ── Age bracket helper ─────────────────────────────────────────────────────────

def age_bracket(species: str, age: int) -> str:
    """Return 'young', 'adult', or 'senior' based on species-appropriate thresholds."""
    if species == "cat":
        if age <= 2:
            return "young"
        elif age <= 10:
            return "adult"
        else:
            return "senior"
    else:  # dog and other use the same thresholds
        if age <= 2:
            return "young"
        elif age <= 7:
            return "adult"
        else:
            return "senior"


# ── Species guidelines ─────────────────────────────────────────────────────────

SPECIES_GUIDELINES: dict[str, str] = {
    "dog": (
        "Dogs are social animals that thrive on routine. "
        "Aim for at least two walks per day and consistent feeding times. "
        "Dogs can overheat quickly in warm weather — keep outdoor sessions short mid-day."
    ),
    "cat": (
        "Cats prefer predictable schedules but are more independent than dogs. "
        "Ensure fresh water is always available; cats are prone to under-drinking. "
        "Indoor cats need environmental enrichment — interactive play counts as exercise."
    ),
    "other": (
        "Care requirements vary widely for non-dog/cat pets. "
        "Consult species-specific guidelines and maintain a consistent daily routine. "
        "Monitor for stress signals such as changes in appetite or activity level."
    ),
}


# ── Age guidelines ─────────────────────────────────────────────────────────────

AGE_GUIDELINES: dict[str, str] = {
    "young": (
        "Young pets have high energy but developing joints and immune systems. "
        "Keep individual exercise sessions shorter and more frequent rather than one long session. "
        "Vaccinations and parasite prevention are especially important at this stage."
    ),
    "adult": (
        "Adult pets are at peak health and can handle a full exercise and feeding routine. "
        "Annual vet check-ups are sufficient for most healthy adults. "
        "Watch for gradual weight changes — adults can become sedentary without noticing."
    ),
    "senior": (
        "Senior pets tire more easily and may have joint stiffness or reduced appetite. "
        "Shorten walk durations and avoid high-impact activities. "
        "Increase vet visit frequency to twice per year; monitor for lumps, dental issues, and vision changes."
    ),
}


# ── Task-type guidelines ───────────────────────────────────────────────────────

TASK_GUIDELINES: dict[str, str] = {
    "walk": (
        "Walk at a pace comfortable for the pet, not the owner. "
        "Avoid hot pavement — if it is too hot to hold your hand on the ground for 5 seconds, it is too hot for paws. "
        "Allow sniffing time; mental stimulation during walks reduces anxiety."
    ),
    "feeding": (
        "Feed at the same times each day to regulate digestion and reduce begging behaviour. "
        "Measure portions — free-feeding leads to obesity in most breeds. "
        "Wait at least 30 minutes after a meal before strenuous exercise to reduce bloat risk."
    ),
    "medication": (
        "Administer medication at the same time each day to maintain consistent blood levels. "
        "Many medications should be given with food to reduce stomach upset — check the label. "
        "Never skip a dose without consulting a vet; missed doses can reduce treatment effectiveness."
    ),
    "appointment": (
        "Bring a written list of any behavioural or physical changes noticed since the last visit. "
        "Keep the pet calm before appointments — avoid vigorous exercise in the hour prior. "
        "Bring previous medical records if visiting a new clinic."
    ),
}


# ── Health-condition guidelines ────────────────────────────────────────────────
# Keys are lowercase keywords that might appear in a pet's health_notes field.

HEALTH_GUIDELINES: dict[str, str] = {
    "joint": (
        "Joint issues require low-impact exercise — swimming or short flat walks are preferred. "
        "Avoid stairs, jumping, and rough terrain. "
        "Ask your vet about joint supplements such as glucosamine."
    ),
    "arthritis": (
        "Pets with arthritis benefit from gentle, consistent movement rather than rest. "
        "Warm up slowly at the start of a walk and stop if the pet shows limping. "
        "Keep sleeping areas warm and elevated off cold floors."
    ),
    "diabetes": (
        "Diabetic pets must eat and exercise on a strict, consistent schedule. "
        "Feed immediately before or after insulin injection as directed by your vet. "
        "Watch for signs of hypoglycaemia: weakness, trembling, or collapse."
    ),
    "kidney": (
        "Kidney disease requires increased water intake — consider a water fountain to encourage drinking. "
        "Feed a vet-prescribed low-phosphorus diet and avoid high-protein treats. "
        "Monitor urination frequency and report sudden changes to your vet."
    ),
    "heart": (
        "Cardiac pets should avoid over-exertion — stop exercise at the first sign of coughing or laboured breathing. "
        "Keep walks short and at a slow, steady pace. "
        "Weigh the pet weekly; sudden weight gain can indicate fluid retention."
    ),
    "overweight": (
        "Overweight pets need calorie-controlled meals — measure every portion. "
        "Increase exercise gradually; start with an extra 5 minutes per walk each week. "
        "Avoid high-calorie treats; use small pieces of plain vegetables instead."
    ),
    "anxiety": (
        "Anxious pets benefit from predictable, low-stimulation routines. "
        "Avoid sudden schedule changes and loud environments during walks. "
        "Consider calming aids (thunder shirts, pheromone diffusers) for high-stress tasks like vet appointments."
    ),
    "allergy": (
        "Pets with allergies may react to grass, pollen, or certain proteins — note patterns. "
        "Wipe paws and coat after outdoor walks to remove allergens. "
        "Report persistent scratching, ear infections, or red skin to your vet."
    ),
}
