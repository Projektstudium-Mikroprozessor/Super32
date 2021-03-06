"""python emulator"""
from PySide2.QtGui import QFontMetrics, Qt
from PySide2.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

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

        # TODO Multiplying by the actual line character count (8)
        #  does not set the width to allow for 8 characters.
        #  Workaround by multiplying with a "magical number" (9)
        metrics = QFontMetrics(self.text_input.font())
        text_width = metrics.width('0') * (8 + 1)
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

    def set_value(self, value: str, highlight: bool = True, color: str = "lightGray", byte_count: int = 8):
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
