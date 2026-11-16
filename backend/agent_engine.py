"""Agent engine: orchestrates all 10 agents using rule-based intelligence."""
import time
from agents import ALL_AGENTS


class AgentEngine:
    def __init__(self, knowledge):
        self.knowledge = knowledge

    def analyze(self, df, progress_cb=None):
        results = []
        n = len(ALL_AGENTS)
        for i, AgentCls in enumerate(ALL_AGENTS):
            agent = AgentCls(df, self.knowledge)
            t0 = time.time()
            try:
                res = agent.run()
            except Exception as e:
                res = {"agent": AgentCls.name, "summary": "error",
                       "findings": [f"Agent error: {e}"], "metrics": {}}
            res["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
            results.append(res)
            if progress_cb:
                progress_cb(int((i + 1) / n * 100), AgentCls.name)
        return results
