from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QSize


class LineNumberArea(QWidget):
    """
    https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    """

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return Qsize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)
