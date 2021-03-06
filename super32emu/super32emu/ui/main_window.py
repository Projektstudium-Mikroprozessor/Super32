"""python emulator"""
import datetime
import os
from os.path import dirname, join, normpath

from PySide2.QtCore import Slot
from PySide2.QtGui import QIcon, Qt, QKeySequence
from PySide2.QtWidgets import QAction, QFileDialog, QMainWindow
from super32assembler.assembler.architecture import Architectures
from super32assembler.assembler.assembler import Assembler
from super32assembler.generator.generator import Generator
from super32assembler.preprocessor.preprocessor import Preprocessor
from super32utils.inout.fileio import FileIO
from super32utils.inout.fileio import ResourceManager

from .editor_widget import EditorWidget
from .emulator_widget import EmulatorDockWidget
from ..logic.emulator import Emulator


class MainWindow(QMainWindow):
    """This is the main window that holds the menu, the toolbar and the main widget"""

    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle("Super32 Emulator")

        self.resources_dir = normpath(join(dirname(__file__), '..', 'resources'))
        self.path_to_instructionset = normpath(join(self.resources_dir, 'instructionset.json'))

        self.setWindowIcon(QIcon(os.path.join(self.resources_dir, "logo_color.png")))

        self.start_path = '.'

        self.__create_menu()
        self.__create_toolbar()

        self.editor_widget = EditorWidget()
        self.emulator_dock_widget = EmulatorDockWidget()

        self.setCentralWidget(self.editor_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.emulator_dock_widget)

        self.emulator = Emulator(
            self.editor_widget,
            self.emulator_dock_widget.emulator
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
        saveas_action = QAction(self.tr("Save As..."), self)
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
        tb_new = QAction(QIcon(os.path.join(self.resources_dir, "file.png")), self.tr("New"), self)
        tb_open = QAction(QIcon(os.path.join(self.resources_dir, "open.png")), self.tr("Open"), self)
        # TODO tb_save = QAction(QIcon(os.path.join(resources_dir, "save.png")), self.tr("Save"), self)
        tb_save = QAction(QIcon(os.path.join(self.resources_dir, "save.png")), self.tr("Save"), self)
        tb_mcode = QAction(QIcon(os.path.join(self.resources_dir, "mcode.png")), self.tr("Generate Machine Code"), self)
        tb_vhdl = QAction(QIcon(os.path.join(self.resources_dir, "rom.png")), self.tr("Generate VHDL"), self)
        tb_run = QAction(QIcon(os.path.join(self.resources_dir, "run.png")), self.tr("Run F9"), self)
        tb_debug = QAction(QIcon(os.path.join(self.resources_dir, "debug.png")), self.tr("Debug F8"), self)
        tb_step = QAction(QIcon(os.path.join(self.resources_dir, "step.png")), self.tr("Step F8"), self)
        tb_stop = QAction(QIcon(os.path.join(self.resources_dir, "stop.png")), self.tr("Stop F10"), self)

        tb_run.setShortcut(QKeySequence(Qt.Key_F9))
        tb_debug.setShortcut(QKeySequence(Qt.Key_F8))
        tb_step.setShortcut(QKeySequence(Qt.Key_F8))
        tb_stop.setShortcut(QKeySequence(Qt.Key_F10))

        tb_separator = QAction("", self)
        tb_separator.setSeparator(True)

        tb_new.triggered.connect(self.__new)
        tb_open.triggered.connect(self.__open)
        tb_save.triggered.connect(self.__save)
        tb_mcode.triggered.connect(self.__mcode)
        tb_vhdl.triggered.connect(self.__vhdl)
        tb_run.triggered.connect(self.__run)
        tb_debug.triggered.connect(self.__debug)
        tb_stop.triggered.connect(self.__stop)
        tb_step.triggered.connect(self.__step)

        tb_step.setEnabled(False)
        tb_stop.setEnabled(False)

        tool_bar = self.addToolBar("Toolbar")
        tool_bar.addAction(tb_new)
        tool_bar.addAction(tb_open)
        tool_bar.addAction(tb_save)
        tool_bar.addAction(tb_mcode)
        tool_bar.addAction(tb_vhdl)
        tool_bar.addAction(tb_separator)
        tool_bar.addAction(tb_run)
        tool_bar.addAction(tb_debug)
        tool_bar.addAction(tb_step)
        tool_bar.addAction(tb_stop)

        self.tb_run = tb_run
        self.tb_debug = tb_debug
        self.tb_step = tb_step
        self.tb_stop = tb_stop

    @Slot()
    def __new(self):
        with ResourceManager(os.path.join(self.resources_dir, "template.s32"), "r") as file:
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
            filename = path.split('/')[-1]
            tab_index = self.editor_widget.new_tab(title=filename, content=content)
            self.editor_widget.set_new_tab_file_path(tab_index, path)

    @Slot()
    def __save(self):
        if not self.editor_widget.exists_file_path():
            self.__saveas()
            return

        content = self.editor_widget.get_plain_text()
        file_path = self.editor_widget.get_file_path()
        FileIO.write(file_path, content)

    @Slot()
    def __saveas(self):
        """Opens a file dialog to save a file"""
        (path, selected_filter) = QFileDialog.getSaveFileName(self,
                                                              'Save File',
                                                              '.',
                                                              'Super32 Assembler Files (*.s32)')
        if path:
            content = self.editor_widget.get_plain_text()
            FileIO.write(path, content)
            filename = os.path.basename(path)
            self.editor_widget.set_tab_title(filename)
            self.editor_widget.set_current_tab_file_path(path)

    @Slot()
    def __mcode(self):
        cfg = FileIO.read_json(self.path_to_instructionset)

        input_file = self.editor_widget.get_text()

        preprocessor = Preprocessor()
        assembler = Assembler(Architectures.SINGLE)
        generator = Generator('lines')

        code_address, code, zeros_constants, symboltable, _ = preprocessor.parse(
            input_file=input_file
        )

        machine_code = assembler.parse(
            code_address=code_address,
            code=code,
            zeros_constants=zeros_constants,
            commands=cfg['commands'],
            registers=cfg['registers'],
            symboltable=symboltable
        )

        (path, selected_filter) = QFileDialog.getSaveFileName(self,
                                                              'Save Machine Code File',
                                                              '.',
                                                              'Super32 Machine Code Files (*.m32)')
        if path:
            generator.write(path, machine_code)

    @Slot()
    def __vhdl(self):
        cfg = FileIO.read_json(self.path_to_instructionset)

        input_file = self.editor_widget.get_text()
        source_file = self.editor_widget.get_file_path()

        if source_file is None:
            source_file = "unsaved source"

        preprocessor = Preprocessor()
        assembler = Assembler(Architectures.SINGLE)
        generator = Generator('stream')

        code_address, code, zeros_constants, symboltable, _ = preprocessor.parse(
            input_file=input_file
        )
        with ResourceManager(os.path.join(self.resources_dir, 'template.vhdl'), 'r') as file:
            template = file.read()

        template = template.replace('{{source}}', source_file)
        template = template.replace('{{date}}', datetime.datetime.now().isoformat())

        spacer = "".join("#" for i in range(len(source_file)))
        template = template.replace('{{spacer}}', spacer)

        machine_code = assembler.parse(
            code_address=code_address,
            code=code,
            zeros_constants=zeros_constants,
            commands=cfg['commands'],
            registers=cfg['registers'],
            symboltable=symboltable
        )

        mem = ''
        mc_length = len(machine_code)
        for i in range(0, mc_length):
            mem += '\t\t\t%d => \"%s\"' % (i, machine_code[i])
            if i < mc_length - 1:
                mem += ',\n'

        template = template.replace('{{mem_size}}', str(mc_length - 1))
        template = template.replace('{{memory}}', mem)

        (path, selected_filter) = QFileDialog.getSaveFileName(self,
                                                              'Save VHDL File',
                                                              '.',
                                                              'VHDL Files (*.vhdl)')
        name = os.path.basename(path).replace(".vhdl", "")
        template = template.replace('{{name}}', name)

        if path:
            generator.write(path, template)

    @Slot()
    def __quit(self):
        self.close()

    @Slot()
    def __run(self):
        """Runs the emulator"""
        self.__toggle_debug_actions(True)
        self.emulator.emulate_continuous()

    @Slot()
    def __debug(self):
        self.__toggle_debug_actions(True)
        self.emulator.run()

    @Slot()
    def __step(self):
        self.emulator.emulate_step()

    @Slot()
    def __stop(self):
        self.__toggle_debug_actions(False)
        self.emulator.end_emulation()

    def __toggle_debug_actions(self, emulation_running: bool = True):
        self.tb_debug.setEnabled(not emulation_running)
        self.tb_step.setEnabled(emulation_running)
        self.tb_stop.setEnabled(emulation_running)
