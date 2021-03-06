# type: ignore
"""Image tagging application for generating annotations for AI training data
for nudity detection."""
from __future__ import annotations

import os
import sys
from contextlib import suppress

from PIL import Image
from PIL.PngImagePlugin import PngInfo
from PySide6.QtCore import QPoint, QRect, QMarginsF, QRectF, QSize, Qt, Signal, QTimer, QPointF # pylint: disable=no-name-in-module
from PySide6.QtGui import (QAction, QIcon, QMouseEvent, QPen, QKeyEvent,# pylint: disable=no-name-in-module
                           QPixmap, QTransform, QWheelEvent, QBrush, QFont)# pylint: disable=no-name-in-module
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFrame, QGridLayout, # pylint: disable=no-name-in-module
                               QHBoxLayout, QLabel, QMainWindow, QMenu, # pylint: disable=no-name-in-module
                               QMenuBar, QPushButton, QRadioButton,# pylint: disable=no-name-in-module
                               QSizePolicy, QToolBar, QWidget,  QFileDialog, # pylint: disable=no-name-in-module;
                               QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                               QGraphicsRectItem, QGraphicsTextItem)# pylint: disable=no-name-in-module;

from icons import delete, icon, next_icon, play, previous, left, right, reload

EXP_FIX = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
EXP_EXP = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
EXP_MAX = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
FIX_FIX = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
INFINITE = 16777215


class ClickableLabel(QLabel):
    """Custom class for a QLabel that responds to click events."""
    def __init__(self, parent: QWidget, file: str) -> None:
        QLabel.__init__(self, parent)
        self.file = file
        self.sizePolicy().setHorizontalStretch(1)
        self.setSizePolicy(EXP_FIX)
        self.setMinimumSize(QSize(0, 100))
        self.setMaximumSize(QSize(INFINITE, 100))
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignCenter)
        self.app = parent

    def mouseReleaseEvent(self, event: QMouseEvent) -> None: # pylint: disable=unused-argument, invalid-name
        """When this label is clicked, open the associated image file."""
        self.app.open_file(self.file)

