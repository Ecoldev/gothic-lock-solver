# How Use https://www.youtube.com/watch?v=la2PTIXOTQo

# Gothic Lock Solver

Supports Gothic 1 Remake locks with any number of plates.

A command-line solver for Gothic-style lock puzzles.

The tool assumes that every lock is new and unknown.

It guides the player through discovering lock dependencies and then calculates the shortest solution automatically.

Current Version: v2.1.0

---

# How It Works

Every lock may contain any number of plates.

When creating a new lock profile, the solver asks for the number of plates and automatically creates:

```text
P1 ... Pn
```

Plate numbering:

```text
TOP
 │
 ├─ P1
 ├─ P2
 ├─ P3
 │
 ├─ ...
 │
 └─ Pn
BOTTOM
```

The goal is to move all plates to position 4.

Position range:

```text
1 = far left
7 = far right
```

Every plate must end in position 4.

Example for a 7-plate lock:

```text
P1 = 4
P2 = 4
P3 = 4
P4 = 4
P5 = 4
P6 = 4
P7 = 4
```

---

# Dynamic Plate Support

Starting from version 2.1.0, the solver supports locks with any number of plates.

Examples:

```text
6 plates
P1-P6

7 plates
P1-P7

8 plates
P1-P8

10 plates
P1-P10
```

When starting a new lock, simply enter:

```text
How many plates does this lock have? 7
```

The solver automatically adjusts:

- Dependency discovery
- State generation
- Goal generation
- Solution calculation
- Profile storage

---

# Step 1 - Discover Dependencies

The program asks you to test each plate.

Example:

```text
Testing P1

Move P1 one step in the game.
```

Observe which other plates move.

Input format:

```text
P2=R
```

Meaning:

```text
P2 moved in the SAME direction.
```

Example:

```text
P2=R,P3=L
```

Meaning:

```text
P2 moved in the SAME direction.
P3 moved in the OPPOSITE direction.
```

Direction codes:

```text
R = same direction
L = opposite direction
```

If no other plate moves:

```text
Press ENTER
```

Important:

Each plate always moves itself automatically.

You only enter additional affected plates.

---

# Step 2 - Enter Current Positions

Example for a 7-plate lock:

```text
P1: 7
P2: 5
P3: 7
P4: 6
P5: 1
P6: 5
P7: 3
```

The solver calculates the shortest valid solution.

---

# Example Output

```text
SOLUTION

01. P1+D
02. P1+D
03. P4+A
04. P5+A
05. P6+D

Number of moves: 5
```

Where:

```text
A = move right
D = move left
```

---

# Features

- Guided lock discovery wizard
- Dynamic plate count (P1-Pn)
- Automatic dependency modeling
- Breadth-First Search (BFS)
- Shortest-path solver
- Invalid move detection
- Profile saving
- JSON export
- Support for locks larger than 6 plates
- Support for plate numbers above P9 (P10, P11, P12...)

---

# Installation

Requirements:

- Python 3.10+

Clone the repository:

```bash
git clone https://github.com/paweldev/gothic-lock-solver.git
cd gothic-lock-solver
```

Run:

```bash
python solver.py
```

---

# Build Windows EXE

Install PyInstaller:

```bash
python -m pip install pyinstaller
```

Build executable:

```bash
python -m pyinstaller --onefile --name GothicLockSolver solver.py
```

Output:

```text
dist/GothicLockSolver.exe
```

---

# Example Workflow

```text
How many plates does this lock have? 7

Enter lock name:
Old Camp Warehouse

STEP 1/2 - DISCOVER DEPENDENCIES

Testing P1
Move P1 one step in the game.

Which OTHER plates moved?
P2=R,P4=L

...

STEP 2/2 - SOLVE LOCK

P1: 7
P2: 3
P3: 5
P4: 1
P5: 4
P6: 7
P7: 2

Solving...

SOLUTION

01. P4+A
02. P2+D
03. P1+D
...
```

---

# Known Limitations

The solver uses Breadth-First Search (BFS) to guarantee the shortest solution.

Very large locks may require significantly more memory and processing time because the number of possible states grows exponentially.

Examples:

```text
6 plates = 117,649 states
7 plates = 823,543 states
8 plates = 5,764,801 states
```

---

# Support

If this project helped you:

https://buymeacoffee.com/paweldev

---

## License

This project is licensed under the MIT License.

See the LICENSE file for details.