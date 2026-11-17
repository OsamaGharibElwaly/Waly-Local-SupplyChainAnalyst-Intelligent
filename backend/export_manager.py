"""Export manager: JSON and self-contained HTML reports in addition to MD/CSV."""
import os
import json
from datetime import datetime
from config import REPORTS_DIR


def export_json(df, results, filename=None):
    if filename is None:
        filename = "report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    path = os.path.join(REPORTS_DIR, filename)
    payload = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "rows": int(len(df)),
        "columns": list(map(str, df.columns)),
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


def export_html(df, results, filename=None):
    if filename is None:
        filename = "report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".html"
    path = os.path.join(REPORTS_DIR, filename)
    rows = []
    for r in results:
        findings = "<br>".join(str(f) for f in r.get("findings", []))
        metrics = "<br>".join(str(k) + " = " + str(v) for k, v in r.get("metrics", {}).items())
        rows.append(
            "<tr><td>" + str(r.get("agent")) + "</td><td>" + str(r.get("summary", "")) +
            "</td><td>" + findings + "</td><td>" + metrics +
            "</td><td>" + str(r.get("elapsed_ms", "-")) + "</td></tr>"
        )
    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Supply Chain Report</title>"
        "<style>body{font-family:Segoe UI,Arial;margin:24px;background:#f7f9fc;color:#1e2a38}"
        "h1{color:#2d6cdf}table{border-collapse:collapse;width:100%;background:#fff}"
        "th,td{border:1px solid #e1e6ed;padding:8px;vertical-align:top;font-size:12px}"
        "th{background:#eef3fb;text-align:left}</style></head><body>"
        "<h1>Supply Chain Analyst Report</h1>"
        "<p><b>Generated:</b> " + datetime.now().isoformat(timespec="seconds") +
        " &nbsp; <b>Rows:</b> " + str(len(df)) + " &nbsp; <b>Agents:</b> " +
        str(len(results)) + "</p>"
        "<table><thead><tr><th>Agent</th><th>Summary</th><th>Findings</th>"
        "<th>Metrics</th><th>ms</th></tr></thead><tbody>" + "".join(rows) +
        "</tbody></table></body></html>"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
