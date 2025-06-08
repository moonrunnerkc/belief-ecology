# core/belief.py
# Author: Bradley R Kinnard

import uuid
import time
from typing import Optional, List


class Belief:
    def __init__(
        self,
        content: str,
        source: Optional[str] = None,
        confidence: float = 0.5,
        utility: float = 0.5,
        recency: Optional[float] = None,
        entropy: Optional[float] = None,
        created: Optional[float] = None,
        last_used: Optional[float] = None,
        status: Optional[str] = None,
        contradictions: Optional[List[str]] = None,
        mutations: Optional[List[str]] = None,
        id: Optional[str] = None,
        origin: Optional[str] = None  # NEW FIELD
    ):
        self.id = id if id else str(uuid.uuid4())
        self.content = content
        self.source = source or "unknown"
        self.origin = origin or self.source  # Track original source
        self.confidence = confidence
        self.utility = utility
        self.recency = recency if recency is not None else 1.0
        self.entropy = entropy if entropy is not None else 0.0
        self.created = created if created is not None else time.time()
        self.last_used = last_used if last_used is not None else time.time()
        self.status = status or "active"
        self.contradictions = contradictions if contradictions is not None else []
        self.mutations = mutations if mutations is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "origin": self.origin,
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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            content=data["content"],
            source=data.get("source", "unknown"),
            origin=data.get("origin"),  # NEW
            confidence=data.get("confidence", 0.5),
            utility=data.get("utility", 0.5),
            recency=data.get("recency", 1.0),
            entropy=data.get("entropy", 0.0),
            created=data.get("created"),
            last_used=data.get("last_used"),
            status=data.get("status", "active"),
            contradictions=data.get("contradictions", []),
            mutations=data.get("mutations", []),
            id=data.get("id")
        )

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

    def detect_mutation_pairs(self):
        return []

    def mutate_belief_pair(self, b1, b2):
        pass
