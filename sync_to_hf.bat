@echo off
echo === Sync to Hugging Face Space ===

REM Navigate to HF space directory
cd hf_space 2>nul || (
    echo First time setup...
    git clone https://huggingface.co/spaces/Themaximum/Poster_Generation hf_space
    cd hf_space
)

echo.
echo Syncing files...
copy ..\app_hf.py app.py
copy ..\requirements.txt .
xcopy ..\src src\ /E /I /Y /Q

echo.
echo Committing changes...
git add .
git commit -m "Update: %date% %time%"

echo.
echo Pushing to HF...
git push

echo.
echo ✓ Done! Check your space in 2-3 minutes
echo   https://huggingface.co/spaces/Themaximum/Poster_Generation
pause
