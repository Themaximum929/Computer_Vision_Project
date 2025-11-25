@echo off
echo === Fixing Git Push ===
echo.

echo Step 1: Check current status
git status
echo.

echo Step 2: Add all files
git add .
echo.

echo Step 3: Commit files
git commit -m "Initial deployment of Key2Poster FLUX"
echo.

echo Step 4: Push to main branch
git push origin main
echo.

echo If push fails, try:
echo   git push origin master
echo.
pause
