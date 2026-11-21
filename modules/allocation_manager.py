from algorithms.csp import run_csp, satisfied_constraints, get_violations, diagnose
from algorithms.hill_climbing import hill_climb
from algorithms.relaxation import relaxed_candidates, relaxed_score
from algorithms.scoring import score_space


class AllocationManager:
    def __init__(self, parking, vehicles):
        self.parking = parking
        self.vehicles = vehicles

    def find_space(self, vehicle):
        csp = run_csp(vehicle, self.parking.spaces)
        result = {"checked": csp["checked"], "valid": [s["id"] for s in csp["valid"]], "rejected": csp["rejected"],
                  "best": None, "csp_failed": not csp["valid"], "diagnosis": [], "candidates": [], "relaxed": []}
        if csp["valid"]:
            candidates, scorer = csp["valid"], score_space
        else:
            result["diagnosis"] = diagnose(vehicle, self.parking.spaces)
            candidates, scorer = relaxed_candidates(vehicle, self.parking.spaces), relaxed_score
            if not candidates:
                return result            # even the fallback has nothing to offer
        result["candidates"] = [s["id"] for s in candidates]
        hc = hill_climb(vehicle, candidates, scorer)
        best = hc["best"]
        result.update(best=best["id"], score=hc["score"], breakdown=hc["breakdown"], log=hc["log"],
                      satisfied=satisfied_constraints(vehicle, best), relaxed=get_violations(vehicle, best))
        result["others"] = sorted(((s["id"], scorer(vehicle, s)[0], "; ".join(get_violations(vehicle, s)))
                                   for s in candidates if s is not best), key=lambda item: -item[1])
        result["explanation"] = [f"{name}: {note} ({pts}/{mx})" if mx else f"{name}: {note} ({pts})"
                                 for name, (pts, mx, note) in hc["breakdown"].items()]
        return result

    def assign(self, plate, space_id):
        vehicle = self.vehicles.get(plate)
        if vehicle is None:
            raise ValueError(f"Vehicle {plate} is not registered")
        if vehicle["space"]:
            raise ValueError(f"{plate} is already parked in {vehicle['space']}")
        self.parking.occupy(space_id, plate)
        self.vehicles.set_space(plate, space_id)

    def release(self, space_id):
        plate = self.parking.release(space_id)
        self.vehicles.set_space(plate, None)
