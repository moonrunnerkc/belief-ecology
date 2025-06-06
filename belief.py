# core/belief.py
#Author: Bradley R Kinnard

import uuid
import time

class Belief:
    def __init__(self, content, source=None, confidence=0.5, utility=0.5):
        self.id = str(uuid.uuid4())
        self.content = content
        self.source = source or "unknown"
        self.confidence = confidence        # How sure the system is
        self.utility = utility              # How useful this belief has been
        self.recency = 1.0                  # How recently it was accessed (1.0 = now)
        self.entropy = 0.0                  # Increases over time if unused
        self.created = time.time()
        self.last_used = time.time()
        self.status = "active"              # Can be: active, decaying, dormant, mutated, archived
        self.contradictions = []            # List of belief IDs that oppose this one
        self.mutations = []                 # List of beliefs derived from this one

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "confidence": self.confidence,
            "utility": self.utility,
            "recency": self.recency,
            "entropy": self.entropy,
            "created": self.created,
            "last_used": self.last_used,
            "status": self.status,
            "contradictions": self.contradictions,
            "mutations": self.mutations
        }

    def reinforce(self, amount=0.1):
        self.confidence = min(self.confidence + amount, 1.0)
        self.utility = min(self.utility + amount, 1.0)
        self.recency = 1.0
        self.entropy = max(self.entropy - 0.1, 0.0)
        self.last_used = time.time()

    def decay(self):
        self.recency = max(self.recency - 0.1, 0.0)
        self.entropy += 0.05
        if self.entropy >= 1.0:
            self.status = "decaying"

    def contradict(self, other_belief_id):
        if other_belief_id not in self.contradictions:
            self.contradictions.append(other_belief_id)

    def run_mutation_cycle(self):
        pairs = self.detect_mutation_pairs()
        for b1, b2 in pairs:
            self.mutate_belief_pair(b1, b2)

