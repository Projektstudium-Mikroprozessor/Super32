from PySide2.QtCore import SIGNAL, QRect
from PySide2.QtGui import QColor, Qt, QTextFormat, QPainter, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit, QTextEdit
from .line_number_area import *


class LineNumberEditor(QPlainTextEdit):
    """
    Editor with line numbers

    https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    """
    def __init__(self, space_left=None):
        """
        space_left: Add more margin to the left of the line numbers
        """
        super().__init__()

        if space_left is None:
            self.space_left = 3
        else:
            self.space_left = space_left

        self.lineNumberArea = LineNumberArea(self)

        self.connect(self, SIGNAL('blockCountChanged(int)'), self.updateLineNumberAreaWidth)
        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.updateLineNumberArea)

        # It is necessary to calculate the line number area width when the editor is created
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        """
        The lineNumberAreaWidth() function calculates the width of the LineNumberArea widget.
        We take the number of digits in the last line of the editor and multiply that with the maximum width of a digit.
        """
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = self.space_left + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                                       rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        """
        When the size of the editor changes, we also need to resize the line number area
        """
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                              self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height,
                                   Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightLine(self, line_number: int):
        extraSelections = []
        lineColor = QColor(Qt.yellow)

        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = QTextCursor(self.document().findBlockByLineNumber(line_number))
        selection.cursor.clearSelection()
        extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
