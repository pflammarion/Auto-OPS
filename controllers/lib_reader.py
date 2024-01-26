import itertools
import re

from liberty.parser import parse_liberty
from liberty.types import *


class LibReader:
    """
    The `LibReader` class is designed to extract truth tables from a library (.lib) file,
    automatically identifying input and output names based on the provided gate name.

    Args:
        lib_file_path (str): The path to the library file (.lib) containing gate definitions.

    Attributes:
        lib_file: Liberty object

    Methods:
        extract_truth_table(gate_name):
            Extracts the truth table for the specified gate from the library file.

    Example usage:
        >>> lib_reader = LibReader("library.lib")
        >>> output_truth_table, voltage, input_names, is_flip_flop = lib_reader.extract_truth_table("INV_X1")
        >>> print(output_truth_table)
    """

    def __init__(self, lib_file_path):
        self.lib_file = parse_liberty(open(lib_file_path).read())

    def extract_truth_table(self, gate_name) -> tuple[dict[Any, list], list[dict[str, Any]], list[Any], bool]:
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
            if pin_group['direction'] == "output" or pin_group['function']:
                str_function = str(pin_group['function'])
                output_function[pin_name] = str_function
            else:
                input_names.append(pin_name)

        output_truth_table = {}
        for output_key in output_function:
            output_truth_table[output_key], is_flip_flop = calculateOutputFunction(output_function[output_key],
                                                                                   output_key,
                                                                                   input_names)

        return output_truth_table, voltage, input_names, is_flip_flop


def calculateOutputFunction(function, pin_name, input_names) -> list:
    is_flip_flop = False

    if any("CK" in name or "RESET" in name or "GATE" in name or "CLK" in name for name in
           input_names) or "Q" in pin_name:
        input_symbols = input_names
        is_flip_flop = True

    else:
        input_symbols = re.findall(r'\w+', function)

    input_symbols = sorted(set(input_symbols))

    input_combinations = list(itertools.product([True, False], repeat=len(input_symbols)))

    truth_table = []

    for inputs in input_combinations:
        input_values = {symbol: value for symbol, value in zip(input_symbols, inputs)}

        if any("CK" in name or "RESET" in name or "GATE" in name or "CLK" in name for name in
               input_names) or "Q" in pin_name:
            truth_table.append((input_values, {pin_name: None}))

        else:
            eval_expression = function

            for symbol, value in input_values.items():
                eval_expression = eval_expression.replace(symbol, str(value))

            eval_expression = eval_expression.replace('"', '')
            eval_expression = parse_boolean_function(eval_expression)
            eval_expression = str(format_boolean_function(eval_expression))
            eval_expression = eval_expression.replace("!", " not ").replace("&", " and ").replace("*",
                                                                                                  " and ").replace(
                "+", " or ")
            result = eval(eval_expression)
            # Hot fix problem of xor
            if result == 0 or result == 1:
                result = bool(result)

            if not isinstance(result, bool):
                raise ValueError("Truthtable result is not of type bool")

            truth_table.append((input_values, {pin_name: result}))

    return truth_table, is_flip_flop
