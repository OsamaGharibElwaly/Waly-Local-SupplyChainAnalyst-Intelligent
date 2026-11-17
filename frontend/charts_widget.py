import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.results = []

        outer = QVBoxLayout(self)
        bar = QHBoxLayout()
        bar.addWidget(QLabel("<b>Chart</b>"))
        self.kind = QComboBox()
        self.kind.addItems(["Top N by category", "Time series", "Histogram"])
        self.col = QComboBox()
        self.val = QComboBox()
        self.btn = QPushButton("Render")
        for w in (self.kind, self.col, self.val, self.btn):
            bar.addWidget(w)
        bar.addStretch()
        outer.addLayout(bar)

        self.fig = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        outer.addWidget(self.canvas)

        self.btn.clicked.connect(self.render)

    def set_data(self, df, results):
        self.df = df
        self.results = results or []
        self.col.clear()
        self.val.clear()
        if df is not None:
            self.col.addItems([str(c) for c in df.columns])
            num = [str(c) for c in df.select_dtypes(include="number").columns]
            self.val.addItems(num if num else [str(c) for c in df.columns])

    def _num_series(self, df, col):
        s = df[col]
        if not pd.api.types.is_numeric_dtype(s):
            s = pd.to_numeric(s, errors="coerce")
        return s

    def render(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        if self.df is None or self.col.count() == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            self.canvas.draw()
            return

        kind = self.kind.currentText()
        col = self.col.currentText()
        val = self.val.currentText() if self.val.count() else None

        try:
            if kind == "Top N by category":
                if val and val in self.df.columns:
                    g = self.df.groupby(col)[val].sum().sort_values(ascending=False).head(10)
                else:
                    g = self.df[col].value_counts().head(10)
                ax.bar([str(i) for i in g.index], [float(v) for v in g.values], color="#2d6cdf")
                ax.set_title("Top 10 by " + col)
                ax.tick_params(axis="x", rotation=35)
            elif kind == "Time series":
                date_col = None
                for c in self.df.columns:
                    lc = str(c).lower()
                    if "date" in lc or "time" in lc:
                        date_col = c
                        break
                if not date_col:
                    ax.text(0.5, 0.5, "No date column", ha="center", va="center")
                else:
                    d = self.df.copy()
                    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
                    d = d.dropna(subset=[date_col])
                    if val and val in d.columns:
                        d[val] = pd.to_numeric(d[val], errors="coerce")
                        ts = d.groupby(date_col)[val].sum().sort_index()
                    else:
                        ts = d.groupby(date_col).size().sort_index()
                    ax.plot(list(ts.index), list(ts.values), marker="o", color="#2d6cdf")
                    ax.set_title("Time series " + str(date_col))
                    ax.tick_params(axis="x", rotation=35)
            else:
                s = self._num_series(self.df, col).dropna()
                ax.hist(s, bins=min(30, max(5, len(s) // 5 or 5)), color="#00b894")
                ax.set_title("Histogram of " + col)
        except Exception as e:
            ax.text(0.5, 0.5, "Chart error: " + str(e), ha="center", va="center")
        self.canvas.draw()
