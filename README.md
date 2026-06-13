# Gothic Lock Solver

A command-line solver for Gothic-style lock puzzles.

The tool assumes that every lock is new and unknown.

It guides the player through discovering lock dependencies and then calculates the shortest solution automatically.

---

# How It Works

Every lock contains six plates.

Plate numbering:

```text
TOP
 │
 ├─ P1
 ├─ P2
 ├─ P3
 ├─ P4
 ├─ P5
 └─ P6
BOTTOM
```

The goal is to move all plates to position 4.

Position range:

```text
1 = far left
7 = far right
```

Target:

```text
P1 = 4
P2 = 4
P3 = 4
P4 = 4
P5 = 4
P6 = 4
```

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

Example:

```text
P1: 7
P2: 5
P3: 7
P4: 6
P5: 1
P6: 5
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

* Guided lock discovery wizard
* Automatic dependency modeling
* Breadth-First Search (BFS)
* Shortest-path solver
* Invalid move detection
* Profile saving
* JSON export

---

# Installation

Requirements:

* Python 3.10+

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

# Support

If this project helped you:

buymeacoffee.com/paweldev

## License

This project is licensed under the MIT License.

See the LICENSE file for details.
