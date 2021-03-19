from __future__ import annotations

import test_rc
from PySide6.QtCore import QMargins, QMetaObject, QSize, Qt
from PySide6.QtGui import QAction, QCursor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QCheckBox,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QWidget,
)

EXP_EXP = QSizePolicy.Expanding, QSizePolicy.Expanding
FIX_FIX = QSizePolicy.Fixed, QSizePolicy.Fixed
FIX_EXP = QSizePolicy.Fixed, QSizePolicy.Expanding
EXP_FIX = QSizePolicy.Expanding, QSizePolicy.Fixed
INFINITE = 16777215
SUNKEN = "border: 2px inset #444;"
NO_MARGIN = "margin: 0;"
SEVENTY_FIVE = QSize(75, 75)
SIXTY_FOUR = QSize(64, 64)


class UIBuilder(object):
    """Constructs the UI for a main application window"""

    def setup(self, main_window: QMainWindow) -> None:
        """
        Initialize the UI.

        :param main_window: An instance of the `QMainWindow` class.
        :type main_window: :class:`QMainWindow`
        """
        main_window.setObjectName("main_window")
        main_window.setWindowTitle("TeaseAI")
        main_window.resize(1137, 751)
        main_window.setSizePolicy(*EXP_EXP)
        main_window.setTabShape(QTabWidget.Rounded)

        self.menubar = QMenuBar(main_window)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(0, 0, 1137, 23)
        self.file_menu = QMenu("File", self.menubar)
        self.file_menu.setObjectName("file_men")
        self.server_menu = QMenu("Server", self.menubar)
        self.server_menu.setObjectName("server_men")
        self.options_menu = QMenu("Options", self.menubar)
        self.options_menu.setObjectName("options_men")
        self.media_menu = QMenu("Media", self.menubar)
        self.media_menu.setObjectName("media_men")
        main_window.setMenuBar(self.menubar)

        self.exit = QAction("Exit", main_window)
        self.exit.setObjectName("exit")
        self.start_server = QAction("Start Server", main_window)
        self.start_server.setObjectName("start_server")
        self.connect_server = QAction("Connect to Server", main_window)
        self.connect_server.setObjectName("connect_server")
        self.kill_server = QAction("Kill Server", main_window)
        self.kill_server.setObjectName("kill_server")
        self.options = QAction("Options", main_window)
        self.options.setObjectName("options")
        self.start_webcam = QAction("Start Webcam", main_window)
        self.start_webcam.setObjectName("start_webcam")
        self.start_webcam.setCheckable(False)
        self.centralwidget = QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setContentsMargins(QMargins(0, 0, 0, 0))
        self.centralwidget.setSizePolicy(*EXP_EXP)
        self.grid_layout = QGridLayout(self.centralwidget)

        self.media = QFrame(self.centralwidget)
        self.media.setObjectName("media")
        self.media.setSizePolicy(*EXP_EXP)
        self.media.setMinimumSize(200, 200)
        self.media.setStyleSheet("background: #000;")
        self.grid_layout.addWidget(self.media, 0, 0, 5, 1)

        self.users_label = QLabel(" Online users:", self.centralwidget)
        self.users_label.setObjectName("users_label")
        self.users_label.setMinimumSize(300, 15)
        self.users_label.setMaximumSize(300, 15)
        self.grid_layout.addWidget(self.users_label, 0, 1, 1, 2)

        self.online = QPlainTextEdit("", self.centralwidget)
        self.online.setObjectName("online")
        self.online.setSizePolicy(*FIX_FIX)
        self.online.setMinimumSize(300, 50)
        self.online.setMaximumSize(300, 50)
        self.online.setStyleSheet("margin-left: 3px;" + SUNKEN)
        self.online.setLineWidth(2)
        self.online.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.online.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.online.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.online.setReadOnly(True)
        self.grid_layout.addWidget(self.online, 1, 1, 1, 2)

        self.chat = QPlainTextEdit("", self.centralwidget)
        self.chat.setObjectName("chat")
        self.chat.setSizePolicy(*FIX_EXP)
        self.chat.setMinimumSize(300, 0)
        self.chat.setMaximumSize(300, INFINITE)
        self.chat.setStyleSheet(
            "margin-bottom: 3px; margin-top: 8px;" + SUNKEN
        )
        self.chat.setLineWidth(2)
        self.chat.setReadOnly(True)
        self.chat.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_layout.addWidget(self.chat, 2, 1, 1, 2)

        self.input = QLineEdit(self.centralwidget)
        self.input.setObjectName("input")
        self.input.setSizePolicy(*FIX_FIX)
        self.input.setMinimumSize(224, 30)
        self.input.setMaximumSize(224, 30)
        self.input.setStyleSheet(SUNKEN)
        self.input.setEchoMode(QLineEdit.Normal)
        self.input.setClearButtonEnabled(True)
        self.grid_layout.addWidget(self.input, 3, 1, 1, 1)

        self.submit = QPushButton("Submit", self.centralwidget)
        self.submit.setObjectName("submit")
        self.submit.setSizePolicy(*FIX_FIX)
        self.submit.setMinimumSize(70, 30)
        self.submit.setMaximumSize(70, 30)
        self.grid_layout.addWidget(self.submit, 3, 2, 1, 1)

        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName("tabs")
        self.tabs.setSizePolicy(*FIX_FIX)
        self.tabs.setMinimumSize(300, 150)
        self.tabs.setMaximumSize(300, 150)
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.tabs.addTab(self.tab, "Actions")
        self.tab2 = QWidget()
        self.tab2.setObjectName("tab2")
        self.tabs.addTab(self.tab2, "My Media")
        self.tab3 = QWidget()
        self.tab3.setObjectName("tab3")
        self.tab3.setSizePolicy(*FIX_FIX)
        self.grid_layout2 = QGridLayout(self.tab3)
        self.grid_layout2.setHorizontalSpacing(0)
        self.grid_layout2.setVerticalSpacing(3)
        self.grid_layout2.setContentsMargins(3, -1, 3, -1)
        self.server_folder = QLineEdit(self.tab3)
        self.server_folder.setObjectName("server_folder")

        self.grid_layout2.addWidget(self.server_folder, 0, 0, 1, 3)
        self.srv_browse = QPushButton("BROWSE", self.tab3)
        self.srv_browse.setObjectName("srv_browse")
        self.srv_browse.setStyleSheet(
            "background: transparent;\n"
            "	color: #4d4940;\n"
            "    font-size: 8pt;\n"
            "	font-weight: 450;\n"
            "    padding: 6px;\n"
        )

        self.grid_layout2.addWidget(self.srv_browse, 0, 3, 1, 1)

        self.back_button = QPushButton("", self.tab3)
        self.back_button.setObjectName("back_button")
        self.back_button.setSizePolicy(*FIX_FIX)
        self.back_button.setMaximumSize(SEVENTY_FIVE)
        self.back_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.back_button.setStyleSheet(
            "border: 0;\n" "background: transparent;"
        )
        icon = QIcon()
        icon.addFile(
            ":/newPrefix/back_button.png", SIXTY_FOUR, QIcon.Normal, QIcon.Off
        )
        self.back_button.setIcon(icon)
        self.back_button.setIconSize(SIXTY_FOUR)

        self.grid_layout2.addWidget(self.back_button, 1, 0, 1, 1)

        self.play_button = QPushButton("", self.tab3)
        self.play_button.setObjectName("play_button")
        self.play_button.setSizePolicy(*FIX_FIX)
        self.play_button.setMaximumSize(SEVENTY_FIVE)
        self.play_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.play_button.setStyleSheet(
            "border: 0;\n" "background: transparent;"
        )
        icon1 = QIcon()
        icon1.addFile(
            ":/newPrefix/play_button.png", SIXTY_FOUR, QIcon.Normal, QIcon.Off
        )
        self.play_button.setIcon(icon1)
        self.play_button.setIconSize(SIXTY_FOUR)

        self.grid_layout2.addWidget(self.play_button, 1, 1, 1, 1)

        self.stop_button = QPushButton("", self.tab3)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setSizePolicy(*FIX_FIX)
        self.stop_button.setMaximumSize(SEVENTY_FIVE)
        self.stop_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_button.setStyleSheet(
            "border: 0;\n" "background: transparent;"
        )
        icon2 = QIcon()
        icon2.addFile(
            ":/newPrefix/stop_button.png", SIXTY_FOUR, QIcon.Normal, QIcon.Off
        )
        self.stop_button.setIcon(icon2)
        self.stop_button.setIconSize(SIXTY_FOUR)

        self.grid_layout2.addWidget(self.stop_button, 1, 2, 1, 1)

        self.fast_forward = QPushButton("", self.tab3)
        self.fast_forward.setObjectName("fast_forward")
        self.fast_forward.setSizePolicy(*FIX_FIX)
        self.fast_forward.setMaximumSize(SEVENTY_FIVE)
        self.fast_forward.setCursor(QCursor(Qt.PointingHandCursor))
        self.fast_forward.setStyleSheet(
            "border: 0;\n" "background: transparent;"
        )
        icon3 = QIcon()
        icon3.addFile(
            ":/newPrefix/fast_forward.png", SIXTY_FOUR, QIcon.Normal, QIcon.Off
        )
        self.fast_forward.setIcon(icon3)
        self.fast_forward.setIconSize(SIXTY_FOUR)

        self.grid_layout2.addWidget(self.fast_forward, 1, 3, 1, 1)

        self.tabs.addTab(self.tab3, "Server Media")
        self.grid_layout.addWidget(self.tabs, 4, 1, 1, 2)
        main_window.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setEnabled(True)
        self.statusbar.setStyleSheet("margin-bottom: 5px;")
        self.statusbar.setSizePolicy(*EXP_FIX)
        self.statusbar.setMinimumSize(INFINITE, 30)
        self.statusbar.setMaximumSize(INFINITE, 30)
        self.statusbar.setSizeGripEnabled(False)
        main_window.setStatusBar(self.statusbar)

        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.server_menu.menuAction())
        self.menubar.addAction(self.options_menu.menuAction())
        self.menubar.addAction(self.media_menu.menuAction())
        self.file_menu.addAction(self.exit)
        self.server_menu.addAction(self.start_server)
        self.server_menu.addAction(self.connect_server)
        self.server_menu.addAction(self.kill_server)
        self.options_menu.addAction(self.options)
        self.media_menu.addAction(self.start_webcam)
        self.exit.triggered.connect(main_window.close)
        self.tabs.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(main_window)
        self.exit.setStatusTip("Exit the program.")
        self.start_server.setStatusTip("Initialize a local server instance.")
        self.connect_server.setStatusTip("Connect to a remote server.")
        self.kill_server.setStatusTip("Shut down a running local server.")
        self.options.setStatusTip("Open the options menu.")
        self.start_webcam.setStatusTip("Start webcam feed.")
        self.tooltip = QLabel("", self.statusbar)
        tooltip_policy = QSizePolicy(*EXP_FIX)
        tooltip_policy.setHorizontalStretch(100)
        self.tooltip.setSizePolicy(tooltip_policy)
        self.tooltip.setMinimumSize(INFINITE, 26)
        self.tooltip.setMaximumSize(INFINITE, 26)
        self.server_status = QLabel("Server status:", self.statusbar)
        self.server_status.setSizePolicy(*FIX_FIX)
        self.server_status.setMinimumSize(300, 26)
        self.server_status.setMaximumSize(300, 26)
        self.client_status = QLabel("Client status:", self.statusbar)
        self.client_status.setSizePolicy(*FIX_FIX)
        self.client_status.setMinimumSize(302, 26)
        self.client_status.setMaximumSize(302, 26)
        self.statusbar.addPermanentWidget(self.tooltip)
        self.statusbar.addPermanentWidget(self.server_status)
        self.statusbar.addPermanentWidget(self.client_status)
        self.tooltip.setStyleSheet(
            SUNKEN
            + "margin-left: 4px;\
            margin-right: 0px;"
        )
        self.client_status.setStyleSheet(SUNKEN + "margin-right: 7px;")
        self.server_status.setStyleSheet(
            SUNKEN
            + "margin-right: 2px;\
            margin-left: 2px;"
        )
        self.statusbar.messageChanged.connect(main_window.status_tip)


