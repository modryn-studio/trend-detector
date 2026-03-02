@echo off
cd /d C:\Users\Luke\Documents\2026\Feb-26\trend-detector

if not exist logs mkdir logs

call venv\Scripts\activate.bat
python pipeline.py --all >> logs\pipeline_%date:~-4%-%date:~4,2%-%date:~7,2%.log 2>&1
