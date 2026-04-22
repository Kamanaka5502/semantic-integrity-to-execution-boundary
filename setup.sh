#!/bin/bash
<<<<<<< HEAD
pip install -r requirements.txt
python run_proof.py
python run_proof.py --stress 5
python -m pytest -q
=======
set -e

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "== Running proof =="
python run_proof.py

echo
echo "== Running deterministic stress =="
python run_proof.py --stress 5

echo
echo "== Running tests =="
python -m pytest -q

echo
echo "Setup complete."
>>>>>>> b875dc8 (Integrate Terry full runtime build into execution boundary repo)
