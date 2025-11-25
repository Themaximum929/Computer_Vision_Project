@echo off
echo ========================================
echo CLEANING GIT HISTORY
echo This will remove large files from ALL commits
echo ========================================
pause

echo.
echo Step 1: Removing large files from history...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch fonts/cinematic/*.ttf fonts/cinematic/*.otf data/products/**/*.* poster_templates/*.jpg models/**/*.pth models/**/*.safetensors data/posters_by_genre/**/*.*" --prune-empty --tag-name-filter cat -- --all

echo.
echo Step 2: Cleaning up...
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo.
echo Step 3: Checking new size...
git count-objects -vH

echo.
echo ========================================
echo DONE! Now force push with:
echo git push origin --force --all
echo ========================================
pause
