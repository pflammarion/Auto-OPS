import ast
import cProfile
import copy
import itertools
import sys
import time
import argparse
import traceback

import gdspy

from controllers import gds_drawing
from controllers.GDS_Object.op import Op
from controllers.def_parser import get_gates_info_from_def_file
from controllers.lib_reader import LibReader
#


def run_cli():
    parser = argparse.ArgumentParser(description='Auto-OPS command line tool')

    parser.add_argument('-s', '--std_file', type=str, help='Input std file', required=True)
    parser.add_argument('-l', '--lib_file', type=str, help='Input lib file', required=True)
    parser.add_argument('-g', '--gds_file', help='Input GDS design file')
    parser.add_argument('-d', '--def_file', help='Input DEF design file')
    parser.add_argument('-i', '--input', nargs='+', type=int, help='Input pattern list applied as A-Z/0-9 order')
    parser.add_argument('-la', '--layer_list', type=str, help='Diffusion, ... [1, 5, 9, 10, 11]',
                        required=True)
    parser.add_argument('-c', '--cell_list', nargs='+', type=str,
                        help='Cell list for active regions extraction (empty for all cells)')
    parser.add_argument('-o', '--output', help='Output type', choices=['reflection_over_cell', 'unit_test'])
    parser.add_argument('--gui', action='store_true', help='Start the gui')
    parser.add_argument('--unit_test', help='Do cell technologie unit test')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('-f', '--flip_flop', type=int, help='Flip Flop output Q')

    args = parser.parse_args()

    std_file = args.std_file
    lib_file = args.lib_file
    gds_file = args.gds_file
    def_file = args.def_file
    cell_input = args.input
    layer_list = ast.literal_eval(args.layer_list)
    cell_list = args.cell_list
    output = args.output
    verbose_mode = args.verbose
    flip_flop = args.flip_flop

    unit_test = args.unit_test

    if args.gui:
        run_gui()
    else:
        run_auto_ops(std_file, lib_file, gds_file, def_file, cell_input, layer_list, cell_list, output, verbose_mode, unit_test, flip_flop)


def run_gui():
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import QApplication
    from controllers.main_controller import MainController

    app = QApplication(sys.argv)
    app.setApplicationName("CMOS-INV-GUI")
    app.setWindowIcon(QIcon('resources/app_logo.png'))
    controller = MainController()
    view = controller.get_view()
    view.show()
    sys.exit(app.exec())



