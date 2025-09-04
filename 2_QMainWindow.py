import datetime
import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyWindow")

        """
            State Start
        """
        self.is_btn_clicked = False

        """
            Button Start
        """

        self.btn = QPushButton("Click me")
        self.btn.clicked.connect(self.btn_clicked)
        """
            Size Start
        """

        # 固定大小 400 * 400 , 不允许拖动
        # self.setFixedSize(QSize(400, 400))

        # 限制最大最小
        self.setMaximumSize(QSize(600, 600))
        self.setMinimumSize(QSize(200, 200))

        self.setCentralWidget(self.btn)

    def btn_clicked(self):
        self.is_btn_clicked = True
        self.btn.setText("Clicked")
        self.btn.setEnabled(False)



app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec())
