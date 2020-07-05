"""python emulator"""
from PySide2.QtWidgets import QFrame, QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget
from PySide2.QtGui import QFont
from PySide2.QtCore import Slot

from .ui_style import UiStyle
from ..logic.highlighter import SyntaxHighlighter
from .code_editor import *


class EditorWidget(QWidget):
    """Editor widget"""

    tab_count = 0

    def __init__(self):
        QWidget.__init__(self)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(False)
        self.tabs.tabCloseRequested.connect(self.__on_close_tab)
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.__open_file_paths = []

    def new_tab(self, title="", content="") -> int:
        """Append new tab"""

        EditorWidget.tab_count += 1
        editor = CodeEditor()
        highlighter = SyntaxHighlighter(editor.document())

        editor.setFrameShape(QFrame.NoFrame)
        editor.setFont(UiStyle.get_font(point_size=12))
        editor.setPlainText(content)
        tab_index = self.tabs.addTab(
            editor,
            "Untitled-{tab_count}".format(tab_count=EditorWidget.tab_count)
        )

        if title:
            self.tabs.setTabText(tab_index, title)
        self.tabs.setCurrentIndex(tab_index)

        self.__open_file_paths.append(None)

        return tab_index

    def exists_file_path(self) -> bool:
        try:
            exists_file_path = self.__open_file_paths[self.tabs.currentIndex()] is not None
        except IndexError:
            exists_file_path = False

        return exists_file_path

    def get_file_path(self) -> str:
        return self.__open_file_paths[self.tabs.currentIndex()]

    def set_current_tab_file_path(self, path):
        self.__open_file_paths[self.tabs.currentIndex()] = path

    def set_new_tab_file_path(self, tab_index: int, path: str) -> bool:
        try:
            self.__open_file_paths[tab_index] = path
            return True
        except IndexError:
            return False

    def set_tab_title(self, title):
        tab_index = self.tabs.currentIndex()
        self.tabs.setTabText(tab_index, title)

    def get_plain_text(self):
        editor = self.tabs.currentWidget()
        return editor.toPlainText()

    def get_text(self):
        editor = self.tabs.currentWidget()
        return editor.toPlainText().split("\n")

    def is_breakpoint_set(self, line: int) -> bool:
        editor = self.tabs.currentWidget()
        return editor.is_breakpoint_set(line)

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
        self.__open_file_paths.pop(index)
