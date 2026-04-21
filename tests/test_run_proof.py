import json
import subprocess
import sys


def run_json(*args):
    result = subprocess.run(
        [sys.executable, "run_proof.py", "--quiet", *args],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_run():
    data = run_json()
    assert "proof" in data


def test_positive():
    data = run_json()
    positive = data["proof"]["positive"]
    assert positive["allowed"] is True
    assert positive["outcome"] == "SAFE_COMMIT"
    assert positive["replay"]["matches"] is True


def test_negative():
    data = run_json()
    negative = data["proof"]["negative"]
    assert negative["replay"]["matches"] is False
    assert len(negative["replay"]["mismatches"]) > 0


def test_stress():
    data = run_json("--stress", "5")
    stress = data["stress"]
    assert stress["iterations"] == 5
    assert stress["deterministic"] is True
    assert stress["all_positive_replays_match"] is True
