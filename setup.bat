@echo off
echo Setting up QUT Course Scraper environment...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Create necessary directories
if not exist "data" mkdir data

echo Environment setup complete.
echo To activate the environment, run: call venv\Scripts\activate
echo To run the scraper, run: python main.py
