# core/belief_ecology.py
# Author: Bradley R. Kinnard
# File: BeliefEcology core engine for Blackbox Mind v3
# Purpose: Manages dynamic belief storage, contradiction tracing, entropy decay, 
# and recursive mutation of belief structures in an autonomous cognitive AI system.
# Notes: Implements fitness scoring, lifecycle pruning, and contradiction-triggered 
# evolution logic for self-regulating belief ecologies.

import json
import os
from core.belief import Belief
from time import time
from difflib import SequenceMatcher
from core.contradiction_tracer import ContradictionTracer


class BeliefEcology:
    def __init__(self, memory_path="memory/episodic_store.json", verbose=False):
        self.beliefs = {}  # key: belief.id, value: Belief object
        self.memory_path = memory_path
        self.tracer = ContradictionTracer()
        self.verbose = verbose
        self.load_memory()

    def add_belief(self, content, source=None, confidence=0.5, utility=0.5):
        belief = Belief(content, source, confidence, utility)
        self.beliefs[belief.id] = belief
        return belief

    def reinforce_belief(self, belief_id, amount=0.1):
        if belief_id in self.beliefs:
            self.beliefs[belief_id].reinforce(amount)

    def decay_all(self):
        for belief in self.beliefs.values():
            belief.decay()

    def apply_entropy_decay(self, decay_rate=0.01):
        for belief in self.beliefs.values():
            belief.entropy += decay_rate
            if belief.entropy >= 1.0:
                belief.status = "decaying"

    def prune_beliefs(self):
        to_remove = [bid for bid, b in self.beliefs.items()
                     if b.status == "decaying" and b.entropy >= 1.2]
        for bid in to_remove:
            del self.beliefs[bid]

    def get_top_beliefs(self, limit=5, sort_by="fitness"):
        sorted_beliefs = sorted(
            self.beliefs.values(),
            key=lambda b: self.score_fitness(b),
            reverse=True
        )
        return sorted_beliefs[:limit]

    def score_fitness(self, belief):
        return (
            (belief.confidence * 0.4) +
            (belief.utility * 0.4) +
            (belief.recency * 0.2) -
            (belief.entropy * 0.5)
        )

    def load_memory(self):
        if not os.path.exists(self.memory_path):
            return
        with open(self.memory_path, "r") as f:
            data = json.load(f)
        for entry in data:
            b = Belief(**entry)
            self.beliefs[b.id] = b

    def save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump([b.to_dict() for b in self.beliefs.values()], f, indent=2)

    def semantic_similarity(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def fuse_content(self, c1, c2):
        tokens1 = c1.lower().split()
        tokens2 = c2.lower().split()
        half1 = tokens1[:len(tokens1)//2]
        half2 = tokens2[len(tokens2)//2:]
        return " ".join(half1 + half2)

    def detect_mutation_pairs(self, threshold=0.75):
        pairs = []
        belief_list = list(self.beliefs.values())
        for i in range(len(belief_list)):
            for j in range(i + 1, len(belief_list)):
                b1, b2 = belief_list[i], belief_list[j]
                similarity = self.semantic_similarity(b1.content, b2.content)
                if similarity >= threshold and b2.id not in b1.mutations:
                    pairs.append((b1, b2))
        return pairs

    def mutate_belief_pair(self, b1, b2):
        if b1.content == b2.content:
            return
        if b2.id in b1.mutations or b1.id in b2.mutations:
            return

        new_content = self.fuse_content(b1.content, b2.content)

        # Prevent trivial or identical mutations
        sim1 = self.semantic_similarity(new_content, b1.content)
        sim2 = self.semantic_similarity(new_content, b2.content)
        if new_content.strip() in (b1.content, b2.content) or sim1 > 0.9 or sim2 > 0.9:
            if self.verbose:
                print("⚠️ Mutation skipped: too similar to parent.")
            return

        new_confidence = (b1.confidence + b2.confidence) / 2 * 0.95
        new_utility = max(b1.utility, b2.utility) * 0.95

        new_belief = Belief(
            content=new_content,
            source=f"mutation:{b1.id[:6]}_{b2.id[:6]}",
            confidence=new_confidence,
            utility=new_utility
        )

        b1.mutations.append(new_belief.id)
        b2.mutations.append(new_belief.id)
        self.beliefs[new_belief.id] = new_belief

        if self.verbose:
            print(f"⚠️ Mutation occurred: '{b1.content}' + '{b2.content}' → '{new_content}'")
        return new_belief

    def is_contradictory(self, text1, text2):
        opposites = [("always", "never"), ("true", "false"), ("is", "is not")]
        for a, b in opposites:
            if a in text1.lower() and b in text2.lower():
                return True
            if b in text1.lower() and a in text2.lower():
                return True
        return False

    def detect_contradictions(self):
        checked = set()
        beliefs_list = list(self.beliefs.values())

        for b1 in beliefs_list:
            for b2 in beliefs_list:
                if b1.confidence < 0.1 or b2.confidence < 0.1:
                    continue
                if b1.id == b2.id or (b2.id, b1.id) in checked:
                    continue
                if self.is_contradictory(b1.content, b2.content):
                    self.tracer.trace_contradiction(b1, b2)
                    self.mutate_belief_pair(b1, b2)
                checked.add((b1.id, b2.id))

    def run_lifecycle_pass(self):
        self.apply_entropy_decay()
        self.detect_contradictions()
        self.prune_beliefs()

    def reload_all_memory(self):
        self.beliefs.clear()
        self.load_memory()
