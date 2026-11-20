"""CSP step: remove parking spaces that violate HARD constraints. Pure Python, no Tkinter.
Variable = the vehicle's parking space. Domain = all spaces. Soft preferences live in scoring.py.
If the CSP finds nothing, relaxation.py relaxes the RELAXABLE constraints (charging, accessibility)."""
from algorithms.scoring import SIZE_RANK

HARD_CONSTRAINTS = [
    "Space must not be occupied or unavailable",
    "Vehicle size must fit the space",
    "If charging is required, space must have EV charging",
    "Reserved spaces only for the vehicle they are reserved for",
    "If accessibility is required, space must be accessible",
]
# Only these may be relaxed by the fallback. Availability, size and reservations never are.
RELAXABLE_KEYS = ("charging", "access")


def get_violations_detailed(vehicle, space):
    """Return [(constraint_key, reason)] for every hard constraint this space breaks."""
    found = []
    if space["unavailable"]:
        found.append(("unavailable", "Marked unavailable"))
    if space["occupied"]:
        found.append(("occupied", f"Occupied by {space['vehicle']}"))
    if SIZE_RANK[vehicle["size"]] > SIZE_RANK[space["size"]]:
        found.append(("size", f"Too small ({vehicle['size']} vehicle, {space['size']} space)"))
    if vehicle["needs_charging"] and not space["ev"]:
        found.append(("charging", "No EV charging (charging required)"))
    if space["reserved"] and space["reserved_for"] != vehicle["plate"]:
        found.append(("reserved", f"Reserved for {space['reserved_for']}"))
    if vehicle["needs_access"] and not space["accessible"]:
        found.append(("access", "Not accessible (accessibility required)"))
    return found


def get_violations(vehicle, space):
    """Reasons only (empty list = feasible)."""
    return [reason for _, reason in get_violations_detailed(vehicle, space)]


def satisfied_constraints(vehicle, space):
    """Hard constraints this space satisfies (violated ones are left out)."""
    broken = {key for key, _ in get_violations_detailed(vehicle, space)}
    lines = []
    if not broken & {"unavailable", "occupied"}:
        lines.append("Space is free and in service")
    if "size" not in broken:
        lines.append(f"{vehicle['size']} vehicle fits {space['size']} space")
    if "charging" not in broken:
        lines.append("EV charging provided" if vehicle["needs_charging"] else "EV charging not required")
    if "reserved" not in broken:
        lines.append("Reserved for this vehicle" if space["reserved"] else "Reservation rule respected")
    if "access" not in broken:
        lines.append("Accessible space provided" if vehicle["needs_access"] else "Accessibility not required")
    return lines


def run_csp(vehicle, spaces):
    """Check every space. Returns {'checked': n, 'valid': [spaces], 'rejected': [(id, reasons)]}."""
    valid, rejected = [], []
    for space in spaces:
        reasons = get_violations(vehicle, space)
        if reasons:
            rejected.append((space["id"], reasons))
        else:
            valid.append(space)
    return {"checked": len(spaces), "valid": valid, "rejected": rejected}


def diagnose(vehicle, spaces):
    """Explain a CSP failure: how many free, unreserved spaces meet each requirement ON ITS OWN."""
    free = [s for s in spaces if not any(k in ("unavailable", "occupied", "reserved")
                                         for k, _ in get_violations_detailed(vehicle, s))]
    def count(key):
        return sum(1 for s in free if key not in [k for k, _ in get_violations_detailed(vehicle, s)])
    rows = [("Free and unreserved spaces", len(free)), (f"...that fit a {vehicle['size']} vehicle", count("size"))]
    if vehicle["needs_charging"]:
        rows.append(("...with EV charging", count("charging")))
    if vehicle["needs_access"]:
        rows.append(("...that are accessible", count("access")))
    return rows
