import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple

APP_NAME = "Gothic Lock Solver"
VERSION = "2.0.0"

PLATES = ["P1", "P2", "P3", "P4", "P5", "P6"]
POSITION_MIN = 1
POSITION_MAX = 7
GOAL = (4, 4, 4, 4, 4, 4)

# A = move right (+1)
# D = move left (-1)
MOVE_DELTA = {
    "A": 1,
    "D": -1,
}

PROFILE_DIR = Path("profiles")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        raw = input(f"{prompt}{suffix} ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes", "t", "tak"):
            return True
        if raw in ("n", "no", "nie"):
            return False
        print("Please answer y or n.")


def slugify(text: str) -> str:
    allowed = []
    for ch in text.strip().lower():
        if ch.isalnum():
            allowed.append(ch)
        elif ch in (" ", "-", "_"):
            allowed.append("_")
    slug = "".join(allowed).strip("_")
    return slug or "lock"


def normalize_plate_name(name: str) -> str:
    return name.strip().upper()


def normalize_dependencies(dep: dict) -> dict:
    """
    Ensures:
    - all plate names are stripped and uppercased,
    - each plate exists in the dict,
    - each plate contains itself with sign +1.
    """
    normalized = {}

    for plate in PLATES:
        normalized[plate] = {plate: 1}

    if not isinstance(dep, dict):
        return normalized

    for plate_key, targets in dep.items():
        plate = normalize_plate_name(str(plate_key))
        if plate not in PLATES:
            continue

        if not isinstance(targets, dict):
            continue

        for target_key, sign in targets.items():
            target = normalize_plate_name(str(target_key))
            if target not in PLATES:
                continue

            try:
                sign_int = int(sign)
            except Exception:
                continue

            if sign_int not in (1, -1):
                continue

            # self-dependency is always +1
            if target == plate:
                normalized[plate][plate] = 1
            else:
                normalized[plate][target] = sign_int

    return normalized


def format_state(state: Tuple[int, ...]) -> str:
    return "(" + ", ".join(str(x) for x in state) + ")"


def state_to_dict(state: Tuple[int, ...]) -> Dict[str, int]:
    return {PLATES[i]: state[i] for i in range(len(PLATES))}


def dict_to_state(d: Dict[str, int]) -> Tuple[int, ...]:
    return tuple(d[p] for p in PLATES)


def print_banner() -> None:
    print(
        f"""
=====================================
       {APP_NAME}
             v{VERSION}
=====================================

This wizard assumes every lock is NEW.

Author: buymeacoffee.com/paweldev
Github: github.com/paweldev/gothic-lock-solver

Position range:
1 = far left
7 = far right

Plate numbering:

P1 = top plate
P2 = second plate
P3 = third plate
P4 = fourth plate
P5 = fifth plate
P6 = bottom plate


Directions:
A = move right (+1)
D = move left (-1)

Dependency input:
R = same direction
L = opposite direction
""".strip()
    )


def ensure_profile_dir() -> None:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def profile_path(lock_name: str) -> Path:
    ensure_profile_dir()
    return PROFILE_DIR / f"{slugify(lock_name)}.json"


