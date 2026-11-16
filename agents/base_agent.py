"""Base class for all agents - resource efficient, local-only."""
import pandas as pd


class BaseAgent:
    name = "BaseAgent"
    description = "Base agent"

    def __init__(self, df: pd.DataFrame, knowledge):
        self.df = df
        self.knowledge = knowledge

    def can_run(self) -> bool:
        return self.df is not None and not self.df.empty

    def run(self) -> dict:
        raise NotImplementedError

    def _safe_col(self, *candidates):
        for c in candidates:
            if c in self.df.columns:
                return c
        return None
