@echo off
echo Removing large files from git...

REM Remove large font files from git (keep locally)
git rm --cached fonts/cinematic/*.ttf
git rm --cached fonts/cinematic/*.otf

REM Remove product images
git rm --cached data/products/food/*.webp
git rm --cached data/products/food/*.jpg
git rm --cached data/products/food/*.png

REM Remove poster templates
git rm --cached poster_templates/*.jpg

echo.
echo Committing changes...
git add .gitignore
git commit -m "Remove large files from git tracking"

echo.
echo Cleaning up git history...
git gc --prune=now

echo.
echo Done! Now you can push.
pause
