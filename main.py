import copy
import itertools
import sys
import time

import gdspy
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from controllers import gds_drawing
from controllers.GDS_Object.op import Op
from controllers.def_parser import get_gates_info_from_def_file
from controllers.lib_reader import LibReader

if __name__ == "__main__":

    benchmarks = 3

    def_path = ""

    with open('benchmarks.log', 'a') as f:
        f.write("\n---------------------------------------\n")

    if benchmarks == 1:
        benchmark_list = ['c17', 'c432', 'c499', 'c1355', 'c1908', 'c2670', 'c3540', 'c7552']

    elif benchmarks == 2:
        benchmark_list = ['test01', 'test02', 'test03', 'test04', 'test05', 'test06', 'test07', 'test08', 'test09', 'test10', 'test11', 'test12', 'test13', 'test14', 'test15', 'test16', 'test17', 'test18', 'test19', 'test20']

    # elif benchmarks == 3
    else:
        benchmark_list = ['adder', 'bar', 'div', 'Hyp', 'log2', 'max', 'multiplier', 'sin', 'sqrt', 'square']

    for def_name in benchmark_list:
        start_time = time.time()

        lib_file = "Platforms/PDK45nm/NangateOpenCellLibrary_typical.lib"
        open_cell_lib = "Platforms/PDK45nm/stdcells.gds"

        if benchmarks == 1:
            def_path = f"benchmarks/Benchmarks_ISCAS85/GDS-II/Benchmarks/{def_name}/{def_name}.def"
        elif benchmarks == 2:
            def_path = f"benchmarks/ICCAD_Contest2021/{def_name}/Par/top.def"
        elif benchmarks == 3:
            def_path = f"benchmarks/EPFL/{def_name}/Par/top.def"

        def_extract = get_gates_info_from_def_file(def_path)
        cells_list = def_extract[1]

        lib_reader = LibReader(lib_file)

        lib_std = gdspy.GdsLibrary()
        std_cells_list = lib_std.read_gds(open_cell_lib).cells

        multiple_exporting_dict = {}
        for def_cell_name in cells_list.keys():
            for cell_name, gds_cell in std_cells_list.items():
                if cell_name == def_cell_name:

                    multiple_exporting_dict[cell_name] = []

                    truth_table, voltage, input_names = lib_reader.extract_truth_table(cell_name)
                    draw_inputs = {}
                    combinations = list(itertools.product([0, 1], repeat=len(input_names)))

                    for combination in combinations:
                        for index, inp in enumerate(input_names):
                            draw_inputs[inp] = combination[index]

                        op_object = Op(cell_name, gds_cell, [1, 5, 9, 10, 11], truth_table, voltage, draw_inputs)
                        multiple_exporting_dict[cell_name].append(copy.deepcopy(op_object))

        gds_drawing.benchmark(multiple_exporting_dict, def_extract, False)
        end_time = time.time()
        gds_drawing.benchmark_export_data(def_extract, end_time - start_time, def_name)
