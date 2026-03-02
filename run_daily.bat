@echo off
cd /d C:\Users\Luke\Documents\2026\Feb-26\trend-detector

if not exist logs mkdir logs

call venv\Scripts\activate.bat

:: Use Python for an ISO date — %date% parsing is Windows locale-dependent
for /f %%d in ('python -c "import datetime; print(datetime.date.today())"') do set TODAY=%%d

python pipeline.py --all >> logs\pipeline_%TODAY%.log 2>&1
if %errorlevel% neq 0 (
    echo [run_daily] pipeline.py exited with error %errorlevel% >> logs\pipeline_%TODAY%.log
)
