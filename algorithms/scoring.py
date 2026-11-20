"""Suitability scoring (soft preferences). Pure Python, no Tkinter. Max score = 100.
Size 30 + EV 20 + Accessibility 20 + Location 20 + Priority 10."""

SIZE_RANK = {"Small": 1, "Medium": 2, "Large": 3}
MAX_DISTANCE = 7  # entrance is at A1 (row 0, col 0); farthest space is D5 (3 + 4)


def closeness_to_entrance(space):
    """1.0 = next to the entrance, 0.0 = farthest away."""
    distance = space["row"] + space["col"]
    return max(0.0, min(1.0, 1 - distance / MAX_DISTANCE))


def score_space(vehicle, space):
    """Return (total_score, breakdown). breakdown = {name: (points, max_points, note)}."""
    b = {}

    # 1. Size suitability: the tighter the fit, the better (no wasted big spaces).
    extra = SIZE_RANK[space["size"]] - SIZE_RANK[vehicle["size"]]
    points = {0: 30, 1: 20}.get(extra, 10)
    b["Size"] = (points, 30, "exact fit" if extra == 0 else f"{extra} size(s) larger than needed")

    # 2. EV charging suitability.
    if vehicle["needs_charging"]:
        if space["ev"]:
            b["EV charging"] = (20, 20, "charging needed and provided")
        else:
            b["EV charging"] = (0, 20, "charging needed but NOT provided (fallback)")
    elif space["ev"]:
        b["EV charging"] = (8, 20, "charger not needed, would waste an EV space")
    else:
        b["EV charging"] = (20, 20, "charger not needed, EV space kept free")

    # 3. Accessibility suitability.
    if vehicle["needs_access"]:
        if space["accessible"]:
            b["Accessibility"] = (20, 20, "accessible space needed and provided")
        else:
            b["Accessibility"] = (0, 20, "accessible space needed but NOT provided (fallback)")
    elif space["accessible"]:
        b["Accessibility"] = (5, 20, "accessibility not needed, would waste accessible space")
    else:
        b["Accessibility"] = (20, 20, "accessible space kept free")

    # 4. Location preference: closer to the entrance is better.
    close = closeness_to_entrance(space)
    b["Location"] = (round(20 * close, 1), 20, f"closeness to entrance {close:.2f}")

    # 5. Priority: high-priority vehicles get close spaces; normal ones leave them free.
    if vehicle["priority"] == "High":
        b["Priority"] = (round(10 * close, 1), 10, "high priority prefers close spaces")
    else:
        b["Priority"] = (round(10 * (1 - close), 1), 10, "normal priority leaves close spaces for others")

    total = round(sum(p for p, _, _ in b.values()), 1)
    return total, b
