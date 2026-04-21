#!/bin/bash
pip install -r requirements.txt
python run_proof.py
python run_proof.py --stress 5
python -m pytest -q