def save_profile(lock_name: str, dep: dict) -> None:
    path = profile_path(lock_name)

    if path.exists():
        overwrite = ask_yes_no(
            f"\nProfile '{lock_name}' already exists. Overwrite it?",
            default=False,
        )
        if not overwrite:
            print("Keeping existing profile file. Model is still usable in memory.")
            return

    payload = {
        "lock_name": lock_name,
        "dependencies": dep,
        "goal": list(GOAL),
        "position_min": POSITION_MIN,
        "position_max": POSITION_MAX,
        "move_delta": MOVE_DELTA,
        "version": VERSION,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Profile saved to: {path}")


def print_dependency_help() -> None:
    print(
        """
For each test:
- Move the chosen plate one step in the game
- Enter ONLY the additional plates that moved
- Self movement is added automatically

Input format examples:
  P2=R,P3=R
  P1=L
  P2=R,P6=L

Meaning:
  R = moved in the same direction
  L = moved in the opposite direction

Press ENTER if no other plates moved.
""".strip()
    )


def sign_to_label(sign: int) -> str:
    if sign == 1:
        return "R"
    return "L"


def label_to_sign(raw: str) -> Optional[int]:
    token = raw.strip().upper()

    if token in ("R", "+1", "1", "S", "SAME", "RIGHT"):
        return 1
    if token in ("L", "-1", "O", "OPP", "OPPOSITE", "LEFT"):
        return -1
    return None


def show_dependencies(dep: dict) -> None:
    print("\nCURRENT DEPENDENCIES\n")

    for plate in PLATES:
        print(f"{plate}:")
        for target, sign in dep[plate].items():
            if target == plate:
                print(f"  {target} -> AUTO (same direction)")
            else:
                label = sign_to_label(sign)
                meaning = "same direction" if sign == 1 else "opposite direction"
                print(f"  {target} -> {label} ({meaning})")
        print()


def parse_additional_dependencies(raw: str) -> Tuple[Optional[List[Tuple[str, int]]], Optional[str]]:
    raw = raw.strip()
    if not raw:
        return [], None

    items = [x.strip() for x in raw.split(",") if x.strip()]
    parsed: List[Tuple[str, int]] = []

    for item in items:
        if "=" not in item:
            return None, f"Invalid item: '{item}'. Use formats like P2=R or P3=L."

        target_raw, sign_raw = item.split("=", 1)
        target = normalize_plate_name(target_raw)

        if target not in PLATES:
            return None, f"Invalid plate: '{target_raw}'. Use P1-P6."

        sign = label_to_sign(sign_raw)
        if sign is None:
            return None, f"Invalid direction for {target}. Use R or L."

        parsed.append((target, sign))

    return parsed, None


def discover_dependencies(lock_name: str) -> dict:
    """
    Guided dependency discovery.
    The user tests one plate in game, then enters all additional affected plates.
    Self-dependency is added automatically.
    """
    print("\nSTEP 1/2 - DISCOVER DEPENDENCIES\n")
    print_dependency_help()

    dep = {}

    for plate in PLATES:
        dep[plate] = {plate: 1}

        print("\n" + "-" * 40)
        print(f"Testing {plate}")
        print(f"Move {plate} one step in the game.")
        print("-" * 40)

        while True:
            answer = input("Which OTHER plates moved? ").strip()
            parsed, error = parse_additional_dependencies(answer)

            if error:
                print(error)
                continue

            for target, sign in parsed:
                dep[plate][target] = sign

            break

    dep = normalize_dependencies(dep)
    save_profile(lock_name, dep)
    return dep


def ask_start_state() -> Tuple[int, ...]:
    print("\nSTEP 2/2 - SOLVE LOCK\n")
    print("Enter current plate positions.\n")

    start: List[int] = []
    for plate in PLATES:
        while True:
            raw = input(f"{plate}: ").strip()
            try:
                value = int(raw)
                if POSITION_MIN <= value <= POSITION_MAX:
                    start.append(value)
                    break
            except ValueError:
                pass
            print("Range must be 1..7")

    return tuple(start)


def simulate(
    state: Tuple[int, ...],
    plate: str,
    direction: str,
    dep: dict,
) -> Tuple[Optional[Tuple[int, ...]], Optional[str]]:
    """
    Simulates a single move.
    Returns:
        (new_state, None) on success
        (None, blocker_plate) if blocked
    """
    delta = MOVE_DELTA[direction]
    affected = dep[plate]

    # Check blocks first
    for target, sign in affected.items():
        idx = int(target[1]) - 1
        new_pos = state[idx] + (delta * sign)
        if new_pos < POSITION_MIN or new_pos > POSITION_MAX:
            return None, target

    # Apply move
    new_state = list(state)
    for target, sign in affected.items():
        idx = int(target[1]) - 1
        new_state[idx] += (delta * sign)

    return tuple(new_state), None


def bfs(start: Tuple[int, ...], dep: dict):
    """
    Breadth-First Search for the shortest path from start to GOAL.
    Returns:
        (solution_path, visited_count)
    """
    queue = deque([start])
    visited = {start}
    parent = {}
    move_used = {}

    while queue:
        state = queue.popleft()

        if state == GOAL:
            path = []
            cur = state
            while cur != start:
                path.append(move_used[cur])
                cur = parent[cur]
            path.reverse()
            return path, len(visited)

        for plate in PLATES:
            for direction in ("A", "D"):
                nxt, blocker = simulate(state, plate, direction, dep)
                if nxt is None:
                    continue
                if nxt in visited:
                    continue

                visited.add(nxt)
                parent[nxt] = state
                move_used[nxt] = f"{plate}+{direction}"
                queue.append(nxt)

    return None, len(visited)


def show_solution(start: Tuple[int, ...], solution: List[str], dep: dict) -> None:
    """
    Prints the move sequence and the resulting states after each move.
    """
    state = start
    print("\nSOLUTION\n")

    for i, move in enumerate(solution, 1):
        plate, direction = move.split("+", 1)
        state, blocker = simulate(state, plate, direction, dep)
        print(f"{i:02d}. {move}")
        print(f"    -> {format_state(state)}")

    print(f"\nNumber of moves: {len(solution)}")


def solve_lock_wizard(lock_name: str, dep: dict) -> None:
    start = ask_start_state()

    print("\nStarting state:")
    print(format_state(start))
    print("Target state:")
    print(format_state(GOAL))

    print("\nSolving...\n")
    solution, visited_count = bfs(start, dep)

    print(f"Visited states: {visited_count}")

    if solution is None:
        print("No solution found.")
        print("Tip: check whether the dependency model is correct.")
        return

    show_solution(start, solution, dep)

    save_choice = ask_yes_no("\nSave this lock profile for later?", default=True)
    if save_choice:
        save_profile(lock_name, dep)


def run_wizard() -> None:
    while True:
        print_banner()
        input("\nPress ENTER to start...")

        lock_name = input("\nEnter lock name: ").strip() or "new_lock"
        dep = discover_dependencies(lock_name)

        print("\nDependency discovery completed.")
        show_dependencies(dep)

        solve_lock_wizard(lock_name, dep)

        another = ask_yes_no("\nSolve another NEW lock?", default=False)
        if not another:
            break


def main():
    run_wizard()
    print("\nDone.")


if __name__ == "__main__":
    main()