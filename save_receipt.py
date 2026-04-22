import json
from datetime import datetime

def save_receipt(receipt):
    filename = f"receipt_{datetime.now().timestamp()}.json"
    with open(filename, "w") as f:
        json.dump(receipt, f, indent=2)
    print(f"Saved receipt: {filename}")
