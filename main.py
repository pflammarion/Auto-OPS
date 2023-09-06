import sys
from PyQt6.QtWidgets import QApplication

from controller import Controller
from view import View


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = View()
    view.show()
    sys.exit(app.exec())
