"""Custom QT Widget for displaying and editing images"""
from __future__ import annotations
from contextlib import suppress

import os

from PIL import Image
from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal # pylint: disable=no-name-in-module
from PySide6.QtGui import (QPixmap, QTransform, QPainter, QPen, QResizeEvent, # pylint: disable=no-name-in-module
    QWheelEvent, QMouseEvent, QPaintEvent) # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QFileDialog, QLabel, QApplication, QWidget # pylint: disable=no-name-in-module

class MediaLabel(QLabel):
    """Custom image viewer/editor widget"""
    reloaded = Signal()

    def __init__(self, parent: QWidget) -> None:
        super(MediaLabel, self).__init__('', parent)
        self.mouse_pos = QPoint(0, 0)
        self.mouse_down = False
        self.crop_rect = QRect(QPoint(0, 0), QSize(0, 0))
        self.crop_started = False
        self.dir_now = os.getcwd()
        self.files = self.refresh_files()
        self.index = 0
        self.dirty = False
        self.filename = self.files[self.index]
        self.delta_x = 0
        self.delta_y = 0
        self.view_rect = self.contentsRect()
        self.offset: QPoint = QPoint(0, 0)

    def open_file(self, file: str) -> None:
        """
        Open an image file and display it.

        :param file: The filename of the image to open
        """
        if not os.path.isfile(file):
            file = QFileDialog(self, self.dir_now,
                               self.dir_now).getOpenFileName()[0]
        if os.path.dirname(file) != self.dir_now:
            self.dir_now = os.path.dirname(file)
            self.files = self.refresh_files()
            for i, index_file in enumerate(self.files):
                if file == index_file:
                    self.index = i
        new_pix = QPixmap(file)
        self.filename = file
        self.update_pixmap(new_pix)
        self.reloaded.emit() #type: ignore

    def scale_to_fit(self, new_pix: QPixmap) -> QPixmap:
        """
        Scales a given pixmap to fit the viewport.  Returns the scaled pixmap
        or the original pixmap if scaling isn't necessary.

        :param new_pix: The `QPixmap` to be scaled.
        """
        if (new_pix.size().width() <= self.size().width()
            and new_pix.size().height() <= self.size().height()):
            return new_pix
        if (max(new_pix.size().width(), new_pix.size().height())
                == new_pix.size().width()):
            return new_pix.scaledToWidth(self.contentsRect().width(),
                                         Qt.SmoothTransformation)
        else:
            return new_pix.scaledToHeight(self.contentsRect().height(),
                                          Qt.SmoothTransformation)

    def refresh_files(self) -> list[str]:
        """Updates the file list when the directory is changed.
        Returns a list of image files available in the current directory."""
        files = os.listdir(self.dir_now)
        return [
            file
            for file in sorted(files, key=lambda x: x.lower())
            if file.endswith((".png", ".jpg", ".gif", ".bmp", ".jpeg"))
        ]

    def resizeEvent(self, event: QResizeEvent) -> None: # pylint: disable=unused-argument, invalid-name
        """Updates the geometry of the widget and reloads the current pixmap
        when the widget gets resized."""
        self.updateGeometry()
        self.reload()

    def next(self) -> None:
        """Opens the next image in the file list."""
        self.index = (self.index + 1) % len(self.files)
        self.reload()

    def previous(self) -> None:
        """Opens the previous image in the file list."""
        self.index = (self.index + (len(self.files) - 1)) % len(self.files)
        self.reload()

    def mirror(self) -> None:
        """Mirros the current image and prompts the user to save the modified
        file."""
        new_pix = self.pixmap().transformed(QTransform().scale(-1, 1)) # type: ignore
        self.dirty = True
        self.update_pixmap(new_pix)

    def reload(self) -> None:
        """Reloads the current pixmap; used to update the screen when the
        current file is changed."""
        self.open_file(f"{self.dir_now}/{self.files[self.index]}")

    def save_image(self) -> None:
        """Save the modified image file."""
        # TODO: make this work
        if self.dirty is True:
            self.dirty = False

    def rotate_right(self) -> None:
        """Rotate the current image 90 degrees to the right and prompts the
        user to save the modified image."""
        new_pix = self.pixmap().transformed(QTransform().rotate(90)) #type: ignore
        self.dirty = True
        self.update_pixmap(new_pix)

    def rotate_left(self) -> None:
        """Rotate the current image 90 degrees to the left and prompts the
        user to save the modified image."""
        new_pix = self.pixmap().transformed(QTransform().rotate(-90)) #type: ignore
        self.dirty = True
        self.update_pixmap(new_pix)

    def delete(self) -> None:
        """Deletes the current image from the file system."""
        with suppress(OSError):
            os.remove(f"{self.dir_now}/{self.files.pop(self.index)}")
        self.refresh_files()
        self.filename = self.files[self.index]
        self.reload()

    def crop(self) -> None:
        """Starts a crop action"""
        # TODO: make this work
        self.crop_started = True

    def wheelEvent(self, event: QWheelEvent) -> None: # pylint: disable=invalid-name
        """With Ctrl depressed, zoom the current image, otherwise fire the
        next/previous functions."""
        modifiers = QApplication.keyboardModifiers()
        if event.angleDelta().y() == 120 and modifiers == Qt.ControlModifier:
            new_pix = self.pixmap().transformed(QTransform().scale(0.75, 0.75)) # type: ignore
            self.update_pixmap(new_pix)
        elif event.angleDelta().y() == 120:
            self.previous()
        elif event.angleDelta().y() == -120 and modifiers == Qt.ControlModifier:
            new_pix = self.pixmap().transformed(QTransform().scale(1.25, 1.25)) # type: ignore
            self.update_pixmap(new_pix)
        elif event.angleDelta().y() == -120:
            self.next()

    def mousePressEvent(self, event: QMouseEvent) -> None: # pylint: disable=invalid-name
        """Event handler for mouse button presses."""
        if event.button() == Qt.MouseButton.RightButton:
            self.crop()
        elif event.button() == Qt.MouseButton.ForwardButton:
            self.next()
        elif event.button() == Qt.MouseButton.BackButton:
            self.previous()
        self.mouse_pos = event.pos()
        if self.crop_started:
            self.crop_rect.setTopLeft(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # pylint: disable=invalid-name
        """Event handler for mouse movement events. Used to draw the cropping
        rectangle while a crop action is in progress."""
        if self.crop_started:
            self.crop_rect.setBottomRight(event.pos())
            self.update() # type: ignore

    def mouseReleasedEvent(self, event: QMouseEvent) -> None: # pylint: disable=invalid-name
        """Event handler for mouse button release events. Used to finalize the
        bounding box for a crop action."""
        if self.crop_started:
            self.crop_started = False
            self.crop_rect.setBottomRight(event.pos())
            self.update() # type: ignore

    def actual_size(self) -> None:
        """Display the current image at its actual size, rather than scaled to
        fit the viewport."""
        self.update_pixmap(QPixmap(self.filename), False)

    def update_pixmap(self, new: QPixmap, scaled: bool = True) -> None:
        """
        Updates the currently displayed image.

        :param new: The new `QPixmap` to be displayed.
        :param scaled: If False, don't scale the image to fit the viewport.
        """
        new_pix = self.scale_to_fit(new) if scaled else new
        self.delta_x = int((new_pix.width() - self.contentsRect().width()) / 2)
        self.delta_y = int((new_pix.height() - self.contentsRect().height()) / 2)
        self.view_rect = QRect(
            QPoint(self.delta_x, self.delta_y),
            QSize(self.contentsRect().width(), self.contentsRect().height()),
        )
        self.setPixmap(new_pix)

    def paintEvent(self, event: QPaintEvent): #pylint: disable=unused-argument, invalid-name
        """Fired when the view is repainted."""
        painter = QPainter(self)
        if self.delta_x < 0 or self.delta_y < 0:
            painter.drawPixmap(
                QPoint(abs(self.delta_x), abs(self.delta_y)), self.pixmap()) # type: ignore
        else:
            painter.drawPixmap(self.contentsRect(), self.pixmap()) # type: ignore
        if self.crop_rect.x() > 0:
            painter.setPen(QPen(Qt.red, 1, Qt.SolidLine)) # type: ignore
            painter.drawRect(self.crop_rect) # type: ignore