def run_auto_ops(std_file, lib_file, gds_file, def_file, cell_input, layer_list, cell_name_list, output, verbose_mode, unit_test, flip_flop):
    blue_color = "\033[1;34m"
    reset_color = "\033[0m"
    orange_color = "\033[1;33m"
    white_color = "\033[1;37m"
    green_color = "\033[1;32m"
    red_color = "\033[1;31m"

    start_time = time.time()

    if unit_test:
        print(f"{blue_color}Reading GDS file ...{reset_color}")

    lib = gdspy.GdsLibrary()
    gds_cell_list = lib.read_gds(std_file).cells

    def_extract = []
    if def_file:
        def_extract = get_gates_info_from_def_file(def_file)
        cell_name_list = def_extract[1].keys()

    if unit_test:
        print(f"{blue_color}Reading lib file ...{reset_color}")

    lib_reader = LibReader(lib_file)

    if cell_name_list is None:
        cell_name_list = gds_cell_list.keys()

    error_cell_list = []
    counter = 0
    state_counter = 0

    total_iterations = len(cell_name_list)
    multiple_exporting_dict = {}

    for input_cell_name in cell_name_list:
        for gds_cell_name, gds_cell in gds_cell_list.items():
            if gds_cell_name != input_cell_name:
                continue

            counter += 1
            internal_state_error = 0

            if unit_test:
                print(f"{blue_color}Generating test object for: {gds_cell_name} ...{reset_color}")

            multiple_exporting_dict[gds_cell_name] = []

            # start progress bar
            if verbose_mode:
                progress = counter / total_iterations
                bar_length = 20
                filled_length = int(bar_length * progress)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                print(
                    f'\n\r{reset_color}Progress: {green_color}[{bar}] {int(progress * 100)}% Complete {reset_color} -- {gds_cell_name}{white_color} || {blue_color}',
                    end='', flush=True)
            # end progress bar

            try:
                truth_table, voltage, input_names = lib_reader.extract_truth_table(gds_cell_name)
                op_master = Op(gds_cell_name, gds_cell, layer_list, truth_table, voltage, input_names)

                draw_inputs = {}

                if cell_input and len(cell_input) == len(input_names):
                    for index, inp in enumerate(input_names):
                        draw_inputs[inp] = cell_input[index]

                    op_object = copy.deepcopy(op_master)
                    op_object.apply_state(draw_inputs, flip_flop)

                    if output == "reflection_over_cell":
                        gds_drawing.export_reflection_to_png_over_gds_cell(op_object, True, False, flip_flop)

                    state_counter += 1

                else:
                    combinations = list(itertools.product([0, 1], repeat=len(input_names)))
                    for combination in combinations:
                        for index, inp in enumerate(input_names):
                            draw_inputs[inp] = combination[index]
                        try:
                            op_object = copy.deepcopy(op_master)
                            op_object.apply_state(draw_inputs, flip_flop)

                            if output == "reflection_over_cell":
                                gds_drawing.export_reflection_to_png_over_gds_cell(op_object, True, False, flip_flop)

                            if def_file:
                                op_object.calculate_orientations()
                                multiple_exporting_dict[gds_cell_name].append(copy.deepcopy(op_object))

                            if unit_test:
                                multiple_exporting_dict[gds_cell_name].append(copy.deepcopy(op_object))

                            state_counter += 1

                        except Exception as e:
                            internal_state_error += 1
                            if verbose_mode:
                                print(f"{orange_color}\nCell processing error {draw_inputs} \nType : {e}{reset_color}")
                                # traceback.print_exc()
                                if gds_cell_name not in error_cell_list:
                                    error_cell_list.append(gds_cell_name)

                if verbose_mode:
                    if internal_state_error > 0:
                        state_length = pow(2, len(input_names))
                        print(f"{red_color}\n{internal_state_error}/{state_length} processes failed{reset_color}")
                    else:
                        print(f'\n{green_color}Processing complete.{reset_color}')

            except Exception as e:
                if verbose_mode:
                    print(f"{red_color}An error occurred: {e}{reset_color}")
                    traceback.print_exc()
                    error_cell_list.append(gds_cell_name)

    end_time_log = time.time()
    gds_drawing.write_output_log(start_time, end_time_log, filtered_cells=cell_name_list, state_counter=state_counter,
                                 error_cell_list=error_cell_list)

    if unit_test:
        gds_drawing.unit_test(multiple_exporting_dict, unit_test)

    if def_file:
        gds_drawing.benchmark(multiple_exporting_dict, def_extract, True)
        end_time = time.time()
        gds_drawing.benchmark_export_data(def_extract, end_time - start_time, def_file)


if __name__ == "__main__":
    debug = False
    if debug:
        #run_auto_ops("Platforms/IHP-Open-PDK130nm/sg13g2_stdcell.gds", "Platforms/IHP-Open-PDK130nm/sg13g2_stdcell_typ_1p20V_25C.lib", "", "", [], [[1, 0], [31, 0], [5, 0], [6, 0], [8, 0], [8, 25]], ['sg13g2_nand2_1'], "unit_test", True)
        run_auto_ops("input/stdcells.gds", "input/stdcells.lib", "", "/Users/paul/IdeaProjects/CMOS-INV-GUI/benchmarks/EPFL/Hyp/Par/top.def", [], [[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]], [], "", True, False, None)
    else:
        run_cli()
