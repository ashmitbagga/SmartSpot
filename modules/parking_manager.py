#Stores parking spaces and saves them to data/parking_data.json.
import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "parking_data.json")

# (id, size, ev, accessible)
DEFAULT_LAYOUT = [
    ("A1", "Large", 1, 0), ("A2", "Large", 0, 0), ("A3", "Large", 0, 0), ("A4", "Medium", 0, 0), ("A5", "Medium", 1, 0),
    ("B1", "Medium", 0, 0), ("B2", "Medium", 0, 0), ("B3", "Medium", 0, 1), ("B4", "Small", 0, 0), ("B5", "Small", 0, 0),
    ("C1", "Small", 1, 0), ("C2", "Medium", 1, 0), ("C3", "Large", 0, 0), ("C4", "Medium", 0, 1), ("C5", "Large", 0, 0),
    ("D1", "Small", 0, 0), ("D2", "Small", 0, 0), ("D3", "Medium", 0, 0), ("D4", "Large", 1, 0), ("D5", "Small", 0, 1),
]


def make_default_spaces():
    spaces = []
    for space_id, size, ev, accessible in DEFAULT_LAYOUT:
        spaces.append({"id": space_id, "row": ord(space_id[0]) - ord("A"), "col": int(space_id[1]) - 1,
                       "size": size, "ev": bool(ev), "accessible": bool(accessible),
                       "occupied": False, "unavailable": False,
                       "reserved": False, "reserved_for": "", "vehicle": None})
    return spaces


class ParkingManager:
    def __init__(self, path=DATA_FILE):
        self.path = path
        self.spaces = self.load()

    def load(self):
        #Load spaces from JSON; fall back to the default layout if the file is missing/corrupt.
        try:
            with open(self.path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return make_default_spaces()

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.spaces, f, indent=2)

    def get_space(self, space_id):
        for space in self.spaces:
            if space["id"] == space_id:
                return space
        raise ValueError(f"Space {space_id} does not exist")

    def occupy(self, space_id, plate):
        space = self.get_space(space_id)
        if space["unavailable"]:
            raise ValueError(f"{space_id} is unavailable")
        if space["occupied"]:
            raise ValueError(f"{space_id} is already occupied by {space['vehicle']}")
        if space["reserved"] and space["reserved_for"] != plate:
            raise ValueError(f"{space_id} is reserved for {space['reserved_for']}")
        space["occupied"], space["vehicle"] = True, plate
        self.save()

    def release(self, space_id): # frees up space
        space = self.get_space(space_id)
        if not space["occupied"]:
            raise ValueError(f"{space_id} is not occupied")
        plate = space["vehicle"]
        space["occupied"], space["vehicle"] = False, None
        self.save()
        return plate

    def set_unavailable(self, space_id, value):
        space = self.get_space(space_id)
        if value and space["occupied"]:
            raise ValueError(f"{space_id} is occupied; release it first")
        space["unavailable"] = value
        self.save()

    def reserve(self, space_id, plate):
        space = self.get_space(space_id)
        if not plate:
            raise ValueError("Enter the registration number the space is reserved for")
        if space["occupied"]:
            raise ValueError(f"{space_id} is occupied; release it first")
        space["reserved"], space["reserved_for"] = True, plate
        self.save()

    def cancel_reservation(self, space_id):
        space = self.get_space(space_id)
        if not space["reserved"]:
            raise ValueError(f"{space_id} has no reservation")
        space["reserved"], space["reserved_for"] = False, ""
        self.save()

    def get_stats(self):
        total = len(self.spaces)
        occupied = sum(s["occupied"] for s in self.spaces)
        unavailable = sum(s["unavailable"] for s in self.spaces)
        reserved = sum(s["reserved"] for s in self.spaces)
        available = sum(1 for s in self.spaces if not (s["occupied"] or s["unavailable"] or s["reserved"]))
        in_service = total - unavailable
        percent = round(100 * occupied / in_service, 1) if in_service else 0.0
        return {"total": total, "available": available, "occupied": occupied, "reserved": reserved,
                "ev": sum(s["ev"] for s in self.spaces), "unavailable": unavailable, "occupancy": percent}
