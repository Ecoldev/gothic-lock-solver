@echo off

echo =====================================
echo Building Gothic Lock Solver...
echo =====================================

python -m pip install --upgrade pyinstaller

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

python -m PyInstaller ^
--onefile ^
--console ^
--clean ^
--name GothicLockSolver ^
--hidden-import=pydirectinput ^
--hidden-import=pygetwindow ^
--hidden-import=win32gui ^
--hidden-import=win32con ^
solver.py

echo.
echo =====================================
echo Build finished
echo Output:
echo dist\GothicLockSolver.exe
echo =====================================
echo.

pause