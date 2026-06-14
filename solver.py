import json
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import pydirectinput
import pygetwindow as gw
import win32gui
import win32con


pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False

APP_NAME = "Gothic Lock Solver"
VERSION = "2.2.0"

POSITION_MIN = 1
POSITION_MAX = 7
DEFAULT_GOAL_POS = 4

# A = move right (+1)
# D = move left (-1)
MOVE_DELTA = {
    "A": 1,
    "D": -1,
}

PROFILE_DIR = Path("profiles")

# These are initialized at runtime
PLATES: List[str] = []
GOAL: Tuple[int, ...] = ()


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


def ask_int(prompt: str, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if min_value is not None and value < min_value:
                raise ValueError
            if max_value is not None and value > max_value:
                raise ValueError
            return value
        except ValueError:
            range_msg = []
            if min_value is not None:
                range_msg.append(f">= {min_value}")
            if max_value is not None:
                range_msg.append(f"<= {max_value}")
            if range_msg:
                print("Value must be " + " and ".join(range_msg))
            else:
                print("Please enter a valid integer.")


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


def plate_index(plate: str) -> int:
    """
    Converts P1 -> 0, P10 -> 9, etc.
    """
    return int(plate[1:]) - 1


def initialize_lock_configuration() -> None:
    global PLATES, GOAL

    print_banner_header()
    count = ask_int("\nHow many plates does this lock have? ", min_value=1)

    PLATES = [f"P{i}" for i in range(1, count + 1)]
    GOAL = tuple(DEFAULT_GOAL_POS for _ in range(count))


def print_banner_header() -> None:
    print(
        f"""
=====================================
       {APP_NAME}
             v{VERSION}
=====================================

This wizard assumes every lock is NEW.

Author: buymeacoffee.com/paweldev
Github: github.com/paweldev/gothic-lock-solver
""".strip()
    )


def print_banner() -> None:
    print_banner_header()
    print(
        f"""

Position range:
{POSITION_MIN} = far left
{POSITION_MAX} = far right

Plate numbering:
""".rstrip()
    )
    for plate in PLATES:
        if plate == PLATES[0]:
            label = "top plate"
        elif plate == PLATES[-1]:
            label = "bottom plate"
        else:
            label = f"{plate.lower()}"
        print(f"{plate} = {label}")

    print(
        """

Directions:
A = move right (+1)
D = move left (-1)

Dependency input:
R = same direction
L = opposite direction
""".rstrip()
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
        "plates": PLATES,
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
    return "R" if sign == 1 else "L"


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


def normalize_dependencies(dep: dict) -> dict:
    """
    Ensures:
    - all plate names are stripped and uppercased,
    - each plate exists in the dict,
    - each plate contains itself with sign +1.
    """
    normalized = {plate: {plate: 1} for plate in PLATES}

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

            if target == plate:
                normalized[plate][plate] = 1
            else:
                normalized[plate][target] = sign_int

    return normalized


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
            return None, f"Invalid plate: '{target_raw}'. Use P1-P{len(PLATES)}."

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
            print(f"Range must be {POSITION_MIN}..{POSITION_MAX}")

    return tuple(start)


def format_state(state: Tuple[int, ...]) -> str:
    return "(" + ", ".join(str(x) for x in state) + ")"


def state_to_dict(state: Tuple[int, ...]) -> Dict[str, int]:
    return {PLATES[i]: state[i] for i in range(len(PLATES))}


def dict_to_state(d: Dict[str, int]) -> Tuple[int, ...]:
    return tuple(d[p] for p in PLATES)


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
        idx = plate_index(target)
        new_pos = state[idx] + (delta * sign)
        if new_pos < POSITION_MIN or new_pos > POSITION_MAX:
            return None, target

    # Apply move
    new_state = list(state)
    for target, sign in affected.items():
        idx = plate_index(target)
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
                nxt, _ = simulate(state, plate, direction, dep)
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
        state, _ = simulate(state, plate, direction, dep)
        print(f"{i:02d}. {move}")
        print(f"    -> {format_state(state)}")

    print(f"\nNumber of moves: {len(solution)}")

def activate_gothic():
    windows = gw.getWindowsWithTitle("Gothic 1 Remake")

    if not windows:
        print("Nie znaleziono okna Gothic")
        return False

    hwnd = windows[0]._hWnd

    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

    return True

def execute_solution(solution):
    """
    Execute solution directly in Gothic.
    """

    print("\n")
    print("=====================================")
    print("OPEN THE LOCK IN GOTHIC")
    print("SET CURSOR TO P1")
    print("=====================================")

    input("\nPress ENTER when ready...")
    print("\nOpen Gothic window...")

    if not activate_gothic():
        return

    time.sleep(1)

    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)

    print("Resetting lock position...")

    # Reset lock
    pydirectinput.press("r")
    time.sleep(0.5)

    # Zejdź na sam dół
    for _ in range(len(PLATES)):
        pydirectinput.press("s")
        time.sleep(0.15)

    # Wróć na P1
    for _ in range(len(PLATES) - 1):
        pydirectinput.press("w")
        time.sleep(0.15)

    current_position = 1

    print("Starting from P1...")

    for step_no, move in enumerate(solution, start=1):

        plate, action = move.split("+")
        target_position = int(plate[1:])

        while current_position < target_position:
            pydirectinput.press("s")
            current_position += 1
            time.sleep(0.15)

        while current_position > target_position:
            pydirectinput.press("w")
            current_position -= 1
            time.sleep(0.15)

        pydirectinput.press(action.lower())
        time.sleep(0.15)
        print(f"{step_no:02d}. {move}")

    print("\nExecution finished.")


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

    auto_execute = ask_yes_no(
        "\nExecute solution in Gothic automatically?",
        default=True
    )

    if auto_execute:
        execute_solution(solution)

    save_choice = ask_yes_no(
        "\nSave this lock profile for later?",
        default=True
    )

    if save_choice:
        save_profile(lock_name, dep)



def run_wizard() -> None:
    while True:
        initialize_lock_configuration()
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