class LoginBuilder(object):
    """Constructs a login window."""

    def setup(self, dialog):
        dialog.resize(320, 132)
        dialog.setModal(True)
        dialog.setWindowTitle("Please Login to Continue")
        self.form_layout = QFormLayout(dialog)
        self.form_layout.setObjectName("formLayout")
        self.login_label = QLabel("Server requesting authentication", dialog)
        self.login_label.setObjectName("login_label")
        self.form_layout.setWidget(
            0, QFormLayout.SpanningRole, self.login_label
        )

        self.username_label = QLabel(dialog)
        self.username_label.setObjectName("username_label")
        self.form_layout.setWidget(
            1, QFormLayout.LabelRole, self.username_label
        )

        self.username = QLineEdit(dialog)
        self.username.setObjectName("username")
        self.username.setStatusTip("Enter your username.")
        self.form_layout.setWidget(1, QFormLayout.FieldRole, self.username)

        self.password_label = QLabel(dialog)
        self.password_label.setObjectName("password_label")
        self.form_layout.setWidget(
            2, QFormLayout.LabelRole, self.password_label
        )

        self.password = QLineEdit(dialog)
        self.password.setObjectName("password")
        self.password.setStatusTip("Enter your password.")
        self.password.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.form_layout.setWidget(2, QFormLayout.FieldRole, self.password)

        self.save_username = QCheckBox("&Save username", dialog)
        self.save_username.setObjectName("save_username")
        self.form_layout.setWidget(
            3, QFormLayout.FieldRole, self.save_username
        )

        self.button_box = QDialogButtonBox(dialog)
        self.button_box.setObjectName("button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        )

        self.form_layout.setWidget(
            4, QFormLayout.SpanningRole, self.button_box
        )

        self.button_box.accepted.connect(dialog.accept)
        self.button_box.rejected.connect(dialog.close)

        QMetaObject.connectSlotsByName(dialog)
