# Gothic Lock Solver

Video Tutorial:
https://youtu.be/NQkDHOd0v6U

## Overview

Gothic Lock Solver is a command-line tool for solving lock puzzles in Gothic 1 Remake.

The solver supports locks with any number of plates and automatically discovers lock dependencies, calculates the shortest solution using Breadth-First Search (BFS), and can execute the solution directly inside the game.

Current Version: **v2.2.0**

---

## Features

* Supports Gothic 1 Remake locks
* Dynamic plate count (P1-Pn)
* Guided dependency discovery
* Automatic dependency modeling
* Breadth-First Search (BFS) shortest-path solver
* Automatic lock execution inside the game
* Automatic plate navigation
* Keyboard input simulation
* JSON profile storage
* Invalid move detection
* Support for large lock configurations
* Support for plate numbers above P9 (P10, P11, P12...)

---

## How It Works

Every lock contains one or more plates.

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

Position range:

```text
1 = far left
7 = far right
```

The objective is to move every plate to position 4.

Example:

```text
P1 = 4
P2 = 4
P3 = 4
P4 = 4
P5 = 4
```

---

## Dynamic Plate Support

Examples:

```text
5 plates
P1-P5

6 plates
P1-P6

7 plates
P1-P7

10 plates
P1-P10

15 plates
P1-P15
```

The solver automatically adjusts:

* Dependency discovery
* State generation
* Goal generation
* BFS search
* Solution calculation
* Profile storage

---

## Step 1 - Discover Dependencies

The solver guides you through discovering lock behavior.

Example:

```text
Testing P1

Move P1 one step in the game.
```

Observe which additional plates moved.

Input:

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

If no other plates moved:

```text
Press ENTER
```

Note:

Each plate automatically affects itself.

Only additional affected plates should be entered.

---

## Step 2 - Enter Current Positions

Example:

```text
P1: 7
P2: 5
P3: 7
P4: 6
P5: 1
```

The solver calculates the shortest possible solution.

---

## Example Output

```text
SOLUTION

01. P1+A
02. P1+A
03. P2+A
04. P4+D
05. P5+A

Number of moves: 5
```

Legend:

```text
A = move right
D = move left
```

---

## Automatic Execution

Starting with version 2.2.0, the solver can execute solutions directly inside Gothic 1 Remake.

Workflow:

```text
Discover lock
↓
Enter current positions
↓
Calculate shortest solution
↓
Open lock in Gothic
↓
Place cursor on P1
↓
Press ENTER
↓
Automatic execution
```

The executor automatically:

* Navigates between plates
* Selects the correct plate
* Simulates keyboard input
* Executes the full solution

Example:

```text
Number of moves: 45

Execute solution in Gothic automatically? [Y/n]
Y

OPEN THE LOCK IN GOTHIC
SET CURSOR TO P1

Press ENTER when ready...

Starting in 3...
Starting in 2...
Starting in 1...

01. P1+A
02. P1+A
03. P2+A
...
```

---

## Controls

Default controls:

```text
A = move right
D = move left
W = move up
S = move down
```

The executor automatically switches between plates and performs the required actions.

---

## Installation

Requirements:

* Python 3.10+

Install dependencies:

```bash
pip install pydirectinput pygetwindow pywin32
```

Clone repository:

```bash
git clone https://github.com/paweldev/gothic-lock-solver.git
cd gothic-lock-solver
```

Run:

```bash
python solver.py
```

---

## Build Windows EXE

Install PyInstaller:

```bash
python -m pip install pyinstaller
```

Build executable:

```bash
python -m PyInstaller --onefile --console --name GothicLockSolver solver.py
```

Output:

```text
dist/GothicLockSolver.exe
```

---

## Example Workflow

```text
How many plates does this lock have? 5

Enter lock name:
Warehouse Lock

STEP 1/2 - DISCOVER DEPENDENCIES

Testing P1
Move P1 one step in the game.

Which OTHER plates moved?
P2=R,P4=L

...

STEP 2/2 - SOLVE LOCK

P1: 3
P2: 5
P3: 7
P4: 6
P5: 7

Solving...

SOLUTION

01. P1+A
02. P1+A
03. P2+A
...

Execute solution in Gothic automatically? [Y/n]
Y

OPEN THE LOCK IN GOTHIC
SET CURSOR TO P1

Press ENTER when ready...
```

---

## Known Limitations

The solver uses Breadth-First Search (BFS) to guarantee the shortest solution.

The number of states grows exponentially with the number of plates.

Examples:

```text
6 plates = 117,649 states
7 plates = 823,543 states
8 plates = 5,764,801 states
```

Very large locks may require significant memory and processing time.

Automatic execution depends on the game accepting simulated keyboard input.

---

## Support

If this project helped you:

https://buymeacoffee.com/paweldev

---

## License

This project is licensed under the MIT License.

See LICENSE for details.
