@echo off
echo === Quick Deploy to HF Space ===
echo.

REM Install HF CLI if needed
pip show huggingface_hub >nul 2>&1 || (
    echo Installing HF CLI...
    pip install huggingface_hub[cli]
)

echo.
echo Uploading files...
huggingface-cli upload Themaximum/Poster_Generation app_hf.py app.py --repo-type=space
huggingface-cli upload Themaximum/Poster_Generation requirements.txt . --repo-type=space
huggingface-cli upload Themaximum/Poster_Generation src/ src/ --repo-type=space

echo.
echo ✓ Deployed! Space will rebuild in 2-3 minutes
echo   https://huggingface.co/spaces/Themaximum/Poster_Generation
pause
