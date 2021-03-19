# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tagger_ui.ui'
##
## Created by: Qt User Interface Compiler version 6.0.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from my_label import MediaLabel

import tagger_ui2_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1140, 850)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(0, 0))
        MainWindow.setMaximumSize(QSize(1920, 1080))
        MainWindow.setStyleSheet(u"padding: 0px; margin: 0px;")
        self.previous = QAction(MainWindow)
        self.previous.setObjectName(u"previous")
        icon = QIcon()
        icon.addFile(u":/:/icons/icons/previous.png", QSize(), QIcon.Normal, QIcon.On)
        self.previous.setIcon(icon)
        self.next = QAction(MainWindow)
        self.next.setObjectName(u"next")
        icon1 = QIcon()
        icon1.addFile(u":/:/icons/icons/next.png", QSize(), QIcon.Normal, QIcon.On)
        self.next.setIcon(icon1)
        self.actionRotate_left = QAction(MainWindow)
        self.actionRotate_left.setObjectName(u"actionRotate_left")
        icon2 = QIcon()
        icon2.addFile(u":/:/icons/icons/rotate_left.png", QSize(), QIcon.Normal, QIcon.On)
        self.actionRotate_left.setIcon(icon2)
        self.actionRotate_Right = QAction(MainWindow)
        self.actionRotate_Right.setObjectName(u"actionRotate_Right")
        icon3 = QIcon()
        icon3.addFile(u":/:/icons/icons/rotate_right.png", QSize(), QIcon.Normal, QIcon.On)
        self.actionRotate_Right.setIcon(icon3)
        self.actionPlay = QAction(MainWindow)
        self.actionPlay.setObjectName(u"actionPlay")
        icon4 = QIcon()
        icon4.addFile(u":/:/icons/icons/play_tagger.png", QSize(), QIcon.Normal, QIcon.On)
        self.actionPlay.setIcon(icon4)
        self.actionCrop = QAction(MainWindow)
        self.actionCrop.setObjectName(u"actionCrop")
        self.actionReload = QAction(MainWindow)
        self.actionReload.setObjectName(u"actionReload")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionMirror = QAction(MainWindow)
        self.actionMirror.setObjectName(u"actionMirror")
        self.actionDelete = QAction(MainWindow)
        self.actionDelete.setObjectName(u"actionDelete")
        icon5 = QIcon()
        icon5.addFile(u":/:/icons/icons/delete.png", QSize(), QIcon.Normal, QIcon.On)
        self.actionDelete.setIcon(icon5)
        self.actionActual_Size = QAction(MainWindow)
        self.actionActual_Size.setObjectName(u"actionActual_Size")
        self.actionBrowser = QAction(MainWindow)
        self.actionBrowser.setObjectName(u"actionBrowser")
        self.actionBrowser.setCheckable(True)
        self.actionBrowser.setChecked(True)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 797, 677))
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.scrollAreaWidgetContents.setLayoutDirection(Qt.LeftToRight)
        self.scrollAreaWidgetContents.setAutoFillBackground(False)
        self.scrollAreaWidgetContents.setStyleSheet(u"background: #000;")
        self.horizontalLayout_3 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.media = MediaLabel(self.scrollAreaWidgetContents)
        self.media.setObjectName(u"media")
        sizePolicy1.setHeightForWidth(self.media.sizePolicy().hasHeightForWidth())
        self.media.setSizePolicy(sizePolicy1)
        self.media.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.media.setAutoFillBackground(False)
        self.media.setStyleSheet(u"background: #000;")
        self.media.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.media)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setMinimumSize(QSize(325, 500))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Plain)
        self.layoutWidget = QWidget(self.frame)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 400, 321, 91))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.save_button = QPushButton(self.layoutWidget)
        self.save_button.setObjectName(u"save_button")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.save_button.sizePolicy().hasHeightForWidth())
        self.save_button.setSizePolicy(sizePolicy3)
        self.save_button.setMaximumSize(QSize(120, 26))
        self.save_button.setVisible(False)

        self.gridLayout.addWidget(self.save_button, 1, 0, 1, 1)

        self.no_save_button = QPushButton(self.layoutWidget)
        self.no_save_button.setObjectName(u"no_save_button")
        sizePolicy3.setHeightForWidth(self.no_save_button.sizePolicy().hasHeightForWidth())
        self.no_save_button.setSizePolicy(sizePolicy3)
        self.no_save_button.setMaximumSize(QSize(120, 26))
        self.no_save_button.setVisible(False)

        self.gridLayout.addWidget(self.no_save_button, 1, 1, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy4)
        self.label.setMaximumSize(QSize(16777215, 60))
        self.label.setVisible(False)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.gridLayout.setRowStretch(0, 1)
        self.layoutWidget1 = QWidget(self.frame)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(0, 0, 321, 213))
        self.gridLayout_2 = QGridLayout(self.layoutWidget1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setVerticalSpacing(15)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.glaring = QRadioButton(self.layoutWidget1)
        self.expression = QButtonGroup(MainWindow)
        self.expression.setObjectName(u"expression")
        self.expression.addButton(self.glaring)
        self.glaring.setObjectName(u"glaring")
        sizePolicy3.setHeightForWidth(self.glaring.sizePolicy().hasHeightForWidth())
        self.glaring.setSizePolicy(sizePolicy3)
        self.glaring.setMinimumSize(QSize(150, 22))
        self.glaring.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.glaring, 4, 1, 1, 1)

        self.assExposed = QRadioButton(self.layoutWidget1)
        self.buttonGroup_3 = QButtonGroup(MainWindow)
        self.buttonGroup_3.setObjectName(u"buttonGroup_3")
        self.buttonGroup_3.addButton(self.assExposed)
        self.assExposed.setObjectName(u"assExposed")
        sizePolicy3.setHeightForWidth(self.assExposed.sizePolicy().hasHeightForWidth())
        self.assExposed.setSizePolicy(sizePolicy3)
        self.assExposed.setMinimumSize(QSize(150, 22))
        self.assExposed.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.assExposed, 0, 1, 1, 1)

        self.breastsExposed = QRadioButton(self.layoutWidget1)
        self.buttonGroup_2 = QButtonGroup(MainWindow)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.breastsExposed)
        self.breastsExposed.setObjectName(u"breastsExposed")
        sizePolicy3.setHeightForWidth(self.breastsExposed.sizePolicy().hasHeightForWidth())
        self.breastsExposed.setSizePolicy(sizePolicy3)
        self.breastsExposed.setMinimumSize(QSize(150, 22))
        self.breastsExposed.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.breastsExposed, 1, 1, 1, 1)

        self.pussyExposed = QRadioButton(self.layoutWidget1)
        self.buttonGroup = QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.pussyExposed)
        self.pussyExposed.setObjectName(u"pussyExposed")
        sizePolicy3.setHeightForWidth(self.pussyExposed.sizePolicy().hasHeightForWidth())
        self.pussyExposed.setSizePolicy(sizePolicy3)
        self.pussyExposed.setMinimumSize(QSize(150, 22))
        self.pussyExposed.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.pussyExposed, 2, 1, 1, 1)

        self.breasts = QRadioButton(self.layoutWidget1)
        self.buttonGroup_2.addButton(self.breasts)
        self.breasts.setObjectName(u"breasts")
        sizePolicy3.setHeightForWidth(self.breasts.sizePolicy().hasHeightForWidth())
        self.breasts.setSizePolicy(sizePolicy3)
        self.breasts.setMinimumSize(QSize(150, 22))
        self.breasts.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.breasts, 1, 0, 1, 1)

        self.fullyClothed = QRadioButton(self.layoutWidget1)
        self.nudity = QButtonGroup(MainWindow)
        self.nudity.setObjectName(u"nudity")
        self.nudity.addButton(self.fullyClothed)
        self.fullyClothed.setObjectName(u"fullyClothed")
        sizePolicy3.setHeightForWidth(self.fullyClothed.sizePolicy().hasHeightForWidth())
        self.fullyClothed.setSizePolicy(sizePolicy3)
        self.fullyClothed.setMinimumSize(QSize(150, 22))
        self.fullyClothed.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.fullyClothed, 3, 0, 1, 1)

        self.fullyNude = QRadioButton(self.layoutWidget1)
        self.nudity.addButton(self.fullyNude)
        self.fullyNude.setObjectName(u"fullyNude")
        sizePolicy3.setHeightForWidth(self.fullyNude.sizePolicy().hasHeightForWidth())
        self.fullyNude.setSizePolicy(sizePolicy3)
        self.fullyNude.setMinimumSize(QSize(150, 22))
        self.fullyNude.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.fullyNude, 3, 1, 1, 1)

        self.ass = QRadioButton(self.layoutWidget1)
        self.buttonGroup_3.addButton(self.ass)
        self.ass.setObjectName(u"ass")
        sizePolicy3.setHeightForWidth(self.ass.sizePolicy().hasHeightForWidth())
        self.ass.setSizePolicy(sizePolicy3)
        self.ass.setMinimumSize(QSize(150, 22))
        self.ass.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.ass, 0, 0, 1, 1)

        self.pussy = QRadioButton(self.layoutWidget1)
        self.buttonGroup.addButton(self.pussy)
        self.pussy.setObjectName(u"pussy")
        sizePolicy3.setHeightForWidth(self.pussy.sizePolicy().hasHeightForWidth())
        self.pussy.setSizePolicy(sizePolicy3)
        self.pussy.setMinimumSize(QSize(150, 22))
        self.pussy.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.pussy, 2, 0, 1, 1)

        self.smiling = QRadioButton(self.layoutWidget1)
        self.expression.addButton(self.smiling)
        self.smiling.setObjectName(u"smiling")
        sizePolicy3.setHeightForWidth(self.smiling.sizePolicy().hasHeightForWidth())
        self.smiling.setSizePolicy(sizePolicy3)
        self.smiling.setMinimumSize(QSize(150, 22))
        self.smiling.setMaximumSize(QSize(150, 22))

        self.gridLayout_2.addWidget(self.smiling, 4, 0, 1, 1)

        self.pushButton = QPushButton(self.layoutWidget1)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy5 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy5)
        self.pushButton.setMaximumSize(QSize(120, 26))

        self.gridLayout_2.addWidget(self.pushButton, 5, 1, 1, 1)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 220, 325, 171))
        sizePolicy6 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy6)
        self.label_2.setMinimumSize(QSize(325, 0))
        self.label_2.setMaximumSize(QSize(325, 16777215))
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(0, 500, 325, 211))
        sizePolicy7 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(2)
        sizePolicy7.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy7)
        self.label_3.setMinimumSize(QSize(325, 0))
        self.label_3.setMaximumSize(QSize(325, 16777215))
        self.ass_reset = QRadioButton(self.frame)
        self.buttonGroup_3.addButton(self.ass_reset)
        self.ass_reset.setObjectName(u"ass_reset")
        self.ass_reset.setGeometry(QRect(10, 230, 0, 0))
        sizePolicy3.setHeightForWidth(self.ass_reset.sizePolicy().hasHeightForWidth())
        self.ass_reset.setSizePolicy(sizePolicy3)
        self.breasts_reset = QRadioButton(self.frame)
        self.buttonGroup_2.addButton(self.breasts_reset)
        self.breasts_reset.setObjectName(u"breasts_reset")
        self.breasts_reset.setGeometry(QRect(0, 239, 0, 0))
        sizePolicy3.setHeightForWidth(self.breasts_reset.sizePolicy().hasHeightForWidth())
        self.breasts_reset.setSizePolicy(sizePolicy3)
        self.pussy_reset = QRadioButton(self.frame)
        self.buttonGroup.addButton(self.pussy_reset)
        self.pussy_reset.setObjectName(u"pussy_reset")
        self.pussy_reset.setGeometry(QRect(4, 250, 0, 0))
        self.nudity_reset = QRadioButton(self.frame)
        self.nudity.addButton(self.nudity_reset)
        self.nudity_reset.setObjectName(u"nudity_reset")
        self.nudity_reset.setGeometry(QRect(30, 240, 0, 0))
        sizePolicy3.setHeightForWidth(self.nudity_reset.sizePolicy().hasHeightForWidth())
        self.nudity_reset.setSizePolicy(sizePolicy3)
        self.expression_reset = QRadioButton(self.frame)
        self.expression.addButton(self.expression_reset)
        self.expression_reset.setObjectName(u"expression_reset")
        self.expression_reset.setGeometry(QRect(50, 260, 0, 0))
        sizePolicy3.setHeightForWidth(self.expression_reset.sizePolicy().hasHeightForWidth())
        self.expression_reset.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.frame, 0, 1, 1, 1)

        self.assReset = QGroupBox(self.centralwidget)
        self.assReset.setObjectName(u"assReset")
        sizePolicy8 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.assReset.sizePolicy().hasHeightForWidth())
        self.assReset.setSizePolicy(sizePolicy8)
        self.assReset.setMinimumSize(QSize(0, 100))
        self.assReset.setMaximumSize(QSize(16777215, 100))
        self.assReset.setAutoFillBackground(False)
        self.assReset.setStyleSheet(u"background: #000;")
        self.horizontalLayout = QHBoxLayout(self.assReset)
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.gridLayout_3.addWidget(self.assReset, 1, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1140, 28))
        sizePolicy9 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.menubar.sizePolicy().hasHeightForWidth())
        self.menubar.setSizePolicy(sizePolicy9)
        self.menubar.setMinimumSize(QSize(0, 0))
        self.menubar.setMaximumSize(QSize(16777215, 30))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setObjectName(u"menuOptions")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        sizePolicy8.setHeightForWidth(self.toolBar.sizePolicy().hasHeightForWidth())
        self.toolBar.setSizePolicy(sizePolicy8)
        self.toolBar.setMinimumSize(QSize(0, 27))
        self.toolBar.setMaximumSize(QSize(16777215, 27))
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionExit)
        self.toolBar.addAction(self.actionBrowser)
        self.toolBar.addAction(self.actionRotate_left)
        self.toolBar.addAction(self.actionRotate_Right)
        self.toolBar.addAction(self.actionCrop)
        self.toolBar.addAction(self.actionDelete)
        self.toolBar.addAction(self.previous)
        self.toolBar.addAction(self.actionPlay)
        self.toolBar.addAction(self.next)
        self.toolBar.addAction(self.actionReload)
        self.toolBar.addAction(self.actionMirror)
        self.toolBar.addAction(self.actionActual_Size)

        self.retranslateUi(MainWindow)
        self.no_save_button.clicked.connect(self.actionReload.trigger)
        self.no_save_button.clicked.connect(self.no_save_button.hide)
        self.no_save_button.clicked.connect(self.save_button.hide)
        self.save_button.clicked.connect(self.no_save_button.hide)
        self.save_button.clicked.connect(self.save_button.hide)
        self.actionMirror.triggered.connect(self.save_button.show)
        self.actionMirror.triggered.connect(self.no_save_button.show)
        self.actionRotate_Right.triggered.connect(self.no_save_button.show)
        self.actionRotate_Right.triggered.connect(self.save_button.show)
        self.actionRotate_left.triggered.connect(self.save_button.show)
        self.actionRotate_left.triggered.connect(self.no_save_button.show)
        self.save_button.clicked.connect(self.label.hide)
        self.no_save_button.clicked.connect(self.label.hide)
        self.actionRotate_left.triggered.connect(self.label.show)
        self.actionRotate_Right.triggered.connect(self.label.show)
        self.actionMirror.triggered.connect(self.label.show)
        self.actionBrowser.toggled.connect(self.assReset.setVisible)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"BossyBot 2000 - Image Tagger", None))
        self.previous.setText(QCoreApplication.translate("MainWindow", u"<<", None))
