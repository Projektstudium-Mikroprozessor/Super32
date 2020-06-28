from .code_editor import *
from PySide2.QtGui import QFont, QTextOption
from PySide2.QtGui import QTextCursor


class MemoryWidget(CodeEditor):
    """
    Like CodeEditor, but...

    ...with different line numbering
    ...read-only

    https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    """

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.extraSelections = []

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
                painter.setFont(QFont('Fira Code', 8, QFont.Medium))
                painter.drawText(0, top, self.lineNumberArea.width(), height,
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()

            # Start of next line is four bytes apart from previous line start
            blockNumber += 4

    def resetHighlightedMemoryLines(self):
        self.extraSelections = []

    def highlightMemoryLine(self, line_number: int, color=Qt.yellow):
        lineColor = QColor(color)

        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = QTextCursor(self.document().findBlockByLineNumber(line_number))
        selection.cursor.clearSelection()
        self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)
