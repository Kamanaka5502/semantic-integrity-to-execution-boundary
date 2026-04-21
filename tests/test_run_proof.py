import json
import subprocess
import sys

def test_run():
    r = subprocess.run([sys.executable, "run_proof.py"], capture_output=True, text=True)
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "proof" in data

def test_positive():
    r = subprocess.run([sys.executable, "run_proof.py"], capture_output=True, text=True)
    data = json.loads(r.stdout)
    p = data["proof"]["positive"]
    assert p["allowed"] is True
    assert p["outcome"] == "SAFE_COMMIT"
    assert p["replay"]["matches"] is True

def test_negative():
    r = subprocess.run([sys.executable, "run_proof.py"], capture_output=True, text=True)
    data = json.loads(r.stdout)
    n = data["proof"]["negative"]
    assert n["replay"]["matches"] is False
    assert len(n["replay"]["mismatches"]) > 0
