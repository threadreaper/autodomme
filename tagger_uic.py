"""Image tagging application for generating annotations for AI training data
for nudity detection."""
import sys
from contextlib import suppress

from PIL import Image
from PIL.PngImagePlugin import PngInfo
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QSizePolicy # pylint: disable=no-name-in-module
from PySide6.QtGui import QPixmap, QMouseEvent, QIcon # pylint: disable=no-name-in-module
from PySide6.QtCore import QSize, Qt, QRect # pylint: disable=no-name-in-module

from tagger_ui import Ui_MainWindow
from icons import icon as bmp


class ClickableLabel(QLabel):
    """Custom class for a QLabel that responds to click events."""
    def __init__(self, parent, file):
        QLabel.__init__(self, parent)
        self.file = file
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy) # type: ignore
        self.setMinimumSize(QSize(0, 100)) # type: ignore
        self.setMaximumSize(QSize(16777215, 100)) # type: ignore
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignCenter)
        self.app = parent

    def mouseReleaseEvent(self, event: QMouseEvent) -> None: # pylint: disable=unused-argument, invalid-name
        """When this label is clicked, open the associated image file."""
        self.app.inter.media.open_file(self.file)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.inter = Ui_MainWindow()
        icon = QPixmap() # type: ignore
        icon.loadFromData(bmp.icon) # type: ignore
        app_icon = QIcon(icon)
        self.setWindowIcon(app_icon)
        self.setIconSize(QSize(32, 32))
        self.inter.setupUi(self)
        self.active_tag = ''
        self.button_groups = [self.inter.buttonGroup, self.inter.buttonGroup_2,
                              self.inter.buttonGroup_3, self.inter.expression,
                              self.inter.nudity]
        self.radios = {
            self.inter.ass: {'this': 'ass', 'that': 'assExposed',
                             'reset': self.inter.ass_reset},
            self.inter.assExposed: {'this': 'assExposed', 'that': 'ass',
                                    'reset': self.inter.ass_reset},
            self.inter.breasts: {'this': 'breasts', 'that': 'breastsExposed',
                                 'reset': self.inter.breasts_reset},
            self.inter.breastsExposed: {'this': 'breastsExposed',
                                        'that': 'breasts',
                                        'reset': self.inter.breasts_reset},
            self.inter.pussy: {'this': 'pussy', 'that': 'pussyExposed',
                               'reset': self.inter.pussy_reset},
            self.inter.pussyExposed: {'this': 'pussyExposed', 'that': 'pussy',
                                      'reset': self.inter.pussy_reset},
            self.inter.fullyClothed: {'this': 'fullyClothed',
                                      'that': 'fullyNude',
                                      'reset': self.inter.nudity_reset},
            self.inter.fullyNude: {'this': 'fullyNude', 'that': 'fullyClothed',
                                   'reset': self.inter.nudity_reset},
            self.inter.smiling: {'this': 'smiling', 'that': 'glaring',
                                 'reset': self.inter.expression_reset},
            self.inter.glaring: {'this': 'glaring', 'that': 'smiling',
                                 'reset': self.inter.expression_reset}
        }
        self.inter.actionOpen.triggered.connect(self.inter.media.open_file) # type: ignore
        self.inter.next.triggered.connect(self.inter.media.next) # type: ignore
        self.inter.previous.triggered.connect(self.inter.media.previous) # type: ignore
        self.inter.actionReload.triggered.connect(self.inter.media.reload) # type: ignore
        self.inter.actionMirror.triggered.connect(self.inter.media.mirror) # type: ignore
        self.inter.save_button.clicked.connect(self.inter.media.save_image) # type: ignore
        self.inter.actionRotate_Right.triggered.connect( # type: ignore
            self.inter.media.rotate_right)
        self.inter.actionRotate_left.triggered.connect(self.inter.media.rotate_left) # type: ignore
        self.inter.actionDelete.triggered.connect(self.inter.media.delete) # type: ignore
        self.inter.actionCrop.triggered.connect(self.inter.media.crop) # type: ignore
        self.inter.actionActual_Size.triggered.connect(self.inter.media.actual_size) # type: ignore
        self.inter.actionBrowser.triggered.connect(self.browser) # type: ignore
        self.inter.media.reloaded.connect(self.browser) # type: ignore
        self.inter.media.reloaded.connect(self.load_tags) # type: ignore
        self.inter.pushButton.clicked.connect(self.save_tags) # type: ignore
        self.inter.ass.toggled.connect(lambda: self.change_cursor('ass')) # type: ignore
        self.inter.assExposed.toggled.connect(lambda: self.change_cursor('assExposed')) # type: ignore
        self.inter.breasts.toggled.connect(lambda: self.change_cursor('breasts')) # type: ignore
        self.inter.breastsExposed.toggled.connect(lambda: self.change_cursor('breastsExposed')) # type: ignore
        self.inter.pussy.toggled.connect(lambda: self.change_cursor('pussy')) # type: ignore
        self.inter.pussyExposed.toggled.connect(lambda: self.change_cursor('pussyExposed')) # type: ignore
        self.inter.fullyClothed.toggled.connect(lambda: self.change_cursor('fullyClothed')) # type: ignore
        self.inter.fullyNude.toggled.connect(lambda: self.change_cursor('fullyNude')) # type: ignore
        self.inter.smiling.toggled.connect(lambda: self.change_cursor('smiling')) # type: ignore
        self.inter.glaring.toggled.connect(lambda: self.change_cursor('glaring')) # type: ignore
        self.inter.media.annotate_rect.connect(self.annotation) # type: ignore

    def change_cursor(self, sender):
        """Changes the cursor when the user applies an annotation requiring
        position data."""
        self.active_tag = sender
        self.setCursor(Qt.CrossCursor)
        self.inter.media.annotate()

    def annotation(self, rect: QRect):
        txt = PngInfo()
        txt.add_itxt(self.active_tag, str(rect.x()), str(rect.y()), str(rect.width()), str(rect.height()))
        print(self.active_tag, str(rect.x()), str(rect.y()), str(rect.width()), str(rect.height()))

    def browser(self):
        """Slot function to initialize image thumbnails for the
        'browse mode.'"""
        while self.inter.horizontalLayout.itemAt(0):
            self.inter.horizontalLayout.takeAt(0).widget().deleteLater()
        files = self.inter.media.files
        index = (self.inter.media.index + (len(files) - 2)) % len(files)
        for i, file in enumerate(files):
            file = self.inter.media.dir_now + '/' + files[index]
            new_label = ClickableLabel(self, file)
            self.inter.horizontalLayout.addWidget(new_label)
            size = new_label.size
            pix = QPixmap(file)
            if pix.size().width() > size().width() or pix.size().height() > size().height():
                if pix.size().height() > 100:
                    new_label.setPixmap(pix.scaledToHeight(100))
                elif pix.size().width() > pix.size().height():
                    new_label.setPixmap(pix.scaledToWidth(size().width()))
            else:
                new_label.setPixmap(pix)
            index = (index + 1) % len(files)
            if i == 4:
                break

    def save_tags(self):
        """Save tags for currently loaded image into its iTxt data."""
        file = self.inter.media.filename
        img = Image.open(file)
        img.load()
        txt = PngInfo()
        with suppress(AttributeError):
            for key, value, in img.text.items(): # type: ignore
                txt.add_itxt(key, value)
        for key in self.radios:
            if key.isChecked():
                txt.add_itxt(self.radios[key]['this'], 'True')
                txt.add_itxt(self.radios[key]['that'], 'False')
        img.save(file, pnginfo=txt)

    def load_tags(self):
        """Load tags from iTxt data."""
        for radio in self.radios:
            if radio.isChecked():
                self.radios[radio]['reset'].setChecked(True)
        filename = self.inter.media.filename
        fqp = filename
        img = Image.open(fqp)
        img.load()
        with suppress(AttributeError):
            for key, value in img.text.items(): # type: ignore
                if value == 'True':
                    for radio in self.radios:
                        if key == self.radios[radio]['this']:
                            radio.setChecked(True)


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec_())
