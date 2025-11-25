@echo off
echo ========================================
echo CHECKING GIT REPOSITORY SIZE
echo ========================================

echo.
echo [1] Checking what files are staged:
git status --short

echo.
echo [2] Finding largest files in git history:
git rev-list --objects --all | git cat-file --batch-check="%(objecttype) %(objectname) %(objectsize) %(rest)" | findstr "^blob" | sort /R /+33 | more +1 | findstr /R "^blob.*[0-9][0-9][0-9][0-9][0-9][0-9][0-9]"

echo.
echo [3] Checking .git folder size:
dir .git /s | findstr "File(s)"

echo.
echo [4] Files NOT ignored by .gitignore:
git ls-files | findstr /I "\.pth$ \.safetensors$ \.bin$ \.jpg$ \.png$ \.webp$"

echo.
echo ========================================
echo DONE
echo ========================================
pause
