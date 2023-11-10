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
    program = 2
    if program == 1:
        app = QApplication(sys.argv)
        app.setApplicationName("CMOS-INV-GUI")
        app.setWindowIcon(QIcon('resources/app_logo.png'))
        controller = MainController()
        view = controller.get_view()
        view.show()
        sys.exit(app.exec())

    elif program == 2:

        lib_file = "Platforms/PDK45nm/NangateOpenCellLibrary_typical.lib"
        gds_file = "Platforms/GDS-II/TRJ.gds"
        open_cell_lib = "Platforms/PDK45nm/stdcells.gds"
        def_file = "Platforms/GDS-II/Trojan1_ALU_prime.def"

        def_extract = get_gates_info_from_def_file(def_file)
        cells_list = def_extract[1]


        lib_reader = LibReader(lib_file)

        lib_std = gdspy.GdsLibrary()
        std_cells_list = lib_std.read_gds(open_cell_lib).cells

        hand_input = hand_input_user = None
        cell_name_hand = None

        # Ask the user for hand_input
        while hand_input_user not in ['y', 'n', 'yes', 'no', '']:
            hand_input_user = input("Do you want to input a hand value? (y/n): ").lower()
            if hand_input_user in ['y', 'yes', '']:
                hand_input = True
            elif hand_input_user in ['n', 'no']:
                hand_input = False
            else:
                print("Please enter 'y' or 'n'.")

        # Ask the user for cell_name_hand
        cell_name_hand = input("Enter the cell name (press enter to perform all): ")
        #cell_name_hand = "XOR3_X1"

        start_time = time.time()

        error_cell_list = []
        counter = 0
        combinations_counter = 0
        state_counter = 0
        time_counter_op = 0
        time_counter_ex = 0

        blue_color = "\033[1;34m"
        reset_color = "\033[0m"
        orange_color = "\033[1;33m"
        white_color = "\033[1;37m"
        green_color = "\033[1;32m"
        red_color = "\033[1;31m"

        total_iterations = len(cells_list)

        multiple_exporting_dict = {}

        for cell_name, gds_cell in std_cells_list.items():

            if len(cell_name_hand) > 0:
                if not cell_name.lower() == cell_name_hand.lower():
                    continue

            if len(cells_list) > 0:
                if cell_name not in cells_list.keys():
                    continue

            combinations = []
            counter += 1

            multiple_exporting_dict[cell_name] = []

            # start progress bar
            progress = counter / total_iterations
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f'\n\r{reset_color}Progress: {green_color}[{bar}] {int(progress * 100)}% Complete {reset_color} -- {cell_name}{white_color} || {blue_color}', end='', flush=True)
            # end progress bar

            try:
                start_ex_time = time.time()

                truth_table, voltage, input_names = lib_reader.extract_truth_table(cell_name)
                draw_inputs = {}

                end_ex_time = time.time()
                execution_ex_time = end_ex_time - start_ex_time
                time_counter_ex += execution_ex_time

                def perform_op(time_counter_op):

                    start_op_time = time.time()

                    op_object = Op(cell_name, gds_cell, [1, 5, 9, 10, 11], truth_table, voltage, draw_inputs)


                    # Add here the different exports from the gds drawing lib

                    #gds_drawing.export_reflection_to_png_over_gds_cell(op_object, True, False)
                    #gds_drawing.export_reflection_to_png(op_object)

                    end_op_time = time.time()
                    execution_time_op = end_op_time - start_op_time
                    time_counter_op += execution_time_op

                    return op_object, time_counter_op


                if hand_input:
                    print("\n\n")
                    for inp in input_names:
                        value = None
                        while value not in ['0', '1']:
                            value = input(f"{reset_color}Enter a value for {inp} {blue_color}(0 or 1){reset_color}: ")
                            if value not in ['0', '1']:
                                print(f"{orange_color}Invalid input. Please enter 0 or 1.{reset_color}")

                        draw_inputs[inp] = int(value)
                    print(f"\n{blue_color}")
                    op_object, time_counter_op = perform_op(time_counter_op)

                else:
                    combinations = list(itertools.product([0, 1], repeat=len(input_names)))

                    for combination in combinations:
                        for index, inp in enumerate(input_names):
                            draw_inputs[inp] = combination[index]

                        op_object, time_counter_op = perform_op(time_counter_op)

                        multiple_exporting_dict[cell_name].append(copy.deepcopy(op_object))

                        combinations_counter += 1
                        state_counter += 1

                if combinations_counter == len(combinations):
                    gds_drawing.data_export_csv(cell_name, execution_ex_time, time_counter_op, op_object, hand_input)
                    time_counter_op = 0
                    combinations_counter = 0
                    time_counter_ex = 0

            except Exception as e:
                print(f"{red_color}An error occurred: {e}{reset_color}")
                error_cell_list.append(cell_name)

        end_time = time.time()
        print(f'\n{green_color}Processing complete.{reset_color}')
        gds_drawing.write_output_log(start_time, end_time,filtered_cells=cells_list, state_counter=state_counter, error_cell_list=error_cell_list)

        gds_drawing.benchmark(multiple_exporting_dict, def_extract)


    elif program == 3:
        lib_file = "Platforms/PDK45nm/NangateOpenCellLibrary_typical.lib"
        open_cell_lib = "Platforms/PDK45nm/stdcells.gds"

        lib_reader = LibReader(lib_file)

        lib_std = gdspy.GdsLibrary()
        std_cells_list = lib_std.read_gds(open_cell_lib).cells

        cell_name = "INV_X1"

        gds_cell = std_cells_list[cell_name]

        op_object = Op(cell_name, gds_cell, [1, 5, 9, 10, 11], {'ZN': [({'A': True}, {'ZN': False}), ({'A': False}, {'ZN': True})]}, [{'name': 'VDD', 'type': 'primary_power'}, {'name': 'VSS', 'type': 'primary_ground'}], {'A': 1})
        gds_drawing.test_orientation(op_object)


