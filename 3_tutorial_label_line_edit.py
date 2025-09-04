import os.path
import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.label = QLabel()
        self.lineEdit = QLineEdit()

        # signal 链接 label 的 setText
        self.lineEdit.textChanged.connect(self.label.setText)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)

        container = QWidget()
        container.setLayout(layout)

        self.resize(400, 400)
        self.setCentralWidget(container)


app = QApplication([])
myapp = MyApp()
myapp.setWindowTitle(os.path.basename(__file__))
myapp.show()

sys.exit(app.exec())
