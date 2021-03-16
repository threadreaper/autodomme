from PySide6.QtWidgets import QApplication, QMainWindow # pylint: disable=no-name-in-module
import sys
import os
from tagger_ui2 import Ui_MainWindow

class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self) -> None:
        """
        Constructs the main window.
        """

        super(MainWindow, self).__init__()
        self.inter = Ui_MainWindow()
        self.inter.setupUi(self)
        self.dir_now = os.getcwd()
        self.inter.actionOpen.triggered.connect(self.inter.media.open_file)
        self.inter.next.triggered.connect(self.inter.media.next)
        self.inter.previous.triggered.connect(self.inter.media.previous)
        self.inter.actionReload.triggered.connect(self.inter.media.reload)
        self.inter.actionMirror.triggered.connect(self.inter.media.mirror)
        self.inter.save_button.clicked.connect(self.inter.media.save_image)
        self.inter.actionRotate_Right.triggered.connect(self.inter.media.rotate_right)
        self.inter.actionRotate_left.triggered.connect(self.inter.media.rotate_left)
        self.inter.actionDelete.triggered.connect(self.inter.media.delete)
        self.inter.actionCrop.triggered.connect(self.inter.media.crop)


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec_())
