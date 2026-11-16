"""Knowledge base that loads rules and provides rule evaluation."""
import json
import os
from config import KNOWLEDGE_DIR


class KnowledgeBase:
    def __init__(self):
        self.rules = []
        self.domain = {}
        self.load()

    def load(self):
        path = os.path.join(KNOWLEDGE_DIR, "supply_chain_rules.json")
        if os.path.exists(path):
            try:
                # utf-8-sig safely handles files with or without BOM
                with open(path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                self.rules = data.get("rules", [])
                self.domain = data.get("domain_knowledge", {})
            except json.JSONDecodeError as e:
                print(f"[KnowledgeBase] JSON error in {path}: {e}")
                self.rules = []
                self.domain = {}

    def get_rules(self):
        return self.rules

    def get_domain(self):
        return self.domain

    def add_rule(self, rule):
        self.rules.append(rule)
        self._persist()

    def _persist(self):
        path = os.path.join(KNOWLEDGE_DIR, "supply_chain_rules.json")
        # utf-8-sig writes BOM; use utf-8 to write WITHOUT BOM
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"rules": self.rules, "domain_knowledge": self.domain}, f, indent=2)
