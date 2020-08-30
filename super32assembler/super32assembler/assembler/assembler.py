"""
Assembler Module
"""

import logging
import re
from bitstring import Bits

REG_SIZE = 4  # bytes


class Assembler():
    """Assembler class"""

    def __init__(self, architecture):
        self.__delimiters = ['(', ')', ',']
        self.__symboltable = {}
        self.__architecture = architecture

    def parse(self, code_address, code, zeros_constants, commands, registers, symboltable):
        """method to parse assembler code"""

        bitcode = []
        self.__symboltable = symboltable

        for line_nr, line in enumerate(code):
            logging.debug(str(line))
            tokens = re.split("\\s*[\\s" + re.escape("".join(self.__delimiters)) + "]\\s*", line + " ")[:-1]
            current_address = code_address + line_nr * REG_SIZE
            if len(tokens[0]) == 0:
                continue
            if tokens[0] in commands['arithmetic']:
                bitcode = bitcode + self.__parse_arithmetic(
                    tokens,
                    commands['arithmetic'],
                    registers
                )
            elif tokens[0] in commands['storage']:
                bitcode = bitcode + self.__parse_storage(
                    current_address,
                    tokens,
                    commands['storage'],
                    registers
                )
            elif tokens[0] in commands['branch']:
                bitcode = bitcode + self.__parse_branch(
                    current_address,
                    tokens,
                    commands['branch'],
                    registers
                )
            else:
                raise Exception(
                    "Parsing error. Command not found: " + tokens[0])

        if not self.__architecture.value:  # single
            zeros_constants = self.__generate_start(
                code_address,
                zeros_constants,
                commands,
                registers
            )
            machine_code = self.__generate_machinecode(
                code_address,
                bitcode,
                zeros_constants
            )
            machine_code = self.__generate_end(
                machine_code,
                commands,
                registers
            )
        else:
            machine_code = bitcode

        return machine_code

    def __generate_machinecode(self, code_address, bitcode, zeros_constants):
        index = int(code_address / REG_SIZE)
        machine_code = zeros_constants[:]
        for i, bitcode_line in enumerate(bitcode, index):
            machine_code[i] = bitcode_line
        return machine_code

    def __validate_label(self, label):
        if label not in self.__symboltable.keys():
            raise Exception("Label not found: " + label)

        return self.__symboltable.get(label)

    def __validate_code_length(self, machine_code):
        if len(machine_code) != 32:
            raise Exception('Parsing error')

    def __validate_token_length(self, tokens):
        if len(tokens) != 4:
            raise Exception('Parsing error')

    def __validate_bits(self, machine_code):
        for bit in machine_code:
            if bit not in ['0', '1']:
                raise Exception('Parsing error')

    def __parse_arithmetic(self, tokens, arithmetic, registers):
        self.__validate_token_length(tokens)

        for cmd in arithmetic:
            for i, token in enumerate(tokens):
                if token == cmd:
                    tokens[i] = arithmetic[cmd]
                    break

        for reg in registers:
            for i, token in enumerate(tokens):
                if token == reg:
                    tokens[i] = registers[reg]

        self.__validate_bits(''.join(tokens))

        # add 5bit dont-cares and 6bit op-code always zero
        tokens = tokens + ['00000'] + ['000000']

        # rearrenge bit-order
        order = [5, 2, 3, 1, 4, 0]
        tokens = [tokens[i] for i in order]

        machine_code = ''.join(tokens)
        self.__validate_code_length(machine_code)

        logging.debug(machine_code)
        return [machine_code]

    def __parse_storage(self, current_address, tokens, storage, registers):
        self.__validate_token_length(tokens)

        for cmd in storage:
            for i, token in enumerate(tokens):
                if token == cmd:
                    tokens[i] = storage[cmd]
                    break

        for reg in registers:
            for i, token in enumerate(tokens):
                if token == reg:
                    tokens[i] = registers[reg]

        label_or_number = tokens[2]
        if self.__is_number(label_or_number):
            offset = self.__hex_to_decimal(label_or_number)
            tokens[2] = Bits(int=offset, length=16).bin
        else:  # label
            address = self.__validate_label(label_or_number)
            tokens[2] = Bits(int=address, length=16).bin

        self.__validate_bits(''.join(tokens))

        # rearrenge bit-order
        order = [0, 3, 1, 2]
        tokens = [tokens[i] for i in order]

        machine_code = ''.join(tokens)
        self.__validate_code_length(machine_code)

        logging.debug(machine_code)
        return [machine_code]

    def __parse_branch(self, current_address, tokens, branch, registers):
        self.__validate_token_length(tokens)

        for cmd in branch:
            for i, token in enumerate(tokens):
                if token == cmd:
                    tokens[i] = branch[cmd]
                    break

        for reg in registers:
            for i, token in enumerate(tokens):
                if token == reg:
                    tokens[i] = registers[reg]

        label_or_number = tokens[-1]
        if self.__is_number(label_or_number):
            address = self.__hex_to_decimal(label_or_number)
            tokens[-1] = Bits(int=address, length=16).bin
        else:  # label
            address = self.__validate_label(label_or_number)
            offset = address - current_address
            offset -= REG_SIZE
            offset = int(offset / REG_SIZE)
            tokens[-1] = Bits(int=offset, length=16).bin

        self.__validate_bits(''.join(tokens))

        # rearrenge bit-order
        order = [0, 2, 1, 3]
        tokens = [tokens[i] for i in order]

        machine_code = ''.join(tokens)
        self.__validate_code_length(machine_code)

        logging.debug(machine_code)
        return [machine_code]

    def __generate_start(self, start_address, zeros_constants, commands, registers):
        branch_address = int(start_address / REG_SIZE - 1)
        branch = self.__parse_branch(
            0,
            ['BEQ', 'R30', 'R30', "{ADDRESS}".format(ADDRESS=branch_address)],
            commands['branch'],
            registers
        )
        zeros_constants[0] = ''.join(branch)
        return zeros_constants

    def __generate_end(self, zeros_constants, commands, registers):
        branch = self.__parse_branch(
            0,
            ['BEQ', 'R30', 'R30', "-1"],
            commands['branch'],
            registers
        )
        zeros_constants[-1] = ''.join(branch)
        return zeros_constants

    @staticmethod
    def __is_number(s: str) -> bool:
        """
        Checks whether a string represents a number
        Returns true if the string represents a hex number ('$') or an integer.
        Returns false otherwise.
        """
        if s.startswith('$'):
            return True

        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def __hex_to_decimal(number: str) -> int:
        """
        Checks whether a string begins with '$'
        If so, it converts the hex number to decimal
        Returns the converted number or the original number
        """
        if not number.startswith('$'):
            return int(number)

        num_no_prefix = number[1:]

        return int(num_no_prefix, 16)
