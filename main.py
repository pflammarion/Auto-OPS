import ast
import copy
import itertools
import sys
import time
import argparse

import gdspy

from controllers import gds_drawing
from controllers.GDS_Object.auto_ops_propagation import AutoOPSPropagation
from controllers.def_parser import get_gates_info_from_def_file
from controllers.lib_reader import LibReader


def run_cli():
    parser = argparse.ArgumentParser(description='Auto-OPS command line tool')

    subparsers = parser.add_subparsers(help='Subcommands', dest='subcommand')

    parser_command_line = subparsers.add_parser('auto_ops', help='Auto-OPS command line mode')

    parser_command_line.add_argument('-s', '--std_file', type=str, help='Input std file', required=True)
    parser_command_line.add_argument('-l', '--lib_file', type=str, help='Input lib file', required=True)
    parser_command_line.add_argument('-la', '--layer_list', type=str, help='Diffusion, ... [1, 5, 9, 10, 11]', required=True)
    parser_command_line.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    parser_command_line.add_argument('--unit_test', help='Do cell technology unit test')

    parser_command_line.add_argument('-d', '--def_file', help='Input DEF design file')
    parser_command_line.add_argument('-vpi', '--vpi_file', help='Input VPI output file')
    parser_command_line.add_argument('--benchmark_plot', action='store_true', help='Plot benchmarks results. This could affect performance.')
    parser_command_line.add_argument('--patch_size', type=int, help='Int in um^2 of the patch size (default 20)')

    parser_command_line.add_argument('-i', '--input', nargs='+', type=int, help='Input pattern list applied as A-Z/0-9 order')
    parser_command_line.add_argument('-c', '--cell_list', nargs='+', type=str, help='Cell list for active regions extraction (empty for all cells)')
    parser_command_line.add_argument('-f', '--flip_flop', type=int, help='Flip Flop output Q')
    parser_command_line.add_argument('-o', '--output', help='Output type', choices=['reflection_over_cell'])

    parser_gui = subparsers.add_parser('gui', help='GUI mode for simulation')
    parser_gui.add_argument('-cli', '--command_line', action='store_true', help='Use the GUI as a command line tool')
    parser_gui.add_argument('-s', '--script', help='Add an input script based on available commands in the GUI_cli')
    parser_gui.add_argument('-c', '--config', help='Change the config file for the GUI')

    args = parser.parse_args()

    if args.subcommand == 'gui':
        run_gui(args.command_line, args.config, args.script)
    else:
        std_file = args.std_file
        lib_file = args.lib_file
        def_file = args.def_file
        vpi_file = args.vpi_file
        cell_input = args.input
        layer_list = ast.literal_eval(args.layer_list)
        cell_list = args.cell_list
        output = args.output
        verbose_mode = args.verbose
        flip_flop = args.flip_flop
        benchmark_plot = args.benchmark_plot
        patch_size = args.patch_size
        unit_test = args.unit_test

        run_auto_ops(std_file, lib_file, def_file, cell_input, layer_list, cell_list, output, verbose_mode, unit_test, flip_flop, vpi_file, benchmark_plot, patch_size)


def run_gui(command_line, config, script):
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication
    from controllers.main_controller import MainController

    print("Starting Auto-OPS....")

    if not command_line:
        app = QApplication(sys.argv)
        controller = MainController(False, config)
        app.setApplicationName("CMOS-INV-GUI")
        app.setWindowIcon(QIcon('resources/app_logo.png'))
        view = controller.get_view()
        view.show()
        sys.exit(app.exec())

    else:
        MainController(True, config, script)




def run_auto_ops(std_file, lib_file, def_file, cell_input, layer_list, cell_name_list, output, verbose_mode, unit_test, flip_flop, vpi_file, benchmark_plot, patch_size):
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

    vpi_extraction = None
    if vpi_file:
        vpi_extraction = {}
        with open(vpi_file, 'r') as file:
            for line in file:
                key, inputs, outputs = line.strip().split(',')
                vpi_extraction[key] = {'inputs': inputs, 'outputs': outputs}

    def_extract = []
    if def_file:
        def_extract = get_gates_info_from_def_file(def_file, patch_size)
        cell_name_list = def_extract[2]

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
                truth_table, voltage, input_names, is_flip_flop = lib_reader.extract_truth_table(gds_cell_name)
                propagation_master = AutoOPSPropagation(gds_cell_name, gds_cell, layer_list, truth_table, voltage, input_names)

                draw_inputs = {}

                if cell_input and len(cell_input) == len(input_names):
                    for index, inp in enumerate(input_names):
                        draw_inputs[inp] = cell_input[index]

                    propagation_object = copy.deepcopy(propagation_master)
                    propagation_object.apply_state(draw_inputs, flip_flop)

                    if output == "reflection_over_cell":
                        gds_drawing.export_reflection_to_png_over_gds_cell(propagation_object, True, False, flip_flop)

                    state_counter += 1

                else:
                    input_number = len(input_names)
                    if is_flip_flop:
                        input_number += 1

                    combinations = list(itertools.product([0, 1], repeat=input_number))

                    if unit_test:
                        multiple_exporting_dict[gds_cell_name] = []
                    else:
                        multiple_exporting_dict[gds_cell_name] = {}

                    for combination in combinations:
                        for index, inp in enumerate(input_names):
                            draw_inputs[inp] = combination[index]
                        try:
                            if is_flip_flop:
                                flip_flop = combination[-1]

                            propagation_object = copy.deepcopy(propagation_master)
                            propagation_object.apply_state(draw_inputs, flip_flop)

                            if output == "reflection_over_cell":
                                gds_drawing.export_reflection_to_png_over_gds_cell(propagation_object, True, False, flip_flop)

                            if def_file:
                                propagation_object.calculate_orientations()
                                key = ''.join(map(str, combination))
                                if is_flip_flop:
                                    key = key + "_" + str(flip_flop)
                                multiple_exporting_dict[gds_cell_name][key] = copy.deepcopy(propagation_object)

                            if unit_test:
                                multiple_exporting_dict[gds_cell_name].append(copy.deepcopy(propagation_object))

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
                    #traceback.print_exc()
                    error_cell_list.append(gds_cell_name)

    end_time_log = time.time()
    gds_drawing.write_output_log(start_time, end_time_log, filtered_cells=cell_name_list, state_counter=state_counter,
                                 error_cell_list=error_cell_list)

    if unit_test:
        gds_drawing.unit_test(multiple_exporting_dict, unit_test)

    if def_file:
        gds_drawing.benchmark(multiple_exporting_dict, def_extract, benchmark_plot, vpi_extraction=vpi_extraction)
        end_time = time.time()
        gds_drawing.benchmark_export_data(def_extract, end_time - start_time, def_file)


if __name__ == "__main__":
    debug = False
    if debug:
        #run_auto_ops("Platforms/IHP-Open-PDK130nm/sg13g2_stdcell.gds", "Platforms/IHP-Open-PDK130nm/sg13g2_stdcell_typ_1p20V_25C.lib", "", "", [], [[1, 0], [31, 0], [5, 0], [6, 0], [8, 0], [8, 25]], ['sg13g2_nand2_1'], "unit_test", True)
        run_auto_ops("input/stdcells.gds", "input/stdcells.lib", "", "/Users/paul/IdeaProjects/CMOS-INV-GUI/benchmarks/EPFL/Hyp/Par/top.def", [], [[1, 0], [5, 0], [9, 0], [[10, 0]], [[11, 0]], [[11, 0]]], [], "", True, False, None)
    else:
        run_cli()
