import os.path
import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.label = QLabel("Normal label")

        # 打开后, 无需按下鼠标移动也会触发 mouseMoveEvent
        self.setMouseTracking(True)

        self.resize(400, 400)
        self.setCentralWidget(self.label)

    def mouseMoveEvent(self, event):
        self.label.setText("Mouse_Move")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.label.setText("Mouse_Press Left")
        if event.button() == Qt.MouseButton.MiddleButton:
            self.label.setText("Mouse_Press Middle")
        if event.button() == Qt.MouseButton.RightButton:
            self.label.setText("Mouse_Press Right")

    def mouseReleaseEvent(self, event):
        self.label.setText("Mouse_Release")

    def mouseDoubleClickEvent(self, event):
        self.label.setText("Mouse_Double_Click")

    """
        添加上下文按钮 ( 右键显示 )
    """
    def contextMenuEvent(self, a0, QContextMenuEvent=None):
        context = QMenu(self)
        context.addAction(QAction("action1", self))
        context.addAction(QAction("action2", self))
        context.addAction(QAction("action3", self))
        context.exec(a0.globalPos())


app = QApplication([])
myapp = MyApp()
myapp.setWindowTitle(os.path.basename(__file__))
myapp.show()

sys.exit(app.exec())
