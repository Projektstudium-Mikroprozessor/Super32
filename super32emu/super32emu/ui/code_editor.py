from .line_number_editor import LineNumberEditor
from PySide2.QtCore import SIGNAL, QRect, QObject
from PySide2.QtGui import QColor, Qt, QTextFormat, QPainter, QMouseEvent
from PySide2.QtCore import SIGNAL, QRect
from PySide2.QtGui import QColor, Qt, QTextFormat, QPainter, QTextCursor
from PySide2.QtWidgets import QPlainTextEdit, QTextEdit


class CodeEditor(LineNumberEditor):
    """
    Editor with line numbers and break points

    https://github.com/eyllanesc/stackoverflow/tree/master/questions/46327656
    """

    def __init__(self):
        super(CodeEditor, self).__init__(20)
        self.lineNumberArea.mouseReleaseEvent = self.onClicked
        self.breakpoints = []

        self.connect(self, SIGNAL('blockCountChanged(int)'), self.updateLineNumberAreaWidth)
        self.connect(self, SIGNAL('updateRequest(QRect,int)'), self.updateLineNumberArea)
        self.connect(self, SIGNAL('cursorPositionChanged()'), self.highlightCurrentLine)

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
        space = 3 + self.fontMetrics().width('9') * digits
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
        width_circle = 10
        painter = QPainter(self.lineNumberArea)
        painter.setBrush(Qt.red)
        painter.setPen(Qt.black)

        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()

        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):

                if blockNumber in self.breakpoints:
                    ellipse_center = top + (self.fontMetrics().height() - width_circle) / 2
                    painter.drawEllipse(0, ellipse_center, width_circle, width_circle)

                number = str(blockNumber + 1)
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def onClicked(self, event: QMouseEvent):
        block = self.firstVisibleBlock()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        mousePosY = event.y()

        blockNumber = block.blockNumber()

        while block.isValid():
            if block.isVisible() and top < mousePosY < bottom:

                if blockNumber in self.breakpoints:
                    self.breakpoints.remove(blockNumber)
                else:
                    self.breakpoints.append(blockNumber)
                self.update()
                return

            blockNumber += 1
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()

    def resetHighlightedLines(self):
        self.extraSelections = []
        self.setExtraSelections(self.extraSelections)

    def highlightLine(self, line_number: int, color=Qt.yellow):
        lineColor = QColor(color)

        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = QTextCursor(self.document().findBlockByLineNumber(line_number))
        selection.cursor.clearSelection()
        self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)
