#!/bin/bash
python3 -m venv pyvenv
. pyvenv/bin/activate
pip install -U pip
pip install -Ur src/requirements.txt
