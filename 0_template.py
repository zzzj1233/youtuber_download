import os.path
import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class MyApp(QMainWindow):
    pass


app = QApplication([])
myapp = MyApp()
myapp.setWindowTitle(os.path.basename(__file__))
myapp.show()

sys.exit(app.exec())
