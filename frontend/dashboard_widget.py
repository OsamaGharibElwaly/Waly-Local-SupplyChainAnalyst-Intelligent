from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout


class KpiCard(QFrame):
    def __init__(self, title, value="-", subtitle=""):
        super().__init__()
        self.setObjectName("kpi")
        self.setStyleSheet(
            "QFrame#kpi{background:#ffffff;border:1px solid #e1e6ed;"
            "border-radius:10px;padding:12px;}"
        )
        v = QVBoxLayout(self)
        t = QLabel(title)
        t.setStyleSheet("color:#7a8aa0;font-weight:600;font-size:11px;")
        self.val = QLabel(value)
        self.val.setStyleSheet("font-size:22px;font-weight:700;color:#1e2a38;")
        self.sub = QLabel(subtitle)
        self.sub.setStyleSheet("color:#8d9aab;font-size:10px;")
        v.addWidget(t)
        v.addWidget(self.val)
        v.addWidget(self.sub)

    def set(self, value, subtitle=None, color=None):
        self.val.setText(str(value))
        if color:
            self.val.setStyleSheet("font-size:22px;font-weight:700;color:" + color + ";")
        if subtitle is not None:
            self.sub.setText(subtitle)


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        title = QLabel("Key Performance Indicators")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#1e2a38;padding:6px;")
        outer.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)
        self.cards = {}
        cards = [
            ("risk", "Composite Risk", "-", "composite risk score"),
            ("sku", "SKUs", "0", "unique products"),
            ("suppliers", "Suppliers", "0", "unique suppliers"),
            ("stock", "Low Stock", "0", "SKUs below threshold"),
            ("otd", "On-Time %", "-", "delivery reliability"),
            ("margin", "Margin %", "-", "avg gross margin"),
            ("sentiment", "Sentiment", "-", "customer sentiment"),
            ("anomalies", "Anomalies", "0", "detected outliers"),
            ("returns", "Return %", "-", "return rate"),
            ("co2", "CO2 (kg)", "-", "estimated footprint"),
        ]
        for i, (k, t, v, s) in enumerate(cards):
            card = KpiCard(t, v, s)
            self.cards[k] = card
            grid.addWidget(card, i // 5, i % 5)
        outer.addLayout(grid)
        outer.addStretch()

    def reset(self):
        for c in self.cards.values():
            c.set("-", color=None)

    def update_from_results(self, results):
        def find(name):
            return next((r for r in results if r.get("agent") == name), None)

        risk = find("RiskAgent")
        if risk:
            score = risk.get("metrics", {}).get("risk_score", 0)
            try:
                score = float(score)
            except Exception:
                score = 0
            color = "#d63031" if score > 60 else "#e17055" if score > 30 else "#00b894"
            self.cards["risk"].set(str(score) + "%", color=color)

        sup = find("SupplierAgent")
        if sup:
            self.cards["suppliers"].set(sup.get("metrics", {}).get("supplier_count", "-"))

        inv = find("InventoryAgent")
        if inv:
            self.cards["stock"].set(inv.get("metrics", {}).get("low_stock_skus", "-"))

        log = find("LogisticsAgent")
        if log:
            rate = log.get("metrics", {}).get("on_time_rate")
            if rate is not None:
                pct = float(rate) * 100 if float(rate) <= 1 else float(rate)
                color = "#00b894" if pct >= 90 else "#e17055" if pct >= 80 else "#d63031"
                self.cards["otd"].set(str(round(pct, 1)) + "%", color=color)

        price = find("PricingAgent")
        if price:
            margin = price.get("metrics", {}).get("margin_pct")
            if margin is not None:
                color = "#00b894" if float(margin) >= 20 else "#e17055" if float(margin) >= 10 else "#d63031"
                self.cards["margin"].set(str(margin) + "%", color=color)

        sent = find("SentimentAgent")
        if sent:
            s = sent.get("metrics", {}).get("avg_sentiment")
            if s is not None:
                color = "#00b894" if float(s) > 0.1 else "#d63031" if float(s) < -0.1 else "#636e72"
                self.cards["sentiment"].set(("+" if float(s) > 0 else "") + str(s), color=color)

        an = find("AnomalyAgent")
        if an:
            self.cards["anomalies"].set(an.get("metrics", {}).get("total_anomalies", "-"))

        ret = find("ReturnsAgent")
        if ret:
            rate = ret.get("metrics", {}).get("return_rate")
            if rate is not None:
                pct = float(rate) * 100
                color = "#d63031" if pct > 5 else "#00b894"
                self.cards["returns"].set(str(round(pct, 2)) + "%", color=color)

        co2 = find("CarbonAgent")
        if co2:
            kg = co2.get("metrics", {}).get("total_co2_kg")
            if kg is not None:
                self.cards["co2"].set(str(kg))

        seg = find("SegmentAgent")
        if seg:
            counts = seg.get("metrics", {}).get("segment_counts", {})
            if counts:
                self.cards["sku"].set(str(sum(counts.values())))
