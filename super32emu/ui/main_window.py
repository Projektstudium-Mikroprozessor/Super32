"""python emulator"""
import os

from PySide2.QtWidgets import QAction, QFileDialog, QMainWindow
from PySide2.QtGui import QIcon, Qt, QKeySequence
from PySide2.QtCore import Slot
from super32utils.inout.fileio import FileIO
from super32utils.inout.fileio import ResourceManager
from logic.emulator import Emulator
from .editor_widget import EditorWidget
from .emulator_widget import EmulatorDockWidget
from .footer_widget import FooterDockWidget


class MainWindow(QMainWindow):
    """This is the main window that holds the menu, the toolbar and the main widget"""

    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle("Super32 Emulator")
        self.start_path = '.'
        self.saved_path = '.'

        self.__create_menu()
        self.__create_toolbar()

        self.editor_widget = EditorWidget()
        self.emulator_dock_widget = EmulatorDockWidget()
        self.footer_dock_widget = FooterDockWidget()

        self.setCentralWidget(self.editor_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.emulator_dock_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.footer_dock_widget)

        self.emulator = Emulator(
            self.editor_widget,
            self.emulator_dock_widget.emulator,
            self.footer_dock_widget.footer
        )

    def __create_menu(self):
        menu_bar = self.menuBar()

        # file menu
        file_menu = menu_bar.addMenu("File")
        new_action = QAction(self.tr("New"), self)
        new_action.setShortcut(QKeySequence.New)
        open_action = QAction(self.tr("Open..."), self)
        open_action.setShortcut(QKeySequence.Open)
        save_action = QAction(self.tr("Save"), self)
        save_action.setShortcut(QKeySequence.Save)
        saveas_action = QAction(self.tr("SaveAs"), self)
        saveas_action.setShortcut(QKeySequence.SaveAs)
        quit_action = QAction(self.tr("Quit"), self)
        quit_action.setShortcut(QKeySequence.Quit)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(saveas_action)
        file_menu.addAction(quit_action)

        # edit menu
        edit_menu = menu_bar.addMenu(self.tr("Edit"))
        edit_menu.addAction(self.tr("Copy"))
        edit_menu.addAction(self.tr("Paste"))

        # help menu
        help_menu = menu_bar.addMenu(self.tr("Help"))
        help_menu.addAction(self.tr("Info"))

        # add slots
        new_action.triggered.connect(self.__new)
        open_action.triggered.connect(self.__open)
        save_action.triggered.connect(self.__save)
        saveas_action.triggered.connect(self.__saveas)
        quit_action.triggered.connect(self.__quit)

    def __create_toolbar(self):
        tb_open = QAction(QIcon("resources/open.png"), self.tr("Open"), self)
        tb_save = QAction(QIcon("resources/save.png"), self.tr("Save"), self)
        tb_save = QAction(QIcon("resources/save.png"), self.tr("SaveAs"), self)
        tb_run = QAction(QIcon("resources/run.png"), self.tr("Run"), self)
        tb_step = QAction(QIcon("resources/step.png"), self.tr("Step"), self)
        tb_debug = QAction(QIcon("resources/debug.png"),
                           self.tr("Debug"), self)
        tb_mcode = QAction(QIcon("resources/mcode.png"), self.tr("Show Code"), self)
        tb_separator = QAction("", self)
        tb_separator.setSeparator(True)

        tb_open.triggered.connect(self.__open)
        tb_save.triggered.connect(self.__save)
        tb_run.triggered.connect(self.__run)
        tb_mcode.triggered.connect(self.__mcode)

        tool_bar = self.addToolBar("Toolbar")
        tool_bar.addAction(tb_open)
        tool_bar.addAction(tb_save)
        tool_bar.addAction(tb_separator)
        tool_bar.addAction(tb_run)
        tool_bar.addAction(tb_debug)
        tool_bar.addAction(tb_step)
        tool_bar.addAction(tb_mcode)

    @Slot()
    def __new(self):
        template = ""
        with ResourceManager("resources/template.s32", "r") as file:
            template = file.read()
        self.editor_widget.new_tab(content=template)

    @Slot()
    def __open(self):
        """Opens a file dialog to open a file"""
        (path, selected_filter) = QFileDialog.getOpenFileName(
            self,
            self.tr('Open File'),
            self.start_path,
            self.tr('Super32 Assembler Files (*.s32)')
        )
        self.start_path = '/'.join(path.split('/')[:-1])
        if path:
            content = FileIO.read_file(path)
            self.saved_path = path
            filename = path.split('/')[-1]
            self.editor_widget.new_tab(title=filename, content=content)

    @Slot()
    def __save(self):
        if self.saved_path != '.':
            content = self.editor_widget.tabs.currentWidget().toPlainText()
            FileIO.write(self.saved_path, content)
        else:
            self.__saveas()

    @Slot()
    def __saveas(self):
        """Opens a file dialog to save a file"""
        (path, selected_filter) = QFileDialog.getSaveFileName(self,
                                                              'Save File',
                                                              '.',
                                                              'Super32 Assembler Files (*.s32)')
        if path:
            content = self.editor_widget.tabs.currentWidget().toPlainText()
            self.saved_path = path
            FileIO.write(path, content)

    @Slot()
    def __mcode(self):
        if self.saved_path != '.':
            self.__save()
            os.system('python ../super32assembler/super32assembler.py parse --output=mcode.txt ' + self.saved_path)
            os.system("notepad.exe mcode.txt")

    @Slot()
    def __quit(self):
        self.close()

    @Slot()
    def __run(self):
        """Runs the emulator"""
        self.emulator.run()
