#!/bin/bash
echo "-----------------------initializing environment-----------------------"
python3 -m venv env

echo "-----------------------activating environment-----------------------"
. env/bin/activate

echo "-----------------------installing requirements-----------------------"
pip install -r requirements.txt

echo "-----------------------Running script-----------------------"
python3 bot.py