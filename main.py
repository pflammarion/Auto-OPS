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
from controllers.main_controller import MainController

if __name__ == "__main__":
    #benchmark_list = ['c17', 'c432', 'c499', 'c1355', 'c1908', 'c2670', 'c3540', 'c7552']

    for def_name in range(0, 1):
        start_time = time.time()

        lib_file = "Platforms/PDK45nm/NangateOpenCellLibrary_typical.lib"
        #gds_file = "Platforms/GDS-II/TRJ.gds"
        open_cell_lib = "Platforms/PDK45nm/stdcells.gds"
        def_path = f"Benchmarks_ISCAS85/GDS-II/Hyp/Par/top.def"

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

        gds_drawing.benchmark(multiple_exporting_dict, def_extract)
        end_time = time.time()
        gds_drawing.benchmark_export_data(def_extract, end_time - start_time, def_name)
