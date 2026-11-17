import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QPushButton, QLabel
)
from PyQt5.QtCore import pyqtSignal
import config


class SettingsWidget(QWidget):
    settings_saved = pyqtSignal(dict)

    KEYS = [
        ("low_stock_days", "Low stock threshold (days)", 0, 365),
        ("high_lead_time", "High lead time (days)", 0, 365),
        ("high_defect_rate", "High defect rate (0-1)", 0.0, 1.0),
        ("supplier_score_warn", "Supplier score warning", 0, 100),
        ("anomaly_zscore", "Anomaly z-score", 1.0, 10.0),
        ("sentiment_negative", "Negative sentiment threshold", -1.0, 1.0),
    ]

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        title = QLabel("Threshold Settings")
        title.setStyleSheet("font-size:16px;font-weight:700;color:#1e2a38;padding:6px;")
        outer.addWidget(title)

        form = QFormLayout()
        self.spins = {}
        for key, label, lo, hi in self.KEYS:
            sp = QDoubleSpinBox()
            sp.setRange(lo, hi)
            sp.setDecimals(3)
            sp.setSingleStep(0.1 if hi <= 1 else 1)
            sp.setValue(float(config.THRESHOLDS.get(key, 0)))
            self.spins[key] = sp
            form.addRow(label + ":", sp)
        outer.addLayout(form)

        self.btn = QPushButton("Save Thresholds (session)")
        self.btn.setStyleSheet(
            "QPushButton{background:#2d6cdf;color:white;border-radius:6px;"
            "padding:8px 14px;font-weight:600;}"
        )
        outer.addWidget(self.btn)
        outer.addStretch()
        self.btn.clicked.connect(self._save)

    def _save(self):
        new = {}
        for key, sp in self.spins.items():
            val = float(sp.value())
            if key in ("high_defect_rate", "sentiment_negative"):
                new[key] = val
            else:
                new[key] = int(val) if val == int(val) else val
        config.THRESHOLDS.update(new)
        self.settings_saved.emit(dict(config.THRESHOLDS))
