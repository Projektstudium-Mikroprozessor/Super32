from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, Qt
from PySide2.QtCore import QRegExp

from ..ui.ui_style import UiStyle


class SyntaxHighlighter(QSyntaxHighlighter):
    """Super32 Syntax-Highlighter"""

    def __init__(self, parent):
        super().__init__(parent)
        self.matches = []
        self.highlighting_rules = []

        # singlelinecomment definitions
        comment_format = QTextCharFormat()
        comment_format.setForeground(Qt.darkGreen)
        UiStyle.set_font_weight(comment_format)
        comment_pattern = QRegExp("'[^\n]*")
        self.highlighting_rules.append((comment_pattern, comment_format))

        # instruction definitions
        instruction_format = QTextCharFormat()
        instruction_format.setForeground(Qt.darkBlue)
        UiStyle.set_font_weight(instruction_format)
        instruction_pattern = QRegExp("\\b(SUB|ADD|AND|OR|NOR|BEQ|LW|SW)\\b")
        self.highlighting_rules.append(
            (instruction_pattern, instruction_format))

        # assembler directive definitions
        directive_format = QTextCharFormat()
        directive_format.setForeground(Qt.darkBlue)
        UiStyle.set_font_weight(directive_format)
        directive_pattern = QRegExp("\\b(ORG|START|END|DEFINE)\\b")
        self.highlighting_rules.append(
            (directive_pattern, directive_format))

        # label definitions
        label_format = QTextCharFormat()
        label_format.setForeground(Qt.darkCyan)
        UiStyle.set_font_weight(label_format)
        label_pattern = QRegExp("\\b[A-Za-z0-9_-]+:")
        self.highlighting_rules.append((label_pattern, label_format))

        # registers definitions
        register_format = QTextCharFormat()
        register_format.setForeground(Qt.darkMagenta)
        UiStyle.set_font_weight(register_format)
        register_pattern = QRegExp("\\bR[0-9]+")
        self.highlighting_rules.append((register_pattern, register_format))

    def highlightBlock(self, text):
        """Check textblock wether to highlight or not"""

        for (pattern, style) in self.highlighting_rules:
            index = pattern.indexIn(text)
            while index >= 0:
                self.matches.append(pattern.cap(1))
                length = pattern.matchedLength()
                self.setFormat(index, length, style)
                index = pattern.indexIn(text, index + length)
