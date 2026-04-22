import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.adapter import from_sdc
from app.admissibility import evaluate_attempt
from app.commit_gate import enforce
from app.receipt import create_receipt, create_proof_receipt
from app.replay import replay


HOST = "0.0.0.0"
PORT = 8001


def build_runtime_response(payload):
    attempt = from_sdc(payload)
    result = evaluate_attempt(attempt)
    commit_result = enforce(result.decision)
    runtime_receipt = create_receipt(attempt, result)
    replay_result = replay(attempt)

    return {
        "attempt": {
            "corridor": attempt.corridor,
            "action": attempt.action,
            "user": attempt.user,
            "authority_level": attempt.authority_level,
            "prior_state": attempt.prior_state,
            "payload": attempt.payload,
        },
        "evaluation": {
            "decision": result.decision.value,
            "reason": result.reason,
            "checks": result.checks,
        },
        "commit_result": commit_result,
        "runtime_receipt": runtime_receipt.to_dict(),
        "replay": {
            "decision": replay_result.decision.value,
            "reason": replay_result.reason,
            "checks": replay_result.checks,
        },
    }


def build_proof_response(payload):
    attempt = from_sdc(payload)
    result = evaluate_attempt(attempt)
    commit_result = enforce(result.decision)

    proof_receipt = create_proof_receipt(attempt, result)
    replay_result = replay(attempt)
    replay_proof_receipt = create_proof_receipt(attempt, replay_result)

    return {
        "attempt": {
            "corridor": attempt.corridor,
            "action": attempt.action,
            "user": attempt.user,
            "authority_level": attempt.authority_level,
            "prior_state": attempt.prior_state,
            "payload": attempt.payload,
        },
        "evaluation": {
            "decision": result.decision.value,
            "reason": result.reason,
            "checks": result.checks,
        },
        "commit_result": commit_result,
        "proof_receipt": proof_receipt.to_dict(),
        "replay": {
            "decision": replay_result.decision.value,
            "reason": replay_result.reason,
            "checks": replay_result.checks,
        },
        "proof_replay_equivalent": (
            proof_receipt.receipt_id == replay_proof_receipt.receipt_id
        ),
    }


class VeritasHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {
                "status": "ok",
                "service": "veritas-cordovaos-stdlib-api",
                "version": "0.1.0"
            })
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            payload = json.loads(raw.decode("utf-8")) if raw else {}

            if self.path == "/evaluate":
                self._send_json(200, build_runtime_response(payload))
                return

            if self.path == "/evaluate/proof":
                self._send_json(200, build_proof_response(payload))
                return

            self._send_json(404, {"error": "Not found"})
        except Exception as e:
            self._send_json(400, {"error": str(e)})


def main():
    server = HTTPServer((HOST, PORT), VeritasHandler)
    print(f"Veritas stdlib API running on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
