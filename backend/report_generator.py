"""Report generator - produces markdown & CSV reports."""
import os
from datetime import datetime
from config import REPORTS_DIR


def generate_markdown(df, results, filename=None):
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{ts}.md"
    path = os.path.join(REPORTS_DIR, filename)
    lines = [
        "# Supply Chain Analyst – Agentic Report",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        f"**Rows analyzed:** {len(df)}  |  **Columns:** {len(df.columns)}",
        "",
        "## Summary",
        "",
        "| Agent | Findings | Time (ms) |",
        "|-------|----------|-----------|",
    ]
    for r in results:
        n = len(r.get("findings", []))
        lines.append(f"| {r['agent']} | {n} | {r.get('elapsed_ms', '-')} |")
    lines.append("")
    for r in results:
        lines.append(f"### {r['agent']} — {r.get('summary','')}")
        for f in r.get("findings", []):
            lines.append(f"- {f}")
        if r.get("metrics"):
            lines.append("")
            lines.append("**Metrics:**")
            for k, v in r["metrics"].items():
                lines.append(f"- `{k}`: {v}")
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def generate_csv(results, filename=None):
    import csv
    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{ts}.csv"
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["agent", "summary", "finding", "metrics"])
        for r in results:
            metrics_str = "; ".join(f"{k}={v}" for k, v in r.get("metrics", {}).items())
            for fd in r.get("findings", []):
                w.writerow([r["agent"], r.get("summary", ""), fd, metrics_str])
    return path
