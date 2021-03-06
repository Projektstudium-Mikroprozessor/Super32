from PySide2.QtCore import SIGNAL, QRect
from PySide2.QtGui import QMouseEvent, QFontMetrics, QKeyEvent
from PySide2.QtGui import Qt, QPainter

from .line_number_editor import LineNumberEditor
from .ui_style import UiStyle


class CodeEditor(LineNumberEditor):
    """
    Editor with line numbers and break points

    https://github.com/eyllanesc/stackoverflow/tree/master/questions/46327656
    """

    def __init__(self):
        super(CodeEditor, self).__init__(20)
        self.lineNumberArea.mouseReleaseEvent = self.onClicked
        self.breakpoints = []

        self.setFont(UiStyle.get_font(point_size=12))

        # It is necessary to calculate the line number area width when the editor is created
        self.updateLineNumberAreaWidth(0)

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Tab:
            tc = self.textCursor()
            tc.insertText("    ")
            return
        return super(CodeEditor, self).keyPressEvent(e)

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

    def is_breakpoint_set(self, line: int) -> bool:
        return line in self.breakpoints
