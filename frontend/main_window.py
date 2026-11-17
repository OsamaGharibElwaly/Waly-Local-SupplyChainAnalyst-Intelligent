import os
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem, QTextEdit, QProgressBar,
    QTabWidget, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, DATA_DIR
from backend import KnowledgeBase, AgentEngine, generate_markdown, generate_csv, export_json, export_html
from frontend.dashboard_widget import DashboardWidget
from frontend.charts_widget import ChartsWidget
from frontend.chat_widget import ChatWidget
from frontend.settings_widget import SettingsWidget


class AnalysisWorker(QThread):
    progress = pyqtSignal(int, str)
    finished_ok = pyqtSignal(list, object)

    def __init__(self, df, engine):
        super().__init__()
        self.df = df
        self.engine = engine

    def run(self):
        results = self.engine.analyze(self.df, lambda p, n: self.progress.emit(p, n))
        self.finished_ok.emit(results, self.df)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME + " v" + APP_VERSION)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.df = None
        self.results = None
        self.kb = KnowledgeBase()
        self.engine = AgentEngine(self.kb)
        self._build_ui()
        self.statusBar().showMessage("Ready - " + str(len(self.kb.get_rules())) + " rules loaded")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        bar = QHBoxLayout()
        self.btn_load = QPushButton("Import CSV")
        self.btn_sample = QPushButton("Load Sample")
        self.btn_run = QPushButton("Run Analysis")
        self.btn_export = QPushButton("Export Report")
        self.btn_run.setEnabled(False)
        self.btn_export.setEnabled(False)
        style = ("QPushButton{background:#2d6cdf;color:white;border-radius:6px;"
                 "padding:6px 12px;font-weight:600;} QPushButton:disabled{background:#95a5a6;}")
        for b in (self.btn_load, self.btn_sample, self.btn_run, self.btn_export):
            b.setMinimumHeight(34)
            b.setStyleSheet(style)
            bar.addWidget(b)
        bar.addStretch()
        root.addLayout(bar)

        self.info = QLabel("No dataset loaded.")
        self.info.setStyleSheet("color:#555;padding:4px;")
        root.addWidget(self.info)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        root.addWidget(self.progress)

        split = QSplitter(Qt.Horizontal)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.addWidget(QLabel("<b>Dataset Preview</b>"))
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        lv.addWidget(self.table)
        split.addWidget(left)

        right = QWidget()
        rv = QVBoxLayout(right)
        self.tabs = QTabWidget()
        self.report_view = QTextEdit(); self.report_view.setReadOnly(True); self.report_view.setFont(QFont("Consolas", 10))
        self.findings_view = QTextEdit(); self.findings_view.setReadOnly(True); self.findings_view.setFont(QFont("Consolas", 10))
        self.metrics_view = QTextEdit(); self.metrics_view.setReadOnly(True); self.metrics_view.setFont(QFont("Consolas", 10))
        self.dashboard = DashboardWidget()
        self.charts = ChartsWidget()
        self.chat = ChatWidget()
        self.settings = SettingsWidget()

        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(self.report_view, "Report")
        self.tabs.addTab(self.findings_view, "Findings")
        self.tabs.addTab(self.metrics_view, "Metrics")
        self.tabs.addTab(self.charts, "Charts")
        self.tabs.addTab(self.chat, "Chat")
        self.tabs.addTab(self.settings, "Settings")
        rv.addWidget(self.tabs)
        split.addWidget(right)

        split.setSizes([600, 800])
        root.addWidget(split)

        self.btn_load.clicked.connect(self.load_csv)
        self.btn_sample.clicked.connect(self.load_sample)
        self.btn_run.clicked.connect(self.run_analysis)
        self.btn_export.clicked.connect(self.export_report)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", DATA_DIR, "CSV Files (*.csv)")
        if not path:
            return
        try:
            self.df = pd.read_csv(path)
            self._set_df()
        except Exception as e:
            QMessageBox.critical(self, "Load error", str(e))

    def load_sample(self):
        path = os.path.join(DATA_DIR, "sample.csv")
        if not os.path.exists(path):
            QMessageBox.warning(self, "Missing", "sample.csv not found")
            return
        self.df = pd.read_csv(path)
        self._set_df()

    def _set_df(self):
        self.info.setText("Loaded " + str(len(self.df)) + " rows x " + str(len(self.df.columns)) +
                          " columns. Columns: " + ", ".join(map(str, self.df.columns)))
        self._populate_table(self.df)
        self.btn_run.setEnabled(True)
        self.progress.setValue(0)
        self.dashboard.reset()
        self.charts.set_data(self.df, [])

    def _populate_table(self, df):
        preview = df.head(200)
        self.table.setRowCount(len(preview))
        self.table.setColumnCount(len(preview.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in preview.columns])
        for r in range(len(preview)):
            for c in range(len(preview.columns)):
                self.table.setItem(r, c, QTableWidgetItem(str(preview.iloc[r, c])))
        self.table.resizeColumnsToContents()

    def run_analysis(self):
        if self.df is None:
            return
        self.btn_run.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.report_view.clear()
        self.findings_view.clear()
        self.metrics_view.clear()
        self.worker = AnalysisWorker(self.df, self.engine)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.start()

    def _on_progress(self, pct, agent):
        self.progress.setValue(pct)
        self.statusBar().showMessage("Running: " + str(agent) + " (" + str(pct) + "%)")

    def _on_done(self, results, df):
        self.results = results
        self.progress.setValue(100)
        self.btn_run.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.statusBar().showMessage("Analysis complete")
        self._render_results(results, df)

    def _render_results(self, results, df):
        lines = ["# Supply Chain Agentic Report",
                 "Rows: " + str(len(df)) + "  |  Columns: " + str(len(df.columns)),
                 "=" * 70, ""]
        for r in results:
            lines.append("> " + str(r["agent"]) + " - " + str(r.get("summary", "")) +
                         " (" + str(r.get("elapsed_ms", "-")) + " ms)")
            for f in r.get("findings", []):
                lines.append("   - " + str(f))
            if r.get("metrics"):
                lines.append("   Metrics: " + ", ".join(str(k) + "=" + str(v) for k, v in r["metrics"].items()))
            lines.append("")
        self.report_view.setPlainText("\n".join(lines))

        flines = []
        for r in results:
            flines.append("[" + str(r["agent"]) + "]")
            for f in r.get("findings", []):
                flines.append("  " + str(f))
            flines.append("")
        self.findings_view.setPlainText("\n".join(flines))

        mlines = []
        for r in results:
            if r.get("metrics"):
                mlines.append("[" + str(r["agent"]) + "]")
                for k, v in r["metrics"].items():
                    mlines.append("  " + str(k) + " = " + str(v))
                mlines.append("")
        self.metrics_view.setPlainText("\n".join(mlines) if mlines else "No metrics")

        self.dashboard.update_from_results(results)
        self.charts.set_data(df, results)
        self.chat.set_results(results)

        risk = next((r for r in results if r.get("agent") == "RiskAgent"), None)
        if risk and float(risk.get("metrics", {}).get("risk_score", 0)) > 50:
            QMessageBox.warning(self, "Risk Alert",
                                "Composite risk score: " + str(risk["metrics"]["risk_score"]) + "%")

    def export_report(self):
        if not self.results:
            return
        try:
            md = generate_markdown(self.df, self.results)
            csv = generate_csv(self.results)
            js = export_json(self.df, self.results)
            html = export_html(self.df, self.results)
            QMessageBox.information(
                self, "Export complete",
                "Markdown:\n" + md + "\n\nCSV:\n" + csv + "\n\nJSON:\n" + js + "\n\nHTML:\n" + html
            )
        except Exception as e:
            QMessageBox.critical(self, "Export error", str(e))
