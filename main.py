"""Supply Chain Analyst - Agentic Local AI PyQt Frontend (Phase 2)."""
import sys
from PyQt5.QtWidgets import QApplication
from frontend.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
