# core/contradiction_tracer.py

import json
import os
from time import time

class ContradictionTracer:
    def __init__(self, memory_path="memory/contradiction_sequences.json"):
        self.log_path = memory_path
        self.sequences = []
        self.load_sequences()

    def trace_contradiction(self, belief_a, belief_b):
        contradiction_id = f"{belief_a.id[:6]}_{belief_b.id[:6]}"
        sequence = {
            "id": contradiction_id,
            "timestamp": time(),
            "belief_a": belief_a.to_dict(),
            "belief_b": belief_b.to_dict(),
            "depth": self.estimate_depth(belief_a, belief_b),
            "severity": self.estimate_severity(belief_a, belief_b),
            "resolved": False
        }

        belief_a.contradict(belief_b.id)
        belief_b.contradict(belief_a.id)

        self.sequences.append(sequence)
        self.save_sequences()

        print(f"⚠️ Contradiction traced: '{belief_a.content}' ⚔ '{belief_b.content}'")

    def estimate_depth(self, b1, b2):
        # Deeper = older + more utility + more confidence
        return (
            (b1.utility + b2.utility) +
            (b1.confidence + b2.confidence)
        ) / 2

    def estimate_severity(self, b1, b2):
        # How strongly they oppose each other, based on confidence gap
        return abs(b1.confidence - b2.confidence)

    def load_sequences(self):
        if not os.path.exists(self.log_path):
            return
        with open(self.log_path, "r") as f:
            self.sequences = json.load(f)

    def save_sequences(self):
        with open(self.log_path, "w") as f:
            json.dump(self.sequences, f, indent=2)
