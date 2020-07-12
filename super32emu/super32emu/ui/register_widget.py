"""python emulator"""
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget
from PySide2.QtGui import QFont, QFontMetrics, Qt

from .ui_style import UiStyle


class RegisterWidget(QWidget):
    """Register widget"""

    def __init__(self, text, fixed_value=None, mask="HHHHHHHH"):
        QWidget.__init__(self)

        self.label = QLabel()

        if text:
            self.label.setText(text)

        self.text_input = QLineEdit()
        self.text_input.setInputMask(mask)
        self.text_input.setFont(UiStyle.get_font())
        self.text_input.setAlignment(Qt.AlignRight)
        text_width = QFontMetrics(self.text_input.font()).maxWidth() * 10
        self.text_input.setFixedWidth(text_width)

        self.__fixed = fixed_value
        if fixed_value is not None:
            self.text_input.setReadOnly(True)
        
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def set_text(self, text):
        """Set the text of the label"""
        self.label.setText(text)

    def set_background_color(self, color: str = "white"):
        self.text_input.setStyleSheet("background-color: " + color)

    def set_value(self, value: str, highlight: bool = True, color: str = "#00ff00", byte_count: int = 8):
        """Set the value of the register"""
        if self.__fixed is not None:
            value = str(self.__fixed)

        value = value.rjust(byte_count, '0')
        self.text_input.setText(value)

        if highlight:
            self.set_background_color(color)
        else:
            self.set_background_color("white")

    def get_value(self):
        return self.text_input.text()
