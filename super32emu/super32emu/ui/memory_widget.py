from PySide2.QtGui import QTextOption

from .code_editor import *
from .ui_style import UiStyle


class MemoryWidget(LineNumberEditor):
    """
    Like CodeEditor, but...

    ...with different line numbering
    ...read-only

    https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    """

    def __init__(self):
        super().__init__()

        # Used to remember the position to which the user scrolled
        self.scrollBarValue = 0

        self.setReadOnly(True)
        self.setWordWrapMode(QTextOption.NoWrap)

        # TODO Multiplying by the actual line character count (42)
        #   results in a horizontal scrollbar when a vertical scrollbar is present.
        #   Workaround by multiplying with a "magical number" (48).
        metrics = QFontMetrics(UiStyle.get_font())
        text_width = metrics.width('0') * (42 + 6)
        self.setFixedWidth(text_width)

        self.connect(self.verticalScrollBar(), SIGNAL('sliderMoved(int)'), self.storeScrollBarValue)

    def storeScrollBarValue(self, value: int):
        self.scrollBarValue = value

    def setPlainText(self, text: str):
        super(MemoryWidget, self).setPlainText(text)

        # Restore vertical scroll position
        self.verticalScrollBar().setValue(self.scrollBarValue)
        
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()

        # Each line contains four bytes
        blockNumber = block.blockNumber() * 4

        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = hex(blockNumber)[2:].upper()
                painter.setPen(Qt.black)
                painter.setFont(UiStyle.get_font())
                painter.drawText(0, top, self.lineNumberArea.width(), height,
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()

            # Start of next line is four bytes apart from previous line start
            blockNumber += 4
