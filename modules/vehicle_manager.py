import json
import os
import re

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vehicles.json")

class VehicleManager:
    def __init__(self, path=DATA_FILE):
        self.path = path
        self.vehicles = self.load()

    def load(self):
        try:
            with open(self.path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.vehicles, f, indent=2)

    def get(self, plate):
        for v in self.vehicles:
            if v["plate"] == plate:
                return v
        return None

    def register(self, plate, vtype, size, is_ev, needs_charging, needs_access, priority):
        plate = plate.strip().upper()
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9 -]{3,11}", plate):
            raise ValueError("Registration number must be 4-12 letters/digits (spaces or '-' allowed)")
        if self.get(plate):
            raise ValueError(f"Vehicle {plate} is already registered")
        if needs_charging and not is_ev:
            raise ValueError("Charging can only be required for an EV")
        vehicle = {"plate": plate, "type": vtype, "size": size, "is_ev": is_ev,
                   "needs_charging": needs_charging, "needs_access": needs_access,
                   "priority": priority, "space": None}
        self.vehicles.append(vehicle)
        self.save()
        return vehicle

    def waiting_vehicles(self):
        return [v for v in self.vehicles if v["space"] is None]

    def set_space(self, plate, space_id):
        vehicle = self.get(plate)
        if vehicle:
            vehicle["space"] = space_id
            self.save()
