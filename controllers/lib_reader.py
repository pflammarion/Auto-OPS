import itertools
import re

from liberty.parser import parse_liberty
from liberty.types import *


class LibReader:
    """
    The `LibReader` class is designed to extract truth tables from a library (.lib) file,
    automatically identifying input and output names based on the provided gate name.

    Attributes:
        gate_name (str): The name of the gate for which the truth table is to be extracted.
        lib_file_path (str): The path to the library file (.lib) containing gate definitions.

    Methods:
        extract_truth_table():
            Extracts the truth table for the specified gate from the library file.

    Example usage:
        >>> lib_reader = LibReader("AND2_X1", "library.lib")
        >>> truth_table = lib_reader.extract_truth_table()
        >>> print(truth_table)
    """

    def __init__(self, gate_name, lib_file_path):
        """
        Initializes a new `LibReader` instance with the provided gate name and library file path.

        Args:
            gate_name (str): The name of the gate for which the truth table is to be extracted.
            lib_file_path (str): The path to the library file (.lib) containing gate definitions.
        """
        self.gate_name = gate_name
        self.lib_file_path = lib_file_path

    def extract_truth_table(self):
        """
        Extracts the truth table for the specified gate from the library file.

        Returns:
            dict: A dictionary representing the truth table, where input patterns (as binary strings)
            are mapped to their corresponding output values (0 or 1).
        """
        library = parse_liberty(open(self.lib_file_path).read())

        # Find the cell (gate) with the specified name
        cell = select_cell(library, self.gate_name)

        for pin_group in cell.get_groups('pin'):
            pin_name = pin_group.args[0]
            print(pin_name)
            if pin_group['function']:
                print("output")
                print("\n")
                print(pin_group['function'])
                str_function = str(pin_group['function'])
                return self.calculateOutputFunction(str_function)
            else:
                print("input")

            print("\n")

    def calculateOutputFunction(self, function):
        # Use regular expression to find input symbols with letters and numbers
        input_symbols = re.findall(r'\w+', function)
        input_symbols = sorted(set(input_symbols))

        input_combinations = list(itertools.product([True, False], repeat=len(input_symbols)))

        truth_table = []

        for inputs in input_combinations:
            input_values = {symbol: value for symbol, value in zip(input_symbols, inputs)}

            eval_expression = function
            for symbol, value in input_values.items():
                eval_expression = eval_expression.replace(symbol, str(value))

            # Replace not logical operator for Python's operators
            eval_expression = eval_expression.replace("!", "not")

            # Evaluate the expression two time to convert it from a string to a result
            result = eval(eval(eval_expression))
            truth_table.append((input_values, result))

        return truth_table


