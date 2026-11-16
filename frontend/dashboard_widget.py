from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt


class KpiCard(QFrame):
    def __init__(self, title, value="—", subtitle=""):
        super().__init__()
        self.setObjectName("kpi")
        self.setStyleSheet("""
            QFrame#kpi{background:#ffffff;border:1px solid #e1e6ed;
                       border-radius:10px;padding:12px;}
        """)
        v = QVBoxLayout(self)
        t = QLabel(title); t.setStyleSheet("color:#7a8aa0;font-weight:600;font-size:11px;")
        self.val = QLabel(value); self.val.setStyleSheet("font-size:22px;font-weight:700;color:#1e2a38;")
        self.sub = QLabel(subtitle); self.sub.setStyleSheet("color:#8d9aab;font-size:10px;")
        v.addWidget(t); v.addWidget(self.val); v.addWidget(self.sub)

    def set(self, value, subtitle=None, color=None):
        self.val.setText(str(value))
        if color:
            self.val.setStyleSheet(f"font-size:22px;font-weight:700;color:{color};")
        if subtitle is not None:
            self.sub.setText(subtitle)


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        title = QLabel("📊 Key Performance Indicators")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#1e2a38;padding:6px;")
        outer.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.cards = {}
        cards = [
            ("risk", "Composite Risk", "0%", "composite risk score"),
            ("sku", "SKUs", "0", "unique products"),
            ("suppliers", "Suppliers", "0", "unique suppliers"),
            ("stock", "Low Stock", "0", "SKUs below threshold"),
            ("otd", "On-Time %", "—", "delivery reliability"),
            ("margin", "Margin %", "—", "avg gross margin"),
            ("sentiment", "Sentiment", "—", "customer sentiment"),
            ("anomalies", "Anomalies", "0", "detected outliers"),
            ("returns", "Return %", "—", "return rate"),
            ("co2", "CO₂ (kg)", "—", "estimated footprint"),
        ]
        for i, (k, t, v, s) in enumerate(cards):
            card = KpiCard(t, v, s)
            self.cards[k] = card
            grid.addWidget(card, i // 5, i % 5)
        outer.addLayout(grid)
        outer.addStretch()

    def update_from_results(self, results):
        def find(name):
            return next((r for r in results if r["agent"] == name), None)

        risk = find("RiskAgent")
        if risk:
            score = risk.get("metrics", {}).get("risk_score", 0)
            color = "#d63031" if score > 60 else "#e17055" if score > 30 else "#00b894"
            self.cards["risk"].set(f"{score}%", color=color)

        sup = find("SupplierAgent")
        if sup:
            self.cards["suppliers"].set(sup.get("metrics", {}).get("supplier_count", "—"))

        inv = find("InventoryAgent")
        if inv:
            self.cards["stock"].set(inv.get("metrics", {}).get("low_stock_skus", "—"))

        log = find("LogisticsAgent")
        if log:
            rate = log.get("metrics", {}).get("on_time_rate")
            if rate is not None:
                pct = rate * 100 if rate <= 1 else rate
                color = "#00b894" if pct >= 90 else "#e17055" if pct >= 80 else "#d63031"
