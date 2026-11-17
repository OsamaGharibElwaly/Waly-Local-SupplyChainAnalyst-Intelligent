from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit
)
from backend.query_engine import QueryEngine


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = QueryEngine()
        self.results = []

        outer = QVBoxLayout(self)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlainText(
            "Supply Chain Assistant\n"
            "Try: summary | risk | stock | supplier | cost | anomaly | trend | reorder | sentiment\n"
        )
        outer.addWidget(self.log)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask about your analysis...")
        self.send = QPushButton("Send")
        row.addWidget(self.input)
        row.addWidget(self.send)
        outer.addLayout(row)

        self.send.clicked.connect(self._send)
        self.input.returnPressed.connect(self._send)

    def set_results(self, results):
        self.results = results or []
        self.engine.set_results(self.results)

    def _send(self):
        q = self.input.text().strip()
        if not q:
            return
        self.input.clear()
        self.log.append("\nYou: " + q)
        ans = self.engine.answer(q)
        self.log.append("Assistant: " + str(ans))
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())
