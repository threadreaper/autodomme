# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow



class ImageTagger(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        for x in ('previous', 'next', 'rotate_left', 'rotate_right', 'play', 'delete'):
            new_action = QAction(QIcon(f'icons/{x}.png'), 'x')
            new_action.setObjectName(f'action{x}')
        for x in ('Crop', 'Thumbnail Bar', 'Exit', 'Reload', 'Mirror', 'Actual_Size', 'Browser', 'Open', 'Save'):
            new_action = QAction(x, self)
            new_action.setObjectName(f'action{x}')

if __name__ == "__main__":
    app = QApplication([])
    window = ImageTagger()
    window.show()
    sys.exit(app.exec_())
