# core/contradiction_tracer.py
# Author: Bradley R Kinnard

import uuid
import json
import os
from datetime import datetime
from typing import List, Tuple, Optional, TYPE_CHECKING
from core.belief import Belief

if TYPE_CHECKING:
    from core.belief_ecology import BeliefEcology

CONTRADICTION_LOG_PATH = "memory/contradiction_sequences.json"


class ContradictionTracer:
    """
    Contradiction tracer for RCTS (Recursive Contradiction Tracing System).
    Tracks, logs, and stores contradiction chains and conflict metadata.
    Also enables live contradiction graph population for visualization.
    """

    def __init__(self):
        self.history = []  # Deep contradiction logs
        self.traced_pairs: List[Tuple[str, str]] = []  # Shallow (id_a, id_b) tuples for graph edge rendering
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not os.path.exists(CONTRADICTION_LOG_PATH):
            with open(CONTRADICTION_LOG_PATH, "w") as f:
                json.dump([], f, indent=2)

    def trace_from_beliefs(self, ecology: "BeliefEcology"):
        """
        New method: Populate contradiction edge list from current BeliefEcology.
        Fills self.traced_pairs with basic (id1, id2) edges for use in the graph engine.
        Does NOT recursively trace — this is fast-graph compatibility mode.
        """
        self.traced_pairs.clear()
        beliefs = list(ecology.beliefs.values())

        for i, b1 in enumerate(beliefs):
            for b2 in beliefs[i + 1:]:
                if self._is_contradictory(b1.content, b2.content):
                    self.traced_pairs.append((b1.id, b2.id))

    def trace_contradiction(self, b1: Belief, b2: Belief, depth=0, chain=None):
        """
        Full recursive contradiction trace. Logs context, entropy, confidence gap, and lineage.
        """
        if not self._is_contradictory(b1.content, b2.content):
            return {}

        contradiction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        chain = chain or []

        entry = {
            "id": contradiction_id,
            "timestamp": timestamp,
            "depth": depth,
            "belief_a": b1.to_dict(),
            "belief_b": b2.to_dict(),
            "confidence_gap": abs(b1.confidence - b2.confidence),
            "entropy_avg": round((b1.entropy + b2.entropy) / 2, 3),
            "trigger_chain": [b.to_dict() for b in chain],
            "conflict_score": self._calculate_conflict_score(b1, b2, depth)
        }

        print(f"🧠 [RCTS] Depth {depth} contradiction: \"{b1.content}\" ⛔ \"{b2.content}\"")
        self._log_contradiction(entry)

        # Recurse through parent chains if available
        if b1.origin and isinstance(b1.origin, str):
            parent = self._resolve_origin_belief(b1.origin)
            if parent:
                self.trace_contradiction(parent, b2, depth + 1, chain + [b1])
        if b2.origin and isinstance(b2.origin, str):
            parent = self._resolve_origin_belief(b2.origin)
            if parent:
                self.trace_contradiction(b1, parent, depth + 1, chain + [b2])

        return entry

    def load_all_traces(self):
        with open(CONTRADICTION_LOG_PATH, "r") as f:
            return json.load(f)

    def _calculate_conflict_score(self, b1: Belief, b2: Belief, depth: int) -> float:
        """
        Combine confidence gap, entropy, and depth to produce a synthetic contradiction score.
        """
        gap = abs(b1.confidence - b2.confidence)
        entropy_avg = (b1.entropy + b2.entropy) / 2
        return round((gap + entropy_avg + (depth * 0.5)), 3)

    def _is_contradictory(self, text1: str, text2: str) -> bool:
        """
        Naive contradiction detection. Replace with semantic/LLM-powered contradiction checker later.
        """
        opposites = [
            ("always", "never"),
            ("true", "false"),
            ("is", "is not"),
            ("can", "cannot"),
            ("will", "won't"),
            ("must", "must not"),
        ]

        t1, t2 = text1.lower(), text2.lower()
        for a, b in opposites:
            if (a in t1 and b in t2) or (b in t1 and a in t2):
                return True
        return False

    def _log_contradiction(self, trace: dict):
        with open(CONTRADICTION_LOG_PATH, "r+") as f:
            history = json.load(f)
            history.append(trace)
            f.seek(0)
            json.dump(history, f, indent=2)

    def _resolve_origin_belief(self, origin_id: str) -> Optional[Belief]:
        """
        Stub: Replace when BeliefEcology reference is available to resolve belief by ID.
        """
        return None
