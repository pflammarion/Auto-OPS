import itertools
import sys
import time

import gdspy
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from controllers.gds_drawing import GdsDrawing
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
        cells = ['AND2_X1',
                 'AND2_X2',
                 'AND2_X4',
                 'AND3_X1',
                 'AND3_X2',
                 'AND3_X4',
                 'AND4_X1',
                 'AND4_X2',
                 'AND4_X4',
                 'ANTENNA_X1',
                 'AOI211_X1',
                 'AOI211_X2',
                 'AOI211_X4',
                 'AOI21_X1',
                 'AOI21_X2',
                 'AOI21_X4',
                 'AOI221_X1',
                 'AOI221_X2',
                 'AOI221_X4',
                 'AOI222_X1',
                 'AOI222_X2',
                 'AOI222_X4',
                 'AOI22_X1',
                 'AOI22_X2',
                 'AOI22_X4',
                 'BUF_X1',
                 'BUF_X16',
                 'BUF_X2',
                 'BUF_X32',
                 'BUF_X4',
                 'BUF_X8',
                 'CLKBUF_X1',
                 'CLKBUF_X2',
                 'CLKBUF_X3',
                 'CLKGATETST_X1',
                 'CLKGATETST_X2',
                 'CLKGATETST_X4',
                 'CLKGATETST_X8',
                 'CLKGATE_X1',
                 'CLKGATE_X2',
                 'CLKGATE_X4',
                 'CLKGATE_X8',
                 'DFFRS_X1',
                 'DFFRS_X2',
                 'DFFR_X1',
                 'DFFR_X2',
                 'DFFS_X1',
                 'DFFS_X2',
                 'DFF_X1',
                 'DFF_X2',
                 'DLH_X1',
                 'DLH_X2',
                 'DLL_X1',
                 'DLL_X2',
                 'FA_X1',
                 'FILLCELL_X1',
                 'FILLCELL_X16',
                 'FILLCELL_X2',
                 'FILLCELL_X32',
                 'FILLCELL_X4',
                 'FILLCELL_X8',
                 'HA_X1',
                 'INV_X1',
                 'INV_X16',
                 'INV_X2',
                 'INV_X32',
                 'INV_X4',
                 'INV_X8',
                 'LOGIC0_X1',
                 'LOGIC1_X1',
                 'MUX2_X1',
                 'MUX2_X2',
                 'NAND2_X1',
                 'NAND2_X2',
                 'NAND2_X4',
                 'NAND3_X1',
                 'NAND3_X2',
                 'NAND3_X4',
                 'NAND4_X1',
                 'NAND4_X2',
                 'NAND4_X4',
                 'NOR2_X1',
                 'NOR2_X2',
                 'NOR2_X4',
                 'NOR3_X1',
                 'NOR3_X2',
                 'NOR3_X4',
                 'NOR4_X1',
                 'NOR4_X2',
                 'NOR4_X4',
                 'OAI211_X1',
                 'OAI211_X2',
                 'OAI211_X4',
                 'OAI21_X1',
                 'OAI21_X2',
                 'OAI21_X4',
                 'OAI221_X1',
                 'OAI221_X2',
                 'OAI221_X4',
                 'OAI222_X1',
                 'OAI222_X2',
                 'OAI222_X4',
                 'OAI22_X1',
                 'OAI22_X2',
                 'OAI22_X4',
                 'OAI33_X1',
                 'OR2_X1',
                 'OR2_X2',
                 'OR2_X4',
                 'OR3_X1',
                 'OR3_X2',
                 'OR3_X4',
                 'OR4_X1',
                 'OR4_X2',
                 'OR4_X4',
                 'SDFFRS_X1',
                 'SDFFRS_X2',
                 'SDFFR_X1',
                 'SDFFR_X2',
                 'SDFFS_X1',
                 'SDFFS_X2',
                 'SDFF_X1',
                 'SDFF_X2',
                 'TBUF_X1',
                 'TBUF_X16',
                 'TBUF_X2',
                 'TBUF_X4',
                 'TBUF_X8',
                 'TINV_X1',
                 'TLAT_X1',
                 'WELLTAP_X1',
                 'XNOR2_X1',
                 'XNOR2_X2',
                 'XOR2_X1',
                 'XOR2_X2']

        cell_to_fix = ['ANTENNA_X1', 'CLKGATETST_X1', 'CLKGATETST_X2', 'CLKGATETST_X4', 'CLKGATETST_X8', 'CLKGATE_X1', 'CLKGATE_X2', 'CLKGATE_X4', 'CLKGATE_X8', 'DFFRS_X2', 'DFFR_X2', 'DFFS_X2', 'SDFFRS_X1', 'SDFFR_X1', 'SDFFR_X2', 'SDFF_X2', 'WELLTAP_X1']

        prefix = 'NAND2_X2'

        filtered_cells = [cell for cell in cells if cell.startswith(prefix)]
        #filtered_cells = [prefix]
        is_debug = True
        error_cell_list = []
        start_time = time.time()
        counter = 0

        for cell_name in filtered_cells:
            print("\n" + cell_name)
            try:
                lib = gdspy.GdsLibrary()
                gds_cell = lib.read_gds("Platforms/PDK45nm/stdcells.gds").cells[cell_name]

                lib_reader = LibReader(cell_name, "Platforms/PDK45nm/NangateOpenCellLibrary_typical.lib")
                truth_table, voltage, input_names = lib_reader.extract_truth_table()
                draw_inputs = {}

                # Generate all combinations of 0 and 1 for input values
                if is_debug:
                    combinations = list(itertools.product([0, 1], repeat=len(input_names)))

                    for combination in combinations:
                        for index, inp in enumerate(input_names):
                            draw_inputs[inp] = combination[index]

                        GdsDrawing(gds_cell, cell_name, [1, 5, 9, 10, 11], [0, 0], truth_table, voltage, draw_inputs)
                        counter += 1
                else:
                    for inp in input_names:
                        value = input(f"Enter a value for {inp}: ")
                        draw_inputs[inp] = int(value)

                    GdsDrawing(gds_cell, cell_name, [1, 5, 9, 10, 11], [0, 0], truth_table, voltage, draw_inputs)

            except Exception as e:
                print("\n")
                print("-----------------------------------------------------------")
                print(f"An error occurred for gate {cell_name}: {e}. Please try again.")
                print("-----------------------------------------------------------")
                print("\n")
                error_cell_list.append(cell_name)

        with open('output.log', 'a') as f:
            end_time = time.time()
            f.write(time.strftime("%d/%m/%Y %Hh%M") + "\n\n")
            if len(error_cell_list) > 0:
                f.write("An error occurred for those cells\n")
                f.write(str(error_cell_list) + "\n")

            execution_time = round(end_time - start_time, 2)
            number_of_gate = len(filtered_cells) - len(error_cell_list)
            time_per_sate = round(execution_time/counter, 4)

            f.write(f"Execution time: {execution_time} seconds\n")
            f.write(f"Number of gates: {number_of_gate} \n")
            f.write(f"Number of state calculated : {counter}\n")
            f.write(f"Time per state : {time_per_sate} seconds\n\n")
            f.write("-----------------------------------------------------------\n\n")


    if program == 5:
        #cell_name = "OR3_X4"
        cell_name = "FA_X1"
        lib = gdspy.GdsLibrary()
        gds_cell = lib.read_gds("Platforms/PDK45nm/stdcells.gds").cells[cell_name]

        start_time = time.time()

        #GdsDrawing(gds_cell, cell_name, [1, 9, 10, 11], [0, 0], {'ZN': [({'A1': True, 'A2': True, 'A3': True}, {'ZN': True}), ({'A1': True, 'A2': True, 'A3': False}, {'ZN': True}), ({'A1': True, 'A2': False, 'A3': True}, {'ZN': True}), ({'A1': True, 'A2': False, 'A3': False}, {'ZN': True}), ({'A1': False, 'A2': True, 'A3': True}, {'ZN': True}), ({'A1': False, 'A2': True, 'A3': False}, {'ZN': True}), ({'A1': False, 'A2': False, 'A3': True}, {'ZN': True}), ({'A1': False, 'A2': False, 'A3': False}, {'ZN': False})]}, [{'name': 'VDD', 'type': 'primary_power'}, {'name': 'VSS', 'type': 'primary_ground'}], {'A1': 1, 'A2': 0, 'A3': 1})
        GdsDrawing(gds_cell, cell_name, [1, 5, 9, 10, 11], [0, 0], {'CO': [({'A': True, 'B': True, 'CI': True}, {'CO': True}), ({'A': True, 'B': True, 'CI': False}, {'CO': True}), ({'A': True, 'B': False, 'CI': True}, {'CO': True}), ({'A': True, 'B': False, 'CI': False}, {'CO': False}), ({'A': False, 'B': True, 'CI': True}, {'CO': True}), ({'A': False, 'B': True, 'CI': False}, {'CO': False}), ({'A': False, 'B': False, 'CI': True}, {'CO': False}), ({'A': False, 'B': False, 'CI': False}, {'CO': False})], 'S': [({'A': True, 'B': True, 'CI': True}, {'S': True}), ({'A': True, 'B': True, 'CI': False}, {'S': False}), ({'A': True, 'B': False, 'CI': True}, {'S': False}), ({'A': True, 'B': False, 'CI': False}, {'S': True}), ({'A': False, 'B': True, 'CI': True}, {'S': False}), ({'A': False, 'B': True, 'CI': False}, {'S': True}), ({'A': False, 'B': False, 'CI': True}, {'S': True}), ({'A': False, 'B': False, 'CI': False}, {'S': False})]} ,  [{'name': 'VDD', 'type': 'primary_power'}, {'name': 'VSS', 'type': 'primary_ground'}],  {'A': 0, 'B': 0, 'CI': 0})

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        print(f"Execution time: {execution_time} seconds")






