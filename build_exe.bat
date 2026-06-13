@echo off

echo =====================================
echo Building Gothic Lock Solver...
echo =====================================

python -m pip install --upgrade pyinstaller

python -m PyInstaller ^
--onefile ^
--name GothicLockSolver ^
--clean ^
solver.py

echo.
echo =====================================
echo Build finished
echo =====================================
echo.

pause
