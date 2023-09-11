#!/bin/bash
echo "-----------------------initializing environment-----------------------"
if [ ! -d "env" ]; then
  python3 -m venv env
fi

echo "-----------------------activating environment-----------------------"
. env/bin/activate

echo "-----------------------installing requirements-----------------------"
pip install -r requirements.txt

echo "-----------------------Running script-----------------------"
python3 bot.py