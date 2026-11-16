"""Supply Chain Analyst - Agentic Local AI PyQt Frontend."""
import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem,
    QTextEdit, QProgressBar, QTabWidget, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, DATA_DIR
from backend import KnowledgeBase, AgentEngine
from backend.report_generator import generate_markdown, generate_csv


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
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.df = None
        self.results = None
        self.kb = KnowledgeBase()
        self.engine = AgentEngine(self.kb)
        self._build_ui()
        self.statusBar().showMessage(f"Ready · {len(self.kb.get_rules())} rules loaded")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Toolbar
        bar = QHBoxLayout()
        self.btn_load = QPushButton("📂 Import CSV")
        self.btn_sample = QPushButton("🎲 Load Sample")
        self.btn_run = QPushButton("▶ Run Analysis (10 Agents)")
        self.btn_export = QPushButton("💾 Export Report")
        self.btn_run.setEnabled(False)
        self.btn_export.setEnabled(False)
        for b in (self.btn_load, self.btn_sample, self.btn_run, self.btn_export):
            b.setMinimumHeight(34)
            b.setStyleSheet("QPushButton{background:#2d6cdf;color:white;border-radius:6px;padding:6px 12px;font-weight:600;} QPushButton:disabled{background:#95a5a6;}")
            bar.addWidget(b)
        bar.addStretch()
        root.addLayout(bar)

        self.info = QLabel("No dataset loaded. Import a CSV or load the sample.")
        self.info.setStyleSheet("color:#555;padding:4px;")
        root.addWidget(self.info)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        root.addWidget(self.progress)

        # Split view
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
        self.report_view = QTextEdit()
        self.report_view.setReadOnly(True)
        self.report_view.setFont(QFont("Consolas", 10))
        self.findings_view = QTextEdit()
        self.findings_view.setReadOnly(True)
        self.findings_view.setFont(QFont("Consolas", 10))
        self.metrics_view = QTextEdit()
        self.metrics_view.setReadOnly(True)
        self.metrics_view.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.report_view, "📋 Report")
        self.tabs.addTab(self.findings_view, "🔍 Findings")
        self.tabs.addTab(self.metrics_view, "📊 Metrics")
        rv.addWidget(self.tabs)
        split.addWidget(right)

        split.setSizes([650, 750])
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
        self.info.setText(f"Loaded {len(self.df)} rows × {len(self.df.columns)} columns. Columns: {', '.join(self.df.columns)}")
        self._populate_table(self.df)
        self.btn_run.setEnabled(True)
        self.progress.setValue(0)

    def _populate_table(self, df):
        preview = df.head(200)
        self.table.setRowCount(len(preview))
        self.table.setColumnCount(len(preview.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in preview.columns])
        for r in range(len(preview)):
            for c in range(len(preview.columns)):
                item = QTableWidgetItem(str(preview.iloc[r, c]))
                self.table.setItem(r, c, item)
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
        self.statusBar().showMessage(f"Running: {agent} ({pct}%)")

    def _on_done(self, results, df):
        self.results = results
        self.progress.setValue(100)
        self.btn_run.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.statusBar().showMessage("✓ Analysis complete")
        self._render_results(results, df)

    def _render_results(self, results, df):
        # Report tab
        lines = [f"# Supply Chain Agentic Report",
                 f"Rows: {len(df)}  |  Columns: {len(df.columns)}",
                 "=" * 70, ""]
        for r in results:
            lines.append(f"▶ {r['agent']} — {r.get('summary','')}  ({r.get('elapsed_ms','-')} ms)")
            for f in r.get("findings", []):
                lines.append(f"   • {f}")
            if r.get("metrics"):
                lines.append("   Metrics: " + ", ".join(f"{k}={v}" for k, v in r["metrics"].items()))
            lines.append("")
        self.report_view.setPlainText("\n".join(lines))

        # Findings tab
        flines = []
        for r in results:
            flines.append(f"[{r['agent']}]")
            for f in r.get("findings", []):
                flines.append(f"  {f}")
            flines.append("")
        self.findings_view.setPlainText("\n".join(flines))

        # Metrics tab
        mlines = []
        for r in results:
            if r.get("metrics"):
                mlines.append(f"[{r['agent']}]")
                for k, v in r["metrics"].items():
                    mlines.append(f"  {k} = {v}")
                mlines.append("")
        self.metrics_view.setPlainText("\n".join(mlines) if mlines else "No metrics")

        # Highlight risk in the report
        risk = next((r for r in results if r["agent"] == "RiskAgent"), None)
        if risk and risk.get("metrics", {}).get("risk_score", 0) > 50:
            QMessageBox.warning(self, "Risk Alert",
                                f"Composite risk score: {risk['metrics']['risk_score']}%")

    def export_report(self):
        if not self.results:
            return
        try:
            md = generate_markdown(self.df, self.results)
            csv = generate_csv(self.results)
            QMessageBox.information(self, "Export complete",
                                    f"Markdown:\n{md}\n\nCSV:\n{csv}")
        except Exception as e:
            QMessageBox.critical(self, "Export error", str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
