# SDC → Veritas Boundary

1. Instruction created
2. Instruction validated (SDC)
3. Instruction hits execution boundary

At that boundary:
Veritas decides if the state change is allowed to become real.

Key point:
Not “is it valid?”
But:
“Is it still admissible at commit time?”
