"""python emulator"""
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget
from PySide2.QtGui import QFont


class RegisterWidget(QWidget):
    """Register widget"""

    def __init__(self, text):
        QWidget.__init__(self)

        self.label = QLabel()

        if text:
            self.label.setText(text)

        self.text_input = QLineEdit()
        self.text_input.setFixedWidth(55)
        self.text_input.setFont(QFont('Fira Code', 8, QFont.Medium))
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

    def __blink_color(self, color: str = "white"):
        self.text_input.setStyleSheet("background-color: " + color)

    def set_value(self, value: str, blink: bool = True):
        """Set the value of the register"""
        value = value.rjust(8, '0')
        self.text_input.setText(value)

        if blink:
            self.__blink_color("yellow")
            QTimer.singleShot(2000, self.__blink_color)

    def get_value(self):
        return self.text_input.text()