#if QT_CONFIG(tooltip)
        self.previous.setToolTip(QCoreApplication.translate("MainWindow", u"View the previous slide.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.previous.setShortcut(QCoreApplication.translate("MainWindow", u"Left", None))
#endif // QT_CONFIG(shortcut)
        self.next.setText(QCoreApplication.translate("MainWindow", u">>", None))
#if QT_CONFIG(tooltip)
        self.next.setToolTip(QCoreApplication.translate("MainWindow", u"View the next slide.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.next.setShortcut(QCoreApplication.translate("MainWindow", u"Right", None))
#endif // QT_CONFIG(shortcut)
        self.actionRotate_left.setText(QCoreApplication.translate("MainWindow", u"Rotate left", None))
#if QT_CONFIG(shortcut)
        self.actionRotate_left.setShortcut(QCoreApplication.translate("MainWindow", u",", None))
#endif // QT_CONFIG(shortcut)
        self.actionRotate_Right.setText(QCoreApplication.translate("MainWindow", u"Rotate Right", None))
#if QT_CONFIG(shortcut)
        self.actionRotate_Right.setShortcut(QCoreApplication.translate("MainWindow", u".", None))
#endif // QT_CONFIG(shortcut)
        self.actionPlay.setText(QCoreApplication.translate("MainWindow", u">", None))
#if QT_CONFIG(shortcut)
        self.actionPlay.setShortcut(QCoreApplication.translate("MainWindow", u"Space", None))
#endif // QT_CONFIG(shortcut)
        self.actionCrop.setText(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.actionReload.setText(QCoreApplication.translate("MainWindow", u"Reload", None))
#if QT_CONFIG(shortcut)
        self.actionReload.setShortcut(QCoreApplication.translate("MainWindow", u"F5", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionMirror.setText(QCoreApplication.translate("MainWindow", u"Mirror", None))
        self.actionDelete.setText(QCoreApplication.translate("MainWindow", u"X", None))
#if QT_CONFIG(shortcut)
        self.actionDelete.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.actionActual_Size.setText(QCoreApplication.translate("MainWindow", u"Actual Size", None))
        self.actionBrowser.setText(QCoreApplication.translate("MainWindow", u"Browser", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.save_button.setText(QCoreApplication.translate("MainWindow", u"Yes (Save)", None))
        self.no_save_button.setText(QCoreApplication.translate("MainWindow", u"No (Reload)", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Current image modified, save it?", None))
        self.glaring.setText(QCoreApplication.translate("MainWindow", u"Glaring", None))
        self.assExposed.setText(QCoreApplication.translate("MainWindow", u"Ass(exposed)", None))
        self.breastsExposed.setText(QCoreApplication.translate("MainWindow", u"Breasts(exposed)", None))
        self.pussyExposed.setText(QCoreApplication.translate("MainWindow", u"Pussy(exposed)", None))
        self.breasts.setText(QCoreApplication.translate("MainWindow", u"Breasts", None))
        self.fullyClothed.setText(QCoreApplication.translate("MainWindow", u"Fully Clothed", None))
        self.fullyNude.setText(QCoreApplication.translate("MainWindow", u"Fully Nude", None))
        self.ass.setText(QCoreApplication.translate("MainWindow", u"Ass", None))
        self.pussy.setText(QCoreApplication.translate("MainWindow", u"Pussy", None))
        self.smiling.setText(QCoreApplication.translate("MainWindow", u"Smiling", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Save Tags", None))
        self.label_2.setText("")
        self.label_3.setText("")
        self.ass_reset.setText(QCoreApplication.translate("MainWindow", u"assReset", None))
        self.breasts_reset.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.pussy_reset.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.nudity_reset.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.expression_reset.setText(QCoreApplication.translate("MainWindow", u"RadioButton", None))
        self.assReset.setTitle("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuOptions.setTitle(QCoreApplication.translate("MainWindow", u"Options", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

