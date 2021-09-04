import sys
from PyQt5.QtWidgets import QApplication
from pytreadmill import Window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Gui = Window()
    sys.exit(app.exec_())