class MyView(QGraphicsView):
    """Custom graphics view class for drawing crop rectangles"""
    got_rect = Signal(tuple)

    def __init__(self, scene: QGraphicsScene, parent: QMainWindow):
        QGraphicsView.__init__(self, scene, parent)
        self.crop_rect = QRect(QPoint(0, 0), QSize(0, 0))
        self.g_rect = QGraphicsRectItem(QRectF(self.crop_rect))
        self.setParent(parent)
        self.app = self.parent()
        self.crop_btn = self.parent().crop_button
        self.mouse_down = False
        self.g_rect.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        self.g_rect.setBrush(QBrush(Qt.red, Qt.Dense6Pattern))
        self.mouse_pos = QPoint(0, 0)
        self.adjustment = ''
        self.annotation = False

    def reset(self):
        self.crop_rect = QRect(QPoint(0, 0), QSize(0, 0))
        self.g_rect = QGraphicsRectItem(QRectF(self.crop_rect))
        self.g_rect.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        self.g_rect.setBrush(QBrush(Qt.red, Qt.Dense6Pattern))
        self.setMouseTracking(False)
        self.unsetCursor()
        self.mouse_pos = QPoint(0, 0)
        self.adjustment = ''
        self.mouse_down = False
        if self.crop_btn.isChecked():
            self.app.reload()
            self.setCursor(Qt.CrossCursor)
        if self.annotation:
            self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event: QMouseEvent): # pylint: disable=invalid-name
        """Mouse event handler; begins a crop action"""
        self.mouse_down = True
        self.mouse_pos = self.mapToScene(event.pos()).toPoint()
        if self.crop_btn.isChecked() or self.annotation:
            self.crop_rect.setTopLeft(self.mapToScene(event.pos()).toPoint())
            self.scene().addItem(self.g_rect)
        if self.annotation:
            self.g_rect.setPen(QPen(Qt.magenta, 1, Qt.SolidLine))
            self.g_rect.setBrush(QBrush(Qt.magenta, Qt.Dense4Pattern))
        elif self.hasMouseTracking() and self.g_rect.isUnderMouse:
            self.adjustment = self.edge(event.pos)[1]
        else:
            QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent):    # pylint: disable=invalid-name
        """Expand crop rectangle"""
        if self.crop_btn.isChecked() | self.annotation and self.mouse_down:
            self.crop_rect.setBottomRight(self.mapToScene(event.pos()).toPoint())
            self.g_rect.setRect(self.crop_rect)
        if self.hasMouseTracking():
            self.setCursor(
                (Qt.ArrowCursor, self.edge(event.pos)[0])
                [self.is_under_mouse(self.g_rect.rect())])
            if self.mouse_down:
                self.move_rect(event.pos)

    def wheelEvent(self, event: QMouseEvent):
        if self.hasMouseTracking():
            self.reset()
        elif self.annotation:
            self.annotation = False
            self.unsetCursor()
        else:
            event.ignore()

    def is_under_mouse(self, rect: QRectF):
        widen = rect + QMarginsF(10, 10, 10, 10)
        self.g_rect.setRect(widen)
        res = self.g_rect.isUnderMouse()
        self.g_rect.setRect(rect)
        return res

    def move_rect(self, pos):
        delta = self.mapToScene(pos()).toPoint() - self.mouse_pos
        self.mouse_pos = self.mapToScene(pos()).toPoint()
        if self.adjustment == 'inside':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(delta.x(), delta.y(),
                                            delta.x(), delta.y()))
        elif self.adjustment == 'left':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(delta.x(), 0, 0, 0))
        elif self.adjustment == 'right':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(0, 0, delta.x(), 0))
        elif self.adjustment == 'top':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(0, delta.y(), 0, 0))
        elif self.adjustment == 'bottom':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(0, 0, 0, delta.y()))
        elif self.adjustment == 'top_left':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(delta.x(), delta.y(), 0, 0))
        elif self.adjustment == 'top_right':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(0, delta.y(), delta.x(), 0))
        elif self.adjustment == 'bot_left':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(delta.x(), 0, 0, delta.y()))
        elif self.adjustment == 'bot_right':
            self.g_rect.setRect(
                self.g_rect.rect().adjusted(0, 0, delta.x(), delta.y()))

    def edge(self, pos):
        event_pos = self.mapToScene(pos()).toPoint()
        rect_left = int(self.g_rect.rect().left())
        rect_right = int(self.g_rect.rect().right())
        rect_top = int(self.g_rect.rect().top())
        rect_bottom = int(self.g_rect.rect().bottom())
        on_left, on_right, on_top, on_bottom = (False, False, False, False)
        if event_pos.x() in range(rect_left - 10, rect_left + 10):
            on_left = True
        if event_pos.x() in range(rect_right - 10, rect_right + 10):
            on_right = True
        if event_pos.y() in range(rect_top - 10, rect_top + 10):
            on_top = True
        if event_pos.y() in range(rect_bottom - 10, rect_bottom + 10):
            on_bottom = True
        if (on_left and on_bottom) or (on_top and on_right):
            return (Qt.SizeBDiagCursor, ('bot_left', 'top_right')[on_right])
        if (on_left and on_top) | (on_right and on_bottom):
            return (Qt.SizeFDiagCursor, ('top_left', 'bot_right')[on_right])
        if on_left | on_right:
            return (Qt.SizeHorCursor, ('left', 'right')[on_right])
        if on_top | on_bottom:
            return (Qt.SizeVerCursor, ('top', 'bottom')[on_bottom])
        else:
            return ((Qt.OpenHandCursor, Qt.ClosedHandCursor)[self.mouse_down], 'inside')

    def mouseReleaseEvent(self, event: QMouseEvent): # pylint: disable=invalid-name
        """Completes the crop rectangle."""
        self.mouse_down = False
        if self.crop_btn.isChecked() | self.annotation:
            self.crop_rect.setBottomRight(self.mapToScene(event.pos()).toPoint())
            self.g_rect.setRect(self.crop_rect)
            self.setMouseTracking(True)
            self.crop_btn.setChecked(False)
            self.annotation = False
            self.unsetCursor()

