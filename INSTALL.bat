@echo off
echo Creating virtual environment...
python -m hamsterbot venv
echo Activating virtual environment...
call hamsterbot\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt
echo Please edit the .env file to add your API_ID and API_HASH.
pause
