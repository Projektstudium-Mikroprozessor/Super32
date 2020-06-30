"""Emulator-Logic"""
from super32assembler.assembler.assembler import Assembler
from super32assembler.preprocessor.preprocessor import Preprocessor
from super32assembler.assembler.architecture import Architectures
from super32utils.inout.fileio import FileIO
from bitstring import BitArray
import os
import logging


class Emulator:
    """This is the logic to emulate the assembly instructions"""

    def __init__(self, editor_widget, emulator_widget, footer_widget):
        self.editor_widget = editor_widget
        self.emulator_widget = emulator_widget
        self.footer_widget = footer_widget

        self.emulator_widget.reset_all_registers()

        self.emulator_widget.set_pc(0)
        self.emulator_widget.set_storage(''.ljust(2**10, '0'))
        self.emulator_widget.set_symbols({"-": "-"})

        path_to_instructionset = os.path.join(os.path.dirname(__file__), '..', 'instructionset.json')
        self.cfg = FileIO.read_json(path_to_instructionset)
        self.commands = self.cfg['commands']
        self.memory = []

        self.editor_line_numbers = None
        self.row_counter = 0
        self.emulation_running = False

    def emulate_continuous(self):
        if self.emulation_running is False:
            self.__run()

        while self.row_counter < len(self.memory):
            self.emulate_step()

        self.__end_emulation()

    def emulate_step(self):
        if self.row_counter >= len(self.memory):
            self.__end_emulation()

        if self.emulation_running is False:
            self.__run()

        logging.debug(f"Executing code address {self.row_counter * 4}")

        instructionset = self.memory[self.row_counter]
        self.__parse_instructionset(instructionset)
        self.row_counter += 1

        self.__set_programm_counter()

        self.emulator_widget.set_storage(
            ''.join(self.memory).ljust(2 ** 10, '0'))

        self.emulator_widget.highlight_memory_line(self.row_counter)
        self.__highlight_editor_line()

    def __end_emulation(self):
        self.emulation_running = False
        logging.debug(f"End of program execution")

    def __run(self):
        """Parse and execute the commands written in the editor"""
        preprocessor = Preprocessor()
        assembler = Assembler(Architectures.SINGLE)

        self.code_address, code, zeros_constants, symboltable, self.editor_line_numbers = preprocessor.parse(
            input_file=self.editor_widget.get_text()
        )

        self.memory = assembler.parse(
            code_address=self.code_address,
            code=code,
            zeros_constants=zeros_constants,
            commands=self.cfg['commands'],
            registers=self.cfg['registers'],
            symboltable=symboltable
        )

        self.emulator_widget.set_symbols(symboltable)
        self.emulator_widget.reset_all_registers()

        # Set the memory content to the widget
        # Fill remaining memory with zeros
        self.emulator_widget.set_storage(
            ''.join(self.memory).ljust(2**10, '0'))

        self.row_counter = 0

        self.emulation_running = True

        logging.debug(f"Starting new program execution: ")

    def __parse_instructionset(self, instructionset: str):
        instruction = instructionset[0:6]

        if instruction == '000000':
            self.__arithmetic_instruction(
                instructionset[6:11],
                instructionset[11:16],
                instructionset[16:21],
                instructionset[26:32])
        elif instruction == self.commands['branch']['BEQ']:
            self.__branch(
                instructionset[6:11],
                instructionset[11:16],
                instructionset[16:32])
        elif instruction == self.commands['storage']['LW']:
            self.__load(
                instructionset[6:11],
                instructionset[11:16],
                instructionset[16:32])
        elif instruction == self.commands['storage']['SW']:
            self.__save(
                instructionset[6:11],
                instructionset[11:16],
                instructionset[16:32])

    def __arithmetic_instruction(self, first_source: str, second_source: str, target: str, func: str):
        r1_value = self.__get_register_value(first_source)
        r2_value = self.__get_register_value(second_source)

        if func == self.commands['arithmetic']['SUB']:
            result = r1_value - r2_value
        elif func == self.commands['arithmetic']['ADD']:
            result = r1_value + r2_value
        elif func == self.commands['arithmetic']['AND']:
            result = r1_value & r2_value
        elif func == self.commands['arithmetic']['OR']:
            result = r1_value | r2_value
        elif func == self.commands['arithmetic']['NOR']:
            result = r1_value | r2_value ^ 0b11111111
        else:
            # TODO Define exception for unknown instruction
            raise Exception

        register = self.__get_register_index(target)
        result_hex = hex(result)[2:].upper()
        self.emulator_widget.set_register(register, result_hex)

        logging.debug(f"Arithmetic: Handling contents from registers {self.__get_register_index(first_source)}"
                      f" and {self.__get_register_index(second_source)}. "
                      f"Saving result to {self.__get_register_index(target)}.")

    def __branch(self, r2: str, r1: str, offset: str):
        if not self.__get_register_value(r2) == self.__get_register_value(r1):
            logging.debug(f"Branch: Did not branch. Register contents of {self.__get_register_index(r1)}"
                          f" and {self.__get_register_index(r2)} not equal")
            return

        offset_num = BitArray(bin=offset).int
        self.row_counter = self.row_counter + offset_num
        logging.debug(f"Branch: Continuing program execution at address {(self.row_counter + 1) * 4}")

    def __load(self, r2: str, r1: str, offset: str):
        offset_num = BitArray(bin=offset).int
        r2_value = self.__get_register_value(r2)
        address = self.row_counter + offset_num + r2_value + 1
        memory_value = BitArray(bin=self.memory[address]).hex.upper()

        r1_num = BitArray(bin=r1).uint
        self.emulator_widget.set_register(r1_num, memory_value)

        logging.debug(f"Load: Loading memory content from address {address * 4} into register {r1_num}")

    def __save(self, r2: str, r1: str, offset: str):
        offset_num = BitArray(bin=offset).int
        r2_value = self.__get_register_value(r2)
        address = self.row_counter + offset_num + r2_value + 1
        value = self.__get_register_value(r1)
        value_bin = bin(value)[2:].rjust(32, '0')
        self.memory[address] = value_bin

        logging.debug(f"Save: Saving content from register {self.__get_register_index(r1)} to address {address * 4}")

    def __get_register_index(self, target):
        for register in self.cfg['registers']:
            value = self.cfg['registers'][register]
            if target == value:
                return int(value, 2)

    def __get_register_value(self, register: str) -> int:
        register_num = BitArray(bin=register).uint
        register_value = int(self.emulator_widget.get_register(register_num), 16)

        return register_value

    def __set_programm_counter(self):
        address_counter = self.row_counter * 4
        address_counter_hex = hex(address_counter)[2:].upper()
        self.emulator_widget.set_pc(address_counter_hex)

    def __highlight_editor_line(self):
        # TODO Fix bug with END directive
        row_counter_at_start_directive = self.row_counter == 0
        if row_counter_at_start_directive:
            return

        current_address_without_offset = self.row_counter - self.code_address // 4
        current_editor_line = self.editor_line_numbers[current_address_without_offset]
        self.editor_widget.highlight_line(current_editor_line)
