from algorithms.scoring import score_space

MAX_RESTARTS = 3


def get_neighbours(current, feasible):
    return [s for s in feasible
            if abs(s["row"] - current["row"]) + abs(s["col"] - current["col"]) == 1]


def hill_climb(vehicle, feasible, score_function=score_space):
    if not feasible:
        return None
    log, visited = [], set()
    best, best_score = None, -1
    restarts = 0

    for start in feasible:
        if start["id"] in visited or restarts >= MAX_RESTARTS:
            continue
        restarts += 1
        current = start
        current_score = score_function(vehicle, current)[0]
        visited.add(current["id"])
        log.append(f"Restart {restarts}: start at {current['id']} (score {current_score})")

        while True:
            better, better_score = None, current_score
            for neighbour in get_neighbours(current, feasible):
                n_score = score_function(vehicle, neighbour)[0]
                log.append(f"  Check neighbour {neighbour['id']}: score {n_score}")
                if n_score > better_score:          # strictly better only
                    better, better_score = neighbour, n_score
            if better is None:
                log.append(f"  No better neighbour -> local optimum at {current['id']} ({current_score})")
                break
            log.append(f"  Move {current['id']} -> {better['id']} ({current_score} -> {better_score})")
            current, current_score = better, better_score
            visited.add(current["id"])

        if current_score > best_score:
            best, best_score = current, current_score

    log.append(f"Selected {best['id']} with score {best_score}")
    total, breakdown = score_function(vehicle, best)
    return {"best": best, "score": total, "breakdown": breakdown, "log": log}
