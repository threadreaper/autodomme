import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer

from main_window import UIBuilder
from server import Server


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self) -> None:
        """Constructs the main window"""
        super(MainWindow, self).__init__()
        self.ui = UIBuilder()
        self.ui.setup(self)
        self.server = Server()
        self.ui.start_server.triggered.connect(self.server.set_up_server)
        self.ui.kill_server.triggered.connect(self.server.kill)
        self.server_queue = QTimer(self)
        self.server_queue.timeout.connect(self.server_status)
        self.server_queue.start(15)

    def server_status(self):
        if not self.server.queue.empty():
            status = self.server.queue.get(False)
            self.ui.server_status.setText("Server status: " + status)

    def status_update(self, message):
        self.ui.tooltip.setText(message)


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
