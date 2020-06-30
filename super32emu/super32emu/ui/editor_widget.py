"""python emulator"""
from PySide2.QtWidgets import QFrame, QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget
from PySide2.QtGui import QFont
from PySide2.QtCore import Slot
from ..logic.highlighter import SyntaxHighlighter
from .code_editor import *


class EditorWidget(QWidget):
    """Editor widget"""

    tab_count = 0

    def __init__(self):
        QWidget.__init__(self)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.__on_close_tab)
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def new_tab(self, title="", content=""):
        """Append new tab"""

        EditorWidget.tab_count += 1
        editor = CodeEditor()
        highlighter = SyntaxHighlighter(editor.document())

        editor.setFrameShape(QFrame.NoFrame)
        editor.setFont(QFont("Fira Code", 10, QFont.Normal))
        editor.setPlainText(content)
        tab_index = self.tabs.addTab(
            editor,
            "Untitled-{tab_count}".format(tab_count=EditorWidget.tab_count)
        )

        if title:
            self.tabs.setTabText(tab_index, title)
        self.tabs.setCurrentIndex(tab_index)

    def get_plain_text(self):
        editor = self.tabs.currentWidget()
        return editor.toPlainText()

    def get_text(self):
        editor = self.tabs.currentWidget()
        return editor.toPlainText().split("\n")

    def editor_readonly(self, readonly: bool = True):
        editor = self.tabs.currentWidget()
        editor.setReadOnly(readonly)

    def highlight_line(self, line_number: int):
        editor = self.tabs.currentWidget()
        editor.highlightLine(line_number)

    def reset_highlighted_lines(self):
        editor = self.tabs.currentWidget()
        editor.resetHighlightedLines()

    @Slot()
    def __on_close_tab(self, index):
        """Close tab on button-press"""
        self.tabs.removeTab(index)
