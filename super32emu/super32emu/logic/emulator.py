"""Emulator-Logic"""
from super32assembler.assembler.assembler import Assembler
from super32assembler.preprocessor.preprocessor import Preprocessor
from super32assembler.assembler.architecture import Architectures
from super32utils.inout.fileio import FileIO
from bitstring import BitArray
import os


class Emulator:
    """This is the logic to emulate the assembly instructions"""

    def __init__(self, editor_widget, emulator_widget, footer_widget):
        self.editor_widget = editor_widget
        self.emulator_widget = emulator_widget
        self.footer_widget = footer_widget

        self.__reset_registers()

        self.emulator_widget.set_pc(0)
        self.emulator_widget.set_storage(''.ljust(2**10, '0'))
        self.emulator_widget.set_symbols({"-": "-"})

        path_to_instructionset = os.path.join(os.path.dirname(__file__), 'instructionset.json')
        self.cfg = FileIO.read_json(path_to_instructionset)
        self.commands = self.cfg['commands']
        self.memory = []

    def run(self):
        """Parse and execute the commands written in the editor"""

        preprocessor = Preprocessor()
        assembler = Assembler(Architectures.SINGLE)

        code_address, code, zeros_constants, symboltable = preprocessor.parse(
            input_file=self.editor_widget.get_text()
        )

        self.memory = assembler.parse(
            code_address=code_address,
            code=code,
            zeros_constants=zeros_constants,
            commands=self.cfg['commands'],
            registers=self.cfg['registers'],
            symboltable=symboltable
        )

        self.emulator_widget.set_symbols(symboltable)
        self.__reset_registers()
        self.__emulate()

    def __emulate(self):
        print(f"Starting new program execution: ")

        # Set the memory content to the widget
        # Fill remaining memory with zeros
        self.emulator_widget.set_storage(
            ''.join(self.memory).ljust(2**10, '0'))

        self.row_counter = 0

        while self.row_counter < len(self.memory):
            print(f"{self.row_counter * 4} - ", end='')
            instructionset = self.memory[self.row_counter]
            self.__parse_instructionset(instructionset)
            self.row_counter += 1

            self.__set_programm_counter()

            self.emulator_widget.set_storage(
                ''.join(self.memory).ljust(2**10, '0'))

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

    def __set_programm_counter(self):
        address_counter = self.row_counter * 4
        self.emulator_widget.set_pc(address_counter)

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

        print(f"Arithmetic: Handling contents from registers {self.__get_register_index(first_source)}"
              f" and {self.__get_register_index(second_source)}. "
              f"Saving result to {self.__get_register_index(target)}.")

    def __branch(self, r2: str, r1: str, offset: str):
        if not self.__get_register_value(r2) == self.__get_register_value(r1):
            print(f"Branch: Did not branch. Register contents of {self.__get_register_index(r1)}"
                  f" and {self.__get_register_index(r2)} not equal")
            return

        offset_num = BitArray(bin=offset).int
        self.row_counter = (offset_num // 4) - 1
        print(f"Branch: Continuing program execution at address {offset_num}")

    def __load(self, r2: str, r1: str, offset: str):
        offset = BitArray(bin=offset).int
        r2_value = self.__get_register_value(r2)
        address = offset + r2_value
        memory_value = BitArray(bin=self.memory[address // 4]).hex.upper()

        r1_num = BitArray(bin=r1).uint
        self.emulator_widget.set_register(r1_num, memory_value)

        print(f"Load: Loading memory content from address {address} into register {r1_num}")

    def __save(self, r2: str, r1: str, offset: str):
        offset_num = BitArray(bin=offset).int
        address = offset_num + self.__get_register_value(r2)
        value = self.__get_register_value(r1)
        value_bin = bin(value)[2:].rjust(32, '0')
        self.memory[address // 4] = value_bin

        print(f"Save: Saving content from register {self.__get_register_index(r1)} to address {address}")

    def __get_register_index(self, target):
        for register in self.cfg['registers']:
            value = self.cfg['registers'][register]
            if target == value:
                return int(value, 2)

    def __get_register_value(self, register: str) -> int:
        register_num = BitArray(bin=register).uint
        register_value = int(self.emulator_widget.get_register(register_num), 16)

        return register_value

    def __reset_registers(self):
        for rindex in range(32):
            self.emulator_widget.set_register(rindex, '00000000')
