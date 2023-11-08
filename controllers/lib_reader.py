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

    def __init__(self, lib_file_path):
        """
        Initializes a new `LibReader` instance with the provided gate name and library file groupe previously extracted.

        Args:
            gate_name (str): The name of the gate for which the truth table is to be extracted.
            lib_file_path (str): The path to the library file (.lib) containing gate definitions.
        """
        self.lib_file = parse_liberty(open(lib_file_path).read())

    def extract_truth_table(self, gate_name):
        """
        Extracts the truth table for the specified gate from the library file.

        Returns:
            dict: A dictionary representing the truth table, where input patterns (as binary strings)
            are mapped to their corresponding output values (0 or 1).
        """

        # Find the cell (gate) with the specified name
        cell = select_cell(self.lib_file, gate_name)

        voltage = []

        for pg_pin in cell.get_groups('pg_pin'):
            data = {
                'name': pg_pin['voltage_name'],
                'type': pg_pin['pg_type']
            }
            voltage.append(data)

        input_names = []
        output_function = {}
        for pin_group in cell.get_groups('pin'):
            pin_name = pin_group.args[0]
            if pin_group['function']:
                str_function = str(pin_group['function'])
                output_function[pin_name] = str_function
            else:
                input_names.append(pin_name)

        output_truth_table = {}
        for output_key in output_function:
            output_truth_table[output_key] = self.calculateOutputFunction(output_function[output_key], output_key)

        return output_truth_table, voltage, input_names



    def calculateOutputFunction(self, function, pin_name):
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
            eval_expression = eval_expression.replace("!", "not ").replace("&", "and")

            # Evaluate the expression two time to convert it from a string to a result
            result = eval(eval(eval_expression))

            truth_table.append((input_values, {pin_name: result}))

        return truth_table


