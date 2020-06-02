"""python emulator"""
from PySide2.QtWidgets import QDockWidget, QGridLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, \
    QWidget, QPlainTextEdit, QFormLayout, QLabel
from PySide2.QtCore import Qt, Slot, QTimer
from PySide2.QtGui import QIcon, QFont
from .register_widget import RegisterWidget


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

        for i in range(32):
            r = RegisterWidget('R' + str(i))
            self.register.append(r)

        self.register_layout = QHBoxLayout()
        self.register_layout.addWidget(self.register[self.index])
        self.register_layout.addWidget(self.register[self.index + 1])
        self.register_layout.addWidget(self.register[self.index + 2])
        self.register_layout.addWidget(self.register[self.index + 3])
        self.register_layout.addWidget(self.register[self.index + 4])
        self.register_layout.addWidget(self.register[self.index + 5])

        back = QPushButton()
        back.setIcon(QIcon("resources/back.png"))
        back.setFlat(True)
        back.clicked.connect(self.__previous_register)
        forth = QPushButton()
        forth.setIcon(QIcon("resources/forth.png"))
        forth.setFlat(True)
        forth.clicked.connect(self.__next_register)

        arrows_layout = QHBoxLayout()
        arrows_layout.addWidget(back)
        arrows_layout.addWidget(forth)

        register_arrows_layout = QHBoxLayout()
        register_arrows_layout.addLayout(self.register_layout)
        register_arrows_layout.addLayout(arrows_layout)
        register_arrows_layout.setAlignment(Qt.AlignTop)

        self.program_counter = RegisterWidget("PC")

        register_group_layout = QVBoxLayout()
        register_group_layout.addLayout(register_arrows_layout)
        register_group_layout.addWidget(self.program_counter)

        self.register_group.setLayout(register_group_layout)

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

    @Slot()
    def __next_register(self):
        if self.index == 26:
            return

        self.index += 1
        self.__update_register()

    @Slot()
    def __previous_register(self):
        if self.index == 0:
            return

        self.index -= 1
        self.__update_register()

    def __update_register(self):
        for i in reversed(range(self.register_layout.count())):
            self.register_layout.itemAt(i).widget().setParent(None)

        self.register_layout.addWidget(self.register[self.index])
        self.register_layout.addWidget(self.register[self.index + 1])
        self.register_layout.addWidget(self.register[self.index + 2])
        self.register_layout.addWidget(self.register[self.index + 3])
        self.register_layout.addWidget(self.register[self.index + 4])
        self.register_layout.addWidget(self.register[self.index + 5])

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
        oldstr = self.storage.toPlainText()
        newstr = ""
        self.storage.clear()
        if oldstr:
            for oldc, newc in zip(oldstr, value):
                if oldc != newc:
                    newc = "<span style=\" color:#ff0000;\" >" + newc + "</span>"
                newstr += newc
            self.storage.appendHtml(newstr)
            QTimer.singleShot(2000, self.reset_storage_color)
        else:
            self.storage.setPlainText(str(value))

    def reset_storage_color(self):
        storagestr = self.storage.toPlainText()
        self.storage.setPlainText(storagestr)


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
