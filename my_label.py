import os

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class MediaLabel(QLabel):
    def __init__(self, parent = None):
        super(MediaLabel, self).__init__(parent)
        self.mousePos = QPoint()
        self.mouseDown = False
        self.crop_rect = QRect()
        self.crop_started = False
        self.dir_now = os.getcwd()
        self.files = self.refresh_files()
        self.index = 0
        self.pix = QPixmap(self.contentsRect().width(), self.contentsRect().height())
        self.dirty = False
        self.filename = self.files[self.index]


    def open_file(self, file=None):
        if not os.path.isfile(file):
            file = QFileDialog(self, self.dir_now, self.dir_now).getOpenFileName()[0]
        if os.path.dirname(file) != self.dir_now:
            self.dir_now = os.path.dirname(file)
            self.files = self.refresh_files()
            for i, index_file in enumerate(self.files):
                if file == index_file:
                    self.index = i
        new_pix = QPixmap(file)
        self.filename = file
        self.setPixmap(self.pix)
        if new_pix.size().width() > self.size().width() or new_pix.size().height() > self.size().height():
            if max(new_pix.size().width(), new_pix.size().height()) == new_pix.size().width():
                self.setPixmap(new_pix.scaledToWidth(self.contentsRect().width(),
                                                    Qt.SmoothTransformation))
            else:
                self.setPixmap(new_pix.scaledToHeight(self.contentsRect().height(),
                                                    Qt.SmoothTransformation))
        else:
            self.setPixmap(new_pix)

    def refresh_files(self):
        files = os.listdir(self.dir_now)
        return [file for file in sorted(files, key=lambda x: x.lower())\
            if file.endswith(('.png', '.jpg', '.gif', '.bmp', '.jpeg'))]

    def next(self):
        if self.index < len(self.files) - 1:
            self.index += 1
            self.reload()

    def previous(self):
        if self.index > 0:
            self.index -= 1
            self.reload()

    def mirror(self):
        new_pix = self.pixmap().transformed(QTransform().scale(-1, 1))
        self.dirty = True
        self.setPixmap(new_pix)

    def reload(self):
        self.open_file(f'{self.dir_now}/{self.files[self.index]}')

    def save_image(self):
        if self.dirty is True:
            print(self.filename, self.filename.split('.')[-1].upper())
            self.dirty = False

    def rotate_right(self):
        new_pix = self.pixmap().transformed(QTransform().rotate(90))
        self.dirty = True
        self.setPixmap(new_pix)

    def rotate_left(self):
        new_pix = self.pixmap().transformed(QTransform().rotate(-90))
        self.dirty = True
        self.setPixmap(new_pix)

    def delete(self):
        os.remove(f'{self.dir_now}/{self.files.pop(self.index)}')
        self.refresh_files()
        self.filename = self.files[self.index]
        self.reload()

    def crop(self):
        self.crop_started = True

    def mousePressEvent(self, event):
        if not self.crop_started:
            self.mouseDown = True
            self.mousePos = event.pos()
            self.crop_rect.setTopLeft(self.mousePos)

    def mouseMoveEvent(self, event):
        if self.mouseDown and self.crop_started:
            self.crop_rect.setBottomRight(event.pos())
            self.repaint()

    def mouseReleasedEvent(self, event):
        if self.mouseDown and self.crop_started:
            self.mouseDown = False
            self.crop_started = False
            self.crop_rect.setBottomRight(event.pos())
            self.repaint()
"""
    def paintEvent(self, event):
        if self.crop_rect.x() > 0:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
            painter.drawRect(self.crop_rect)
"""
