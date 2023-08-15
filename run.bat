echo "-----------------------initializing environment-----------------------"
python -m venv env

echo "-----------------------activating environment-----------------------"
call "env\Scripts\activate.bat"

echo "-----------------------installing requirements-----------------------"
pip install -r requirements.txt

echo "-----------------------Running script-----------------------"
python bot.py


pause