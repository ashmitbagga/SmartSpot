"""Fallback when the CSP fails: relax charging/accessibility into penalised preferences.
Size, availability and reservations are NEVER relaxed. Hill Climbing then runs with this scorer."""
from algorithms.csp import get_violations_detailed, RELAXABLE_KEYS
from algorithms.scoring import score_space

PENALTY = 30  # points lost for each relaxed constraint


def relaxed_candidates(vehicle, spaces):
    """Spaces that break only relaxable constraints."""
    return [s for s in spaces
            if all(key in RELAXABLE_KEYS for key, _ in get_violations_detailed(vehicle, s))]


def relaxed_score(vehicle, space):
    """Normal suitability score minus PENALTY for every relaxed (violated) constraint."""
    total, breakdown = score_space(vehicle, space)
    count = sum(1 for key, _ in get_violations_detailed(vehicle, space) if key in RELAXABLE_KEYS)
    if count:
        breakdown["Relaxed constraints"] = (-PENALTY * count, 0, f"{count} requirement(s) not met")
    return round(max(0, total - PENALTY * count), 1), breakdown