class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self) -> None:
        QMainWindow.__init__(self)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.setMaximumSize(QSize(1920, 1080))
        self.setStyleSheet("padding: 0px; margin: 0px;")
        self.setIconSize(QSize(32, 32))
        self.setWindowTitle("BossyBot 2000 - Image Tagger")
        self.setWindowIcon(self.load_icon(icon))

        self.menubar = QMenuBar(self)
        self.menubar.setSizePolicy(EXP_MAX)
        self.menubar.setMaximumSize(QSize(INFINITE, 30))
        self.menu_file = QMenu('File', self.menubar)
        self.menu_options = QMenu('Options', self.menubar)
        self.menu_help = QMenu('Help', self.menubar)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_options.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())
        self.open = QAction('Open', self)
        self.menu_file.addAction(self.open)
        self.open.triggered.connect(self.open_file)
        self.exit_button = QAction('Exit', self)
        self.exit_button.triggered.connect(lambda: sys.exit(0), Qt.QueuedConnection)
        self.menu_file.addAction(self.exit_button)
        self.setMenuBar(self.menubar)

        self.previous_button = QAction(self.load_icon(previous), '<<', self)
        self.next_button = QAction(self.load_icon(next_icon), '>>', self)
        self.rotate_left_button = QAction(self.load_icon(left), '', self)
        self.rotate_right_button = QAction(self.load_icon(right), '', self)
        self.play_button = QAction(self.load_icon(play), '', self)
        self.play_button.setCheckable(True)
        self.delete_button = QAction(self.load_icon(delete), '', self)
        self.reload_button = QAction(self.load_icon(reload), '', self)
        self.mirror_button = QAction('Mirror', self)
        self.actual_size_button = QAction('Actual Size', self)
        self.browser_button = QAction('Browser', self)
        self.browser_button.setCheckable(True)
        self.browser_button.setChecked(True)
        self.crop_button = QAction('Crop', self)
        self.crop_button.setCheckable(True)

        self.toolbuttons = {
            self.rotate_left_button: {'shortcut': ',', 'connect': lambda:
                self.pixmap.setRotation(self.pixmap.rotation() - 90)},
            self.rotate_right_button: {'shortcut': '.', 'connect': lambda:
                self.pixmap.setRotation(self.pixmap.rotation() + 90)},
            self.delete_button: {'shortcut': 'Del', 'connect': self.delete},
            self.previous_button: {'shortcut': 'Left', 'connect': self.previous},
            self.play_button: {'shortcut': 'Space', 'connect': self.play},
            self.next_button: {'shortcut': 'Right', 'connect': self.next},
            self.reload_button: {'shortcut': 'F5', 'connect': self.reload}
        }

        self.toolbar = QToolBar(self)
        self.toolbar.setSizePolicy(EXP_MAX)
        self.toolbar.setMaximumSize(QSize(INFINITE, 27))
        for _ in (self.browser_button, self.crop_button, self.mirror_button,
                  self.actual_size_button):
            self.toolbar.addAction(_)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        for button in self.toolbuttons:
            button.setShortcut(self.toolbuttons[button]['shortcut'])
            button.triggered.connect(self.toolbuttons[button]['connect'])
            self.toolbar.addAction(button)

        self.centralwidget = QWidget(self)
        self.centralwidget.setSizePolicy(EXP_EXP)
        self.setCentralWidget(self.centralwidget)
        self.grid = QGridLayout(self.centralwidget)

        self.media = QGraphicsScene(self)
        self.media.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.media.setBackgroundBrush(QBrush(Qt.black))
        self.view = MyView(self.media, self)
        self.view.setSizePolicy(EXP_EXP)
        self.media.setSceneRect(0, 0, self.view.width(), self.view.height())
        self.grid.addWidget(self.view, 0, 0, 1, 1)

        self.frame = QFrame(self.centralwidget)
        self.frame.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.MinimumExpanding))
        self.frame.setMinimumSize(QSize(325, 500))
        self.frame.setStyleSheet(
            "QFrame { border: 4px inset #222; border-radius: 10; }")

        self.layout_widget = QWidget(self.frame)
        self.layout_widget.setGeometry(QRect(0, 400, 321, 91))
        self.layout_widget.setContentsMargins(15, 15, 15, 15)

        self.grid2 = QGridLayout(self.layout_widget)
        self.grid2.setContentsMargins(0, 0, 0, 0)

        self.save_button = QPushButton('Yes (Save)', self.layout_widget)
        self.save_button.setSizePolicy(FIX_FIX)
        self.save_button.setMaximumSize(QSize(120, 26))
        self.save_button.setVisible(False)
        self.grid2.addWidget(self.save_button, 1, 0, 1, 1)

        self.no_save_button = QPushButton('No (Reload)', self.layout_widget)
        self.no_save_button.setSizePolicy(FIX_FIX)
        self.no_save_button.setMaximumSize(QSize(120, 26))
        self.no_save_button.setVisible(False)
        self.grid2.addWidget(self.no_save_button, 1, 1, 1, 1)

        self.label = QLabel("Current image modified, save it?", self.layout_widget)
        self.label.setSizePolicy(FIX_FIX)
        self.label.setMaximumSize(QSize(325, 60))
        self.label.setVisible(False)
        self.label.setAlignment(Qt.AlignCenter)
        self.grid2.addWidget(self.label, 0, 0, 1, 2)

        self.layout_widget = QWidget(self.frame)
        self.layout_widget.setGeometry(QRect(0, 0, 321, 213))

        self.ass = QRadioButton('Ass', self.layout_widget)
        self.ass_exposed = QRadioButton('Ass (exposed)', self.layout_widget)
        self.ass_reset = QRadioButton(self.frame)
        self.ass_group = QButtonGroup(self)

        self.breasts = QRadioButton('Breasts', self.layout_widget)
        self.breasts_exposed = QRadioButton('Breasts (exposed)', self.layout_widget)
        self.breasts_reset = QRadioButton(self.frame)
        self.breasts_group = QButtonGroup(self)

        self.pussy = QRadioButton('Pussy', self.layout_widget)
        self.pussy_exposed = QRadioButton('Pussy (exposed)', self.layout_widget)
        self.pussy_reset = QRadioButton(self.frame)
        self.pussy_group = QButtonGroup(self)

        self.fully_clothed = QRadioButton('Fully Clothed', self.layout_widget)
        self.fully_nude = QRadioButton('Fully Nude', self.layout_widget)
        self.nudity_reset = QRadioButton(self.frame)
        self.nudity = QButtonGroup(self)

        self.smiling = QRadioButton('Smiling', self.layout_widget)
        self.glaring = QRadioButton('Glaring', self.layout_widget)
        self.expression_reset = QRadioButton(self.frame)
        self.expression = QButtonGroup(self)


        self.grid3 = QGridLayout(self.layout_widget)
        self.grid3.setVerticalSpacing(15)
        self.grid3.setContentsMargins(0, 15, 0, 0)

        self.radios = {
            self.ass: {'this': 'ass', 'that': 'ass_exposed',
                       'group': self.ass_group, 'reset': self.ass_reset,
                       'grid': (0, 0, 1, 1)},
            self.ass_exposed: {'this': 'ass_exposed', 'that': 'ass',
                               'group': self.ass_group, 'reset': self.ass_reset,
                               'grid': (0, 1, 1, 1)},
            self.breasts: {'this': 'breasts', 'that': 'breasts_exposed',
                           'group': self.breasts_group,
                           'reset': self.breasts_reset, 'grid': (1, 0, 1, 1)},
            self.breasts_exposed: {'this': 'breasts_exposed','that': 'breasts',
                                   'group': self.breasts_group,
                                   'reset': self.breasts_reset,
                                   'grid': (1, 1, 1, 1)},
            self.pussy: {'this': 'pussy', 'that': 'pussy_exposed',
                         'group': self.pussy_group, 'reset': self.pussy_reset,
                         'grid': (2, 0, 1, 1)},
            self.pussy_exposed: {'this': 'pussy_exposed', 'that': 'pussy',
                                 'group': self.pussy_group,
                                 'reset': self.pussy_reset,
                                 'grid': (2, 1, 1, 1)},
            self.fully_clothed: {'this': 'fully_clothed',
                                 'that': 'fully_nude', 'group': self.nudity,
                                 'reset': self.nudity_reset,
                                 'grid': (3, 0, 1, 1)},
            self.fully_nude: {'this': 'fully_nude', 'that': 'fully_clothed',
                              'group': self.nudity, 'reset': self.nudity_reset,
                              'grid': (3, 1, 1, 1)},
            self.smiling: {'this': 'smiling', 'that': 'glaring',
                           'group': self.expression,
                           'reset': self.expression_reset,
                           'grid': (4, 0, 1, 1)},
            self.glaring: {'this': 'glaring', 'that': 'smiling',
                           'group': self.expression,
                           'reset': self.expression_reset,
                           'grid': (4, 1, 1, 1)},
        }

        for radio in self.radios:
            radio.setSizePolicy(FIX_FIX)
            radio.setMaximumSize(QSize(150, 22))
            self.radios[radio]['reset'].setGeometry(QRect(0, 0, 0, 0))
            self.grid3.addWidget(radio, *self.radios[radio]['grid'])
            if self.radios[radio]['group'] != self.nudity:
                radio.toggled.connect(lambda x=_, y=radio: self.annotate(self.radios[y]['this']))
            self.radios[radio]['group'].addButton(radio)
            self.radios[radio]['group'].addButton(self.radios[radio]['reset'])

        self.save_tags_button = QPushButton('Save Tags', self.layout_widget)
        self.save_tags_button.setSizePolicy(FIX_FIX)
        self.save_tags_button.setMaximumSize(QSize(120, 26))
        self.grid3.addWidget(self.save_tags_button, 5, 1, 1, 1)

        self.grid.addWidget(self.frame, 0, 1, 1, 1)

        self.browse_bar = QLabel(self.centralwidget)
        self.browse_bar.setSizePolicy(EXP_FIX)
        self.browse_bar.setMinimumSize(QSize(0, 100))
        self.browse_bar.setMaximumSize(QSize(INFINITE, 100))
        self.browse_bar.setStyleSheet("background: #000;")
        self.browse_bar.setAlignment(Qt.AlignCenter)
        self.h_box2 = QHBoxLayout(self.browse_bar)
        self.h_box2.setContentsMargins(4, 0, 0, 0)

        self.grid.addWidget(self.browse_bar, 1, 0, 1, 2)

        hiders = [self.no_save_button.clicked, self.save_button.clicked,
                  self.reload_button.triggered]
        for hider in hiders:
            hider.connect(self.save_button.hide)
            hider.connect(self.no_save_button.hide)
            hider.connect(self.label.hide)
        showers = [self.mirror_button.triggered,
                   self.rotate_right_button.triggered,
                   self.rotate_left_button.triggered]
        for shower in showers:
            shower.connect(self.save_button.show)
            shower.connect(self.no_save_button.show)
            shower.connect(self.label.show)

        self.no_save_button.clicked.connect(self.reload)
        self.browser_button.toggled.connect(self.browse_bar.setVisible)

        self.play_button.toggled.connect(
            lambda: self.frame.setVisible(
                (True, False)[self.frame.isVisible()]))
        self.reload_button.triggered.connect(self.reload)
        self.mirror_button.triggered.connect(lambda: self.pixmap.setScale(-1))
        self.save_button.clicked.connect(self.save_image)
        self.play_button.toggled.connect(
            lambda: self.browser_button.setChecked(
                (True, False)[self.browse_bar.isVisible()]))
        self.crop_button.toggled.connect(self.view.reset)
        self.actual_size_button.triggered.connect(self.actual_size)
        self.browser_button.triggered.connect(self.browser)
        self.save_tags_button.clicked.connect(self.save_tags)
        self.view.got_rect.connect(self.set_rect)

        self.crop_rect = QRect(QPoint(0, 0), QSize(0, 0))
        self.dir_now = os.getcwd()
        self.files = []
        self.index = 0
        self.refresh_files()
        self.pixmap_is_scaled = False
        self.pixmap = QGraphicsPixmapItem()
        self.active_tag = ''
        self.reset_browser = False
        self.txt = PngInfo()

    def set_rect(self, rect: tuple[QPointF, QPointF]):
        """Converts the crop rectangle to a QRect after a crop action"""
        self.crop_rect = QRect(rect[0].toPoint(), rect[1].toPoint())

    def keyPressEvent(self, event: QKeyEvent): # pylint: disable=invalid-name;
        """Keyboard event handler."""
        if event.key() == Qt.Key_Escape and self.play_button.isChecked():
            self.play_button.toggle()
            self.browser_button.setChecked((True, False)[self.reset_browser])
        elif (event.key() in [16777220, 16777221] and
              self.view.g_rect.rect().width() > 0):
            self.view.got_rect.emit((self.view.g_rect.rect().topLeft(),
                                      self.view.g_rect.rect().bottomRight()))
            if self.view.g_rect.pen().color() == Qt.red:
                new_pix = self.pixmap.pixmap().copy(self.crop_rect)
                if self.pixmap_is_scaled:
                    new_pix = new_pix.transformed(
                        self.view.transform().inverted()[0],
                        Qt.SmoothTransformation)
                self.update_pixmap(new_pix)
            elif self.view.g_rect.pen().color() == Qt.magenta:
                self.annotate_rect()
                self.view.annotation = False
            for _ in (self.label, self.save_button, self.no_save_button):
                _.show()
            self.view.reset()

    def play(self):
        """Starts a slideshow."""
        if self.play_button.isChecked():
            if self.browser_button.isChecked():
                self.reset_browser = True
            else:
                self.reset_browser = False
            QTimer.singleShot(3000, self.play)
            self.next()

    def _yield_radio(self):
        """Saves code connecting signals from all the radio buttons."""
        yield from self.radios.keys().__str__()

    def load_icon(self, icon_file):
        """Loads an icon from Base64 encoded strings in icons.py."""
        pix = QPixmap()
        pix.loadFromData(icon_file)
        return QIcon(pix)

    def open_file(self, file: str) -> None:
        """
        Open an image file and display it.

        :param file: The filename of the image to open
        """
        if not os.path.isfile(file):
            file = QFileDialog(self, self.dir_now,
                               self.dir_now).getOpenFileName()[0]
            self.dir_now = os.path.dirname(file)
            self.refresh_files()
        for i, index_file in enumerate(self.files):
            if file.split('/')[-1] == index_file:
                self.index = i
        self.view.setTransform(QTransform())
        self.update_pixmap(QPixmap(file))
        self.browser()
        self.load_tags()

    def refresh_files(self) -> list[str]:
        """Updates the file list when the directory is changed.
        Returns a list of image files available in the current directory."""
        files = os.listdir(self.dir_now)
        self.files = [file
            for file in sorted(files, key=lambda x: x.lower())
            if file.endswith((".png", ".jpg", ".gif", ".bmp", ".jpeg"))]

    def next(self) -> None:
        """Opens the next image in the file list."""
        self.index = (self.index + 1) % len(self.files)
        self.reload()

    def previous(self) -> None:
        """Opens the previous image in the file list."""
        self.index = (self.index + (len(self.files) - 1)) % len(self.files)
        self.reload()

    def save_image(self) -> None:
        """
        Save the modified image file.  If the current pixmap has been
        scaled, we need to load a non-scaled pixmap from the original file and
        re-apply the transformations that have been performed to prevent it
        from being saved as the scaled-down image.
        """
        if self.pixmap_is_scaled:
            rotation = self.pixmap.rotation()
            mirror = self.pixmap.scale() < 0
            pix = QPixmap(self.files[self.index])
            pix = pix.transformed(QTransform().rotate(rotation))
            if mirror:
                pix = pix.transformed(QTransform().scale(-1, 1))
            pix.save(self.files[self.index], quality=-1)
        else:
            self.pixmap.pixmap().save(self.files[self.index], quality=-1)
        self.save_tags()

    def delete(self) -> None:
        """Deletes the current image from the file system."""
        with suppress(OSError):
            os.remove(f"{self.dir_now}/{self.files.pop(self.index)}")
        self.refresh_files()

    def reload(self) -> None:
        """Reloads the current pixmap; used to update the screen when the
        current file is changed."""
        self.open_file(f"{self.dir_now}/{self.files[self.index]}")

    def annotate(self, tag):
        """Starts an annotate action"""
        self.txt = PngInfo()
        self.view.annotation = True
        self.active_tag = tag
        self.view.reset()

    def wheelEvent(self, event: QWheelEvent) -> None: # pylint: disable=invalid-name
        """With Ctrl depressed, zoom the current image, otherwise fire the
        next/previous functions."""
        modifiers = QApplication.keyboardModifiers()
        if event.angleDelta().y() == 120 and modifiers == Qt.ControlModifier:
            self.view.scale(0.75, 0.75)
        elif event.angleDelta().y() == 120:
            self.previous()
        elif event.angleDelta().y() == -120 and modifiers == Qt.ControlModifier:
            self.view.scale(1.25, 1.25)
        elif event.angleDelta().y() == -120:
            self.next()

    def actual_size(self) -> None:
        """Display the current image at its actual size, rather than scaled to
        fit the viewport."""
        self.update_pixmap(QPixmap(self.files[self.index]), False)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event: QMouseEvent) -> None: # pylint: disable=invalid-name
        """Event handler for mouse button presses."""
        if event.button() == Qt.MouseButton.ForwardButton:
            self.next()
        elif event.button() == Qt.MouseButton.BackButton:
            self.previous()

    def update_pixmap(self, new: QPixmap, scaled: bool = True) -> None:
        """
        Updates the currently displayed image.

        :param new: The new `QPixmap` to be displayed.
        :param scaled: If False, don't scale the image to fit the viewport.
        """
        self.pixmap_is_scaled = scaled
        self.media.clear()
        self.pixmap = self.media.addPixmap(new)
        self.pixmap.setTransformOriginPoint(
            self.pixmap.boundingRect().width() / 2,
            self.pixmap.boundingRect().height() / 2)
        if scaled and (new.size().width() > self.view.width() or
            new.size().height() > self.view.height()):
            self.view.fitInView(self.pixmap, Qt.KeepAspectRatio)
        self.media.setSceneRect(self.pixmap.boundingRect())

    def annotate_rect(self):
        """Creates image coordinate annotation data."""
        self.txt.add_itxt(f'{str(self.active_tag)}-rect',
                          f'{str(self.crop_rect.x())}, {str(self.crop_rect.y())}, {str(self.crop_rect.width())}, {str(self.crop_rect.height())}')


    def browser(self):
        """Slot function to initialize image thumbnails for the
        'browse mode.'"""
        while self.h_box2.itemAt(0):
            self.h_box2.takeAt(0).widget().deleteLater()
        index = (self.index + (len(self.files) - 2)) % len(self.files)
        for i, file in enumerate(self.files):
            file = self.dir_now + '/' + self.files[index]
            label = ClickableLabel(self, file)
            self.h_box2.addWidget(label)
            pix = QPixmap(file)
            if (pix.size().width() > self.browse_bar.width() / 5 or
                pix.size().height() > 100):
                pix = pix.scaled(self.browse_bar.width() / 5, 100, Qt.KeepAspectRatio)
            label.setPixmap(pix)
            index = (index + 1) % len(self.files)
            if i == 4:
                break

    def save_tags(self):
        """Save tags for currently loaded image into its iTxt data."""
        file = self.files[self.index]
        img = Image.open(file)
        img.load()
        for key, value, in img.text.items():
            self.txt.add_itxt(key, value)
        for key in self.radios:
            if key.isChecked():
                self.txt.add_itxt(self.radios[key]['this'], 'True')
                self.txt.add_itxt(self.radios[key]['that'], 'False')
        img.save(file, pnginfo=self.txt)

    def load_tags(self):
        """Load tags from iTxt data."""
        for radio in self.radios:
            if radio.isChecked():
                self.radios[radio]['reset'].setChecked(True)
        filename = self.files[self.index]
        fqp = filename
        img = Image.open(fqp)
        img.load()
        with suppress(AttributeError):
            for key, value in img.text.items():
                if value == 'True':
                    for radio in self.radios:
                        if key == self.radios[radio]['this']:
                            radio.setChecked(True)
                            self.view.annotation = False
                            self.active_tag = ''
                            self.view.reset()
            for key, value in img.text.items():
                if key.endswith('-rect'):
                    btn = [radio for radio in self.radios if
                           self.radios[radio]['this'] == key.split('-')[0]]
                    print(key, value)
                    if btn[0].isChecked():
                        coords = [int(coord) for coord in value.split(', ')]
                        rect = QGraphicsRectItem(*coords)
                        rect.setPen(QPen(Qt.magenta, 1, Qt.SolidLine))
                        rect.setBrush(QBrush(Qt.magenta, Qt.Dense4Pattern))
                        self.view.scene().addItem(rect)
                        text = self.view.scene().addText(
                            key.split('-')[0], QFont('monospace',
                                                     20, 400, False))
                        text.font().setPointSize(text.font().pointSize() * 2)
                        text.update()
                        text.setX(rect.rect().x() + 10)
                        text.setY(rect.rect().y() + 10)
                        print(f'set {key}')


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
