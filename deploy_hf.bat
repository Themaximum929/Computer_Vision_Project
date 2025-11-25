@echo off
echo === Hugging Face Space Deployment ===
echo.
echo 1. Install Git LFS (if not installed):
echo    Download from: https://git-lfs.github.com/
echo.
echo 2. Login to Hugging Face:
set /p HF_USERNAME="Enter your HF username: "
set /p SPACE_NAME="Enter space name (e.g., key2poster-flux): "
echo.

echo Creating deployment directory...
mkdir hf_space
cd hf_space

echo Initializing git...
git init
git lfs install

echo Adding Hugging Face remote...
git remote add origin https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%

echo Copying files...
copy ..\app_hf.py app.py
copy ..\requirements.txt .
xcopy ..\src src\ /E /I /Y
if exist ..\fonts xcopy ..\fonts fonts\ /E /I /Y

echo Creating README...
echo ---^> README.md
echo title: Key2Poster FLUX>> README.md
echo emoji: 🎨>> README.md
echo colorFrom: blue>> README.md
echo colorTo: purple>> README.md
echo sdk: gradio>> README.md
echo sdk_version: 4.0.0>> README.md
echo app_file: app.py>> README.md
echo pinned: false>> README.md
echo license: mit>> README.md
echo --->> README.md
echo.>> README.md
echo # Key2Poster FLUX>> README.md
echo Generate professional posters from 2-5 keywords using FLUX.1>> README.md

echo.
echo Files ready! Now run:
echo   cd hf_space
echo   git add .
echo   git commit -m "Initial commit"
echo   git push origin main
echo.
pause
