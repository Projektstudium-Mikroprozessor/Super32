"""python emulator"""
from PySide2.QtWidgets import QDockWidget, QGridLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget, QPlainTextEdit, QFormLayout, QLabel, QSizePolicy
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QIcon, QFont
from .register_widget import RegisterWidget
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

        for i in range(32):
            r = RegisterWidget('R' + str(i))
            self.register.append(r)

        current_register = 0

        for x in range(8):
            for y in range(4):
                r = self.register[current_register]
                self.register_layout.addWidget(r, x, y, Qt.AlignRight)
                current_register += 1

        self.program_counter = RegisterWidget("PC")
        self.register_layout.addWidget(self.program_counter, 9, 3, alignment=Qt.AlignRight)

        self.register_group.setLayout(self.register_layout)

    def __create_storage_group(self):
        self.storage = QPlainTextEdit()
        self.storage.setFont(QFont('Fira Code', 8, QFont.Medium))

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
        self.symbol_layout.addRow(self.tr("Address"), symbol)

    def set_register(self, index, value):
        """Sets the value of a register chosen by its index"""
        if index < 0 or index > 32:
            raise Exception('Register out of index')

        self.register[index].set_value(str(value))

    def set_pc(self, value):
        """Sets the value of the program counter"""

        self.program_counter.set_value(str(value))

    def set_storage(self, value):
        """Sets the value of the storage"""

        self.storage.setPlainText(str(value))

    def set_symbols(self, symboltable: dict):
        """Fills the symboltable with parsed labels and addresses"""

        for index in range(1, self.symbol_layout.rowCount()):
            self.symbol_layout.removeRow(index)

        font = QFont('Fira Code', 8, QFont.Medium)
        for entry in symboltable:
            symbol = QLineEdit()
            symbol.setReadOnly(True)
            symbol.setText(entry)
            symbol.setFont(font)
            address = QLineEdit()
            address.setReadOnly(True)
            address.setFont(font)
            address.setText(str(symboltable[entry]))
            self.symbol_layout.addRow(address, symbol)
