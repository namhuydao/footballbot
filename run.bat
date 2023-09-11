echo "-----------------------initializing environment-----------------------"
if exist env goto :SKIP
python -m venv env

:SKIP
echo "-----------------------activating environment-----------------------"
call "env\Scripts\activate.bat"

echo "-----------------------installing requirements-----------------------"
pip install -r requirements.txt

echo "-----------------------Running script-----------------------"
python bot.py


pause