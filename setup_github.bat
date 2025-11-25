@echo off
echo === Setup GitHub Repository ===
echo.

set /p GITHUB_USERNAME="Enter your GitHub username: "
set /p REPO_NAME="Enter repository name (e.g., Key2Poster): "

echo.
echo Initializing git...
git init

echo.
echo Adding files...
git add .

echo.
echo Creating first commit...
git commit -m "Initial commit: Key2Poster FLUX project"

echo.
echo Adding GitHub remote...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

echo.
echo Creating main branch...
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ✓ Done! Repository created at:
echo   https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.
echo Share this link with your team:
echo   git clone https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo.
pause
