"""python emulator"""
from PySide2.QtWidgets import QDockWidget, QGridLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QPlainTextEdit, QFormLayout, QLabel, QSizePolicy
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QIcon, QFont
from .register_widget import RegisterWidget
from .memory_widget import *
import os


class EmulatorDockWidget(QDockWidget):
    """Dockable emulator widget"""

    def __init__(self):
        QDockWidget.__init__(self)

        self.emulator = EmulatorWidget()
        self.setWindowTitle(self.tr("Hardware-Monitor"))
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        self.setStyleSheet(
            """
            QDockWidget {
                border: 1px solid lightgray;
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(undock.png);
            }

            QDockWidget::title {
                background: lightgray;
            }

            QDockWidget::close-button, QDockWidget::float-button {
                border: 1px solid transparent;
                background: white;
                padding: 0px;
            }

            QDockWidget::close-button:hover, QDockWidget::float-button:hover {
                background: gray;
            }

            QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {
                padding: 1px -1px -1px 1px;
            }
            """
        )

        self.setWidget(self.emulator)


class EmulatorWidget(QWidget):
    """Emulator widget"""

    def __init__(self):
        QWidget.__init__(self)

        self.register_group = QGroupBox(self.tr("Register"))
        self.storage_group = QGroupBox(self.tr("Storage"))
        self.symbol_group = QGroupBox(self.tr("Symboltable"))

        layout = QGridLayout()
        layout.addWidget(self.register_group, 0, 0, 1, 2)
        layout.addWidget(self.storage_group, 1, 0)
        layout.addWidget(self.symbol_group, 1, 1)
        layout.setSizeConstraint(layout.SetMaximumSize)

        self.setLayout(layout)

        self.__create_register_group()
        self.__create_storage_group()
        self.__create_symbol_group()

    def __create_register_group(self):
        self.index = 0
        self.register = []
        self.register_layout = QGridLayout()

        for i in range(30):
            r = RegisterWidget('R' + str(i))
            self.register.append(r)
        self.register.append(RegisterWidget('R30', 0))
        self.register.append(RegisterWidget('R31', 1))

        current_register = 0

        for x in range(8):
            for y in range(4):
                r = self.register[current_register]
                self.register_layout.addWidget(r, x, y, Qt.AlignRight)
                current_register += 1

        self.z_register = RegisterWidget("Z", mask="B")
        self.register_layout.addWidget(self.z_register, 9, 2, alignment=Qt.AlignRight)

        self.program_counter = RegisterWidget("PC")
        self.register_layout.addWidget(self.program_counter, 9, 3, alignment=Qt.AlignRight)

        self.register_group.setLayout(self.register_layout)

    def __create_storage_group(self):
        self.storage = MemoryWidget()
        self.storage.setFont(UiStyle.get_font())

        storage_layout = QVBoxLayout()

        storage_layout.addWidget(self.storage)
        self.storage_group.setLayout(storage_layout)

    def __create_symbol_group(self):
        self.symbol_layout = QFormLayout()
        self.symbol_layout.setHorizontalSpacing(0)
        self.symbol_layout.setVerticalSpacing(0)
        self.symbol_layout.setLabelAlignment(Qt.AlignLeft)
        self.symbol_layout.setFieldGrowthPolicy(
            QFormLayout.AllNonFixedFieldsGrow)
        self.symbol_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.symbol_group.setLayout(self.symbol_layout)

        symbol = QLabel(self.tr("Symbol"))
        self.symbol_layout.addRow(self.tr("Value"), symbol)

    def get_register(self, index):
        """Sets the value of a register chosen by its index"""
        if index < 0 or index > 32:
            raise Exception('Register out of index')

        return self.register[index].get_value()

    def set_register_background(self, index, color = "white"):
        """Resets the register background color"""
        if index < 0 or index > 32:
            raise Exception('Register out of index')

        self.register[index].set_background_color(color)

    def set_register(self, index, value, highlight: bool = True):
        """Sets the value of a register chosen by its index"""
        if index < 0 or index > 32:
            raise Exception('Register out of index')

        self.register[index].set_value(str(value), highlight)

    def reset_all_register_backgrounds(self):
        for rindex in range(32):
            self.set_register_background(rindex)

    def reset_all_registers(self):
        for rindex in range(32):
            self.set_register(rindex, '00000000', False)

    def reset_pc_background(self):
        self.program_counter.set_background_color()

    def set_z(self, value, highlight: bool = True):
        """Sets the value of the program counter"""

        self.z_register.set_value(str(value), highlight=highlight, color="yellow", byte_count=1)

    def set_pc(self, value, highlight: bool = True):
        """Sets the value of the program counter"""

        self.program_counter.set_value(str(value), highlight=highlight, color="yellow")

    def set_storage(self, value):
        """Sets the value of the storage"""
        self.storage.setPlainText(self.__beautify_storage(value))

    def set_symbols(self, symboltable: dict):
        """Fills the symboltable with parsed labels and values"""

        num_rows = self.symbol_layout.rowCount()
        for _ in range(1, num_rows):
            self.symbol_layout.removeRow(1)

        font = UiStyle.get_font()

        for entry in symboltable:
            symbol = QLineEdit()
            symbol.setReadOnly(True)
            symbol.setText(entry)
            symbol.setFont(font)
            value = QLineEdit()
            value.setReadOnly(True)
            value.setFont(font)
            value.setText(str(symboltable[entry]))
            self.symbol_layout.addRow(value, symbol)

    def highlight_memory_line(self, line_number: int, color=Qt.yellow):
        self.storage.highlightLine(line_number, color)

    def reset_highlighted_memory_lines(self):
        self.storage.resetHighlightedLines()

    def __beautify_storage(self, value: str) -> str:
        """Makes the memory string more readable.

        Takes a string containing the memory content (0s and 1s)
        Inserts a newline after four bytes
        Inserts two blanks after a byte
        Inserts one blank after a nibble
        """
        bit_occurences = 0
        i = 0

        for char in value:
            i += 1

            if char == "0" or char == "1":
                bit_occurences += 1

            if not bit_occurences % 32:
                value = value[:i] + '\n' + value[i:]
                i += 1
            elif not bit_occurences % 8:
                value = value[:i] + '  ' + value[i:]
                i += 2
            elif not bit_occurences % 4:
                value = value[:i] + ' ' + value[i:]
                i += 1

        return value.strip()